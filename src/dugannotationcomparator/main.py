import argparse
import json
import os
from itertools import groupby

from annotationdiff import DirFiles, process_element_files, get_diff, get_report_item
from nodenormalization import get_normalized_concept_ids


def main():
    parser = argparse.ArgumentParser(description='Util that compares output annotator files')
    parser.add_argument('-l', '--list', nargs='*', help='<Required> List of directories', required=True)
    parser.add_argument('-d', '--destination', help='<Required> Path for the output', required=True)

    args = parser.parse_args()

    dirs = args.list
    destination = args.destination

    compare(destination, dirs)


def compare(destination, dirs):
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
            "label": c.label
        }

    for e in all_reports:
        element = id_to_element[e.id]

        concepts_grouped_by_action = groupby(e.children, lambda c: c.action)
        concepts_grouped_by_action_dict = {"none": [], "added": [], "deleted": []}
        for k, g in concepts_grouped_by_action:
            concepts_grouped_by_action_dict[k] = list(g)
        deleted_concepts = []

        for d in concepts_grouped_by_action_dict["deleted"]:
            concept_exists_in = list(d.diff.exists_in)[0]
            el_in_existing = source_to_elementdict_by_id[concept_exists_in][e.id]
            deleted_concepts.append(el_in_existing.get_concept_by_id(d.id))

        el = {
            "id": element.id,
            "description": element.description,
            "same_concepts": [get_concept_for_report(element.get_concept_by_id(r.id)) for r in
                              concepts_grouped_by_action_dict["none"]],
            "new_concepts": [get_concept_for_report(element.get_concept_by_id(r.id)) for r in
                             concepts_grouped_by_action_dict["added"]],
            "deleted_concepts": [get_concept_for_report(d) for d in deleted_concepts]
        }
        report_doc.append(el)
    result_txt = json.dumps(report_doc)
    with open(destination, 'w') as output:
        output.write(result_txt)


def get_element_files(dirs) -> list[DirFiles]:
    """Selects all elements.txt files grouped by directory (DirFile)"""
    dir_n_files = []
    for directory in dirs:
        files = get_all_files(directory)
        dir_n_files.append(DirFiles(directory, files))
    element_files_to_cmp = []
    for df in dir_n_files:
        elements = list(filter(lambda f: str.endswith(f, "elements.txt"), df.files))
        element_files_to_cmp.append(DirFiles(df.directory, elements))
    return element_files_to_cmp


def get_all_files(dirpath) -> list[str]:
    """Visits all directories and collects all files"""
    res_files = []

    for root, dirs, files in os.walk(dirpath):
        for file in files:
            res_files.append(os.path.join(root, file))

    return res_files


if __name__ == '__main__':
    main()
