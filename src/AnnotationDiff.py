import json
from dataclasses import dataclass


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
    """List of files in a directory"""
    directory: str
    files: list[str]


@dataclass
class Diff(object):
    """Contains information about where some item is present"""
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
    """Contains information for an output file.
    It represents an item id and can have an action[None,Added,Deleted]"""
    id: str
    action: str
    children: list # nested Report list


def process_element_files(df: DirFiles) -> list[DugElement]:
    """Parses JSON elements files and returns a list of DugElements"""
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
                        #possible error in an input file
                        print("----No concept------")
                        print(path)
                        print(d["id"])

    return res


def get_diff(all_elements: list, all_places: list, process_concepts: bool) -> dict[str, Diff]:
    """Walks through all elements and concepts and collects info where each item is present and absent.
    :returns dictionary with a key Id of an element and Diff value."""

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


def get_report_item(path1: str, path2: str, element: Diff) -> Report:
    """:argument path1 - path to the folder with annotations
       :argument path2 - path to the folder with annotations, that we compare to
       :argument element - Diff information for an element"""
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
