class BackupDestinationNFSParams():
    host: str = ""
    directory: str = None

    def __init__(self, host: str, directory: str) -> None:
        self.host = host
        self.directory = directory