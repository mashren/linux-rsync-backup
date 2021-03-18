class BackupDestinationDiskUUIDParams():
    uuid: str = ""
    location_prefix: str = "/dev/disk/by-uuid"

    def __init__(self, uuid: str) -> None:
        self.uuid = uuid