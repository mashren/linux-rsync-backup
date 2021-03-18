from typing import List


class ProtectedFolder():
    source: str
    destination: str

    exclusions: List[str] = []

    def __init__(self, source: str, destination: str, exclusions: List[str] = None) -> None:
        self.source = source
        self.destination = destination
        if exclusions:
            self.exclusions = exclusions
