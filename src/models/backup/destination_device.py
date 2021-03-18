
from typing import Tuple
from . import BackupDestinationDiskUUIDParams
from . import BackupDestinationNFSParams


class BackupDestinationDevice():
    type: str = ""
    supported_types: Tuple[str] = (
        "nfs",
        "disk_uuid"
    )
    mount_point: str = None
    disk_uuid_params: BackupDestinationDiskUUIDParams = None
    nfs_params: BackupDestinationNFSParams = None

    def __init__(self, type: str, mount_point: str , disk_uuid_params: BackupDestinationDiskUUIDParams = None, nfs_params: BackupDestinationNFSParams = None) -> None:
        if type not in self.supported_types:
            print("Unsupported Backup Destination Device type")
            exit()
        if type == "disk_uuid" and disk_uuid_params == None:
            print("Missing Disk UUID Parameters")
            exit()
        if type == "nfs" and nfs_params == None:
            print("Missing NFS Parameters")
            exit()

        if disk_uuid_params != None and nfs_params != None:
            print("NFS params and Disk UUID params cannot be specified at the same time")
            exit()
        self.disk_uuid_params = disk_uuid_params
        self.nfs_params = nfs_params
        self.mount_point = mount_point
        self.type = type





def parse_destination_device_config(config):
    destination_device: BackupDestinationDevice = None
    device_type = config["type"]

    assert config["mount_point"] != None and config["mount_point"] != ""

    if device_type == "disk_uuid":

        assert config["diskUuid"]["uuid"] != None
        destination_device = BackupDestinationDevice(
            type=device_type, disk_uuid_params=BackupDestinationDiskUUIDParams(uuid=config["diskUuid"]["uuid"]),
            mount_point=config["mount_point"])
    
    elif device_type == "nfs":
        assert config["nfs"]["host"] != None and config["nfs"]["directory"] != None
        destination_device = BackupDestinationDevice(
            type=device_type,
            nfs_params=BackupDestinationNFSParams(
                host=config["nfs"]["host"],
                directory=config["nfs"]["directory"],
                mount_point=config["mount_point"]
            )
        )
    else:
        print("Unsupported backup device type")
        exit()
    
    return destination_device
