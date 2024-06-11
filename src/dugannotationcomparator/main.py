import argparse
import json
from itertools import groupby

from annotationdiff import process_element_files, get_diff, get_report_item
from dugannotationcomparator.acomptask import ACompTask, read_task_from_file
from fileoperations import get_element_files, get_files_from_lakefs, get_lfs
from nodenormalization import get_normalized_concept_ids


def main():
    parser = argparse.ArgumentParser(description='Util that compares output annotator files')
    parser.add_argument('-l', '--list', nargs='*', help='<Optional> List of directories', required=False)
    parser.add_argument('-d', '--destination', help='<Optional> Path for the output', required=False)
    parser.add_argument('-e', '--empty', help='<Optional> Include variants with no concepts', required=False, default=False)
    parser.add_argument('-t', '--task',  help='<Optional> Task file path', required=False)

    args = parser.parse_args()

    dirs = None

    if args.task:
        task = read_task_from_file(args.task)
        lfs = get_lfs(task)
        get_files_from_lakefs(lfs, local_path=task.LocalPath_1,
                              repo_name=task.LakeFSRepository,
                              remote_path=task.RemotePath_1,
                              branch=task.Branch_1)
        get_files_from_lakefs(lfs, local_path=task.LocalPath_2,
                              repo_name=task.LakeFSRepository,
                              remote_path=task.RemotePath_2,
                              branch=task.Branch_2)
        destination = task.OutputPath
        dirs = [task.LocalPath_1, task.LocalPath_2]
    else:
        destination = args.destination
        dirs = args.list

    include_empty = args.empty
    compare(destination, dirs, include_empty)


def compare(destination, dirs, include_empty):
    element_files_to_cmp = get_element_files(dirs)
    all_elements = []
    id_to_element = {}
    source_to_elementdict_by_id = {}
    for files in element_files_to_cmp:
        fs = process_element_files(files)
        all_elements.extend(fs)
        for element in fs:
            id_to_element[element.id] = element

            if element.source_dir not in source_to_elementdict_by_id:
                source_to_elementdict_by_id[element.source_dir] = {}

            source_to_elementdict_by_id[element.source_dir][element.id] = element

    ### get normalized ids
    all_concept_ids = set([c.id
                           for e in all_elements
                           for c in e.concepts])
    norm_result = get_normalized_concept_ids(all_concept_ids)

    # set norm_id and label for concepts
    for e in all_elements:
        for c in e.concepts:
            if (c.id in norm_result
                    and type(norm_result[c.id]) is dict
                    and "id" in norm_result[c.id]
                    and "identifier" in norm_result[c.id]["id"]
                    and "label" in norm_result[c.id]["id"]):
                c.norm_id = norm_result[c.id]["id"]["identifier"]
                c.label = norm_result[c.id]["id"]["label"]
            else:
                print(f"Not enough normalized info for concept {c.id}")
    elements_diff = get_diff(all_elements, dirs, True)
    sorted_elements_diff = sorted(elements_diff.items(), key=lambda x: x[1].id)

    ## make report
    all_reports = []
    for e in sorted_elements_diff:
        element = e[1]
        r = get_report_item(dirs[0], dirs[1], element)
        all_reports.append(r)
    report_doc = []

    def get_concept_for_report(c):
        return {
            "id": c.id,
            "norm_id": c.norm_id,
            "label": c.label,
            "description": c.description
        }

    for e in all_reports:
        element = id_to_element[e.id]

        concepts_grouped_by_action = groupby(e.children, lambda c: c.action)
        concepts_grouped_by_action_dict = {"none": [], "added": [], "deleted": []}
        for k, g in concepts_grouped_by_action:
            concepts_grouped_by_action_dict[k] = list(g)
        deleted_concepts_list = []

        for d in concepts_grouped_by_action_dict["deleted"]:
            concept_exists_in = list(d.diff.exists_in)[0]
            el_in_existing = source_to_elementdict_by_id[concept_exists_in][e.id]
            deleted_concepts_list.append(el_in_existing.get_concept_by_id(d.id))

        same_concepts = list([get_concept_for_report(element.get_concept_by_id(r.id)) for r in concepts_grouped_by_action_dict["none"]])
        new_concepts = list([get_concept_for_report(element.get_concept_by_id(r.id)) for r in concepts_grouped_by_action_dict["added"]])
        deleted_concepts = list([get_concept_for_report(d) for d in deleted_concepts_list])

        el = {
            "id": element.id,
            "description": element.description,
            "same_concepts": same_concepts,
            "new_concepts": new_concepts,
            "deleted_concepts": deleted_concepts
        }

        if not include_empty and len(same_concepts) == 0 and len(new_concepts) == 0 and len(deleted_concepts) == 0:
            continue

        report_doc.append(el)

    result_txt = json.dumps(report_doc)
    with open(destination, 'w') as output:
        output.write(result_txt)


if __name__ == '__main__':
    main()
