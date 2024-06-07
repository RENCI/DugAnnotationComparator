import os

from dugannotationcomparator.annotationdiff import DirFiles


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

def get_files_from_lakefs():
    raise NotImplemented("not implemented yet")