from dataclasses import dataclass


@dataclass
class ClassificationResults:
    name: str
    silence: list[int]
    applause: list[int]
    speech: list[int]
    length: int
