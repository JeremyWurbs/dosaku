from dataclasses import dataclass


@dataclass
class TaskConnection:
    task: str
    action: str
