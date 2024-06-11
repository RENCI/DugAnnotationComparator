import os

from avalon.mainoperations import get_files
from avalon.operations.LakeFsWrapper import LakeFsWrapper
from lakefs_sdk import Configuration

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


def get_files_from_lakefs(lfs, local_path: str, repo_name: str, remote_path: str, branch: str) -> None:

    check_dir_create_if_not_exists(local_path)

    try:
        get_files(local_path=local_path,
                lake_fs_client=lfs,
                remote_path=remote_path,
                repo=repo_name,
                branch=branch,
                changes_only=False)
    except Exception as e:
        raise Exception("Error getting files from lakefs: {}".format(e))

def get_lfs(acompstask):
    c = Configuration(host=acompstask.LakeFSHost,
                      password=acompstask.LakeFSPassword,
                      username=acompstask.LakeFSUsername)
    c.temp_folder_path = acompstask.LocalTempPath
    lfs = LakeFsWrapper(configuration=c)
    return lfs


def check_dir_create_if_not_exists(dirpath: str) -> None:
    if os.path.isdir(dirpath):
        return
    else:
        os.mkdir(dirpath)