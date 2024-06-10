import json
from dataclasses import dataclass


@dataclass
class ACompTask:
    LakeFSHost: str
    LakeFSUsername: str
    LakeFSPassword: str
    LakeFSRepository: str
    LocalTempPath: str

    Branch_1: str
    RemotePath_1: str
    LocalPath_1: str

    Branch_2: str
    RemotePath_2: str
    LocalPath_2: str

    OutputPath: str


def read_task_from_file(filepath: str) -> ACompTask:
    with open(filepath) as f:
        try:
            json_obj = json.load(f)
            acomptask = ACompTask(**json_obj)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON: {filepath}")
        except TypeError:
            raise ValueError(f"Invalid JSON: {filepath}")

        return acomptask


