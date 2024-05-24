import argparse
import json
import os

from AnnotationDiff import DirFiles, process_element_files, get_diff, get_report_item
from NodeNormalization import get_normalized_concept_ids


def main():
    parser = argparse.ArgumentParser(description='Util that compares output annotator files')
    parser.add_argument('-l', '--list', nargs='*', help='<Required> List of directories', required=True)
    parser.add_argument('-d', '--destination', help='<Required> Path for the output', required=True)

    args = parser.parse_args()

    dirs = args.list
    element_files_to_cmp = get_element_files(dirs)

    all_elements = []
    id_to_desc = {}

    for files in element_files_to_cmp:
        fs = process_element_files(files)
        all_elements.extend(fs)
        for element in fs:
            id_to_desc[element.id] = element.description


    elements_diff = get_diff(all_elements, dirs, True)

    sorted_elements_diff = sorted(elements_diff.items(), key=lambda x: x[1].id)
    ### get normalized ids
    all_concept_ids =set([c.id
                       for e in all_elements
                       for c in e.concepts])

    norm_result = get_normalized_concept_ids(all_concept_ids)

    #set norm_id and label for concepts
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

    ## make report

    all_reports = []
    for e in sorted_elements_diff:
        element = e[1]
        r = get_report_item(dirs[0], dirs[1], element)
        all_reports.append(r)


    report_doc = []

    get_concept_dict = lambda c: {
        "id": c.id,
        "norm_id": c.norm_id,
        "label": c.label
    }

    for e in all_reports:
        el = {
            "id": e.id,
            "description": id_to_desc[e.id],
            "concepts": list([c.id for c in filter(lambda f: "none" == f.action, e.children)]),
            "new_concepts": list([c.id for c in filter(lambda f: "added" == f.action, e.children)]),
            "deleted_concepts": list([c.id for c in filter(lambda f: "deleted" == f.action, e.children)]),
        }
        report_doc.append(el)

    result_txt = json.dumps(report_doc)

    with open(args.destination, 'a') as output:
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