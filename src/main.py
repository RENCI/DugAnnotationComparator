import argparse
import json
import os
from dataclasses import dataclass


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

    ## make report

    all_reports = []
    for e in sorted_elements_diff:
        element = e[1]
        r = get_report_item(dirs[0], dirs[1], element)
        all_reports.append(r)


    report_doc = []
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

    pass


def get_element_files(dirs):
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
    res_files = []

    for root, dirs, files in os.walk(dirpath):
        for file in files:
            res_files.append(os.path.join(root, file))

    return res_files


@dataclass
class DugConcept(object):
    id: str
    name: str
    description: str
    source_dir: str


@dataclass
class DugElement(object):
    id: str
    name: str
    description: str
    concepts: list[DugConcept]
    source_dir: str


@dataclass
class DirFiles(object):
    directory: str
    files: list[str]

@dataclass
class Diff(object):
    id: str
    exists_in: set[str]
    absent_in: set[str]
    child_diff: dict

    def __init__(self, id: str):
        self.id = id
        self.exists_in = set()
        self.absent_in = set()
        self.child_diff = {}

@dataclass
class Report:
    id: str
    action: str
    children: list


def process_element_files(df: DirFiles) -> list[DugElement]:
    res = []
    for path in df.files:
        with open(path, "r") as f:
            data = json.loads(f.read())
            for d in data:
                element = DugElement(id=d['id'],
                                     name=d['name'],
                                     description=d['description'],
                                     concepts=[],
                                     source_dir=df.directory)
                res.append(element)
                for c in d['concepts']:
                    concept = d['concepts'][c]
                    if 'id' in concept:
                        element.concepts.append(DugConcept(id=concept['id'],
                                                           name=concept['name'],
                                                           description=concept['description'],
                                                           source_dir=df.directory))
                    else:
                        print("----No concept------")
                        print(path)
                        print(d["id"])

    return res


def get_diff(all_elements: list, all_places: list, process_concepts: bool) -> {}:
    diff: dict[str, Diff] = {}
    for e in all_elements:
        if e.id not in diff:
            diff[e.id] = Diff(id=e.id)
            diff[e.id].absent_in = set(all_places)

        diff[e.id].exists_in.add(e.source_dir)
        diff[e.id].absent_in.remove(e.source_dir)

        if process_concepts:
            for c in e.concepts:
                if c.id not in diff[e.id].child_diff:
                    diff[e.id].child_diff[c.id] = Diff(id=c.id)
                    diff[e.id].child_diff[c.id].absent_in = set(all_places)

                diff[e.id].child_diff[c.id].absent_in.remove(c.source_dir)
                diff[e.id].child_diff[c.id].exists_in.add(c.source_dir)


    return diff


def get_report_item(path1: str, path2: str, element) -> Report:
    r = Report(element.id, "none", [])

    if path1 in element.absent_in and path2 in element.exists_in:
        r.action = "added"
    elif path2 in element.absent_in and path1 in element.exists_in:
        r.action = "deleted"

    if len(element.child_diff) > 0:
        for child in element.child_diff:
            child_r = get_report_item(path1, path2, element.child_diff[child])
            r.children.append(child_r)

    return r

if __name__ == '__main__':
    main()
