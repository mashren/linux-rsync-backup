from subprocess import PIPE, run
from typing import List, Tuple

from src.services.notifications import send_discord_notification

from . import BackupDestinationDevice, ProtectedFolder

class BackupClient():

    protected_folders: List[ProtectedFolder] = []
    destination_device: BackupDestinationDevice = None
    accepted_rsync_lines = (
        'Number of files:',
        'Number of created files:',
        'Number of deleted files:',
        'Number of regular files transferred:',
        'Total file size:',
        'Total transferred',
        'Literal data:',
        'Matched data:',
        'File list size:',
        'File list generation time:',
        'File list transfer time:',
        'Total bytes sent:',
        'Total bytes received:'
    )

    discord_notifications_enabled: bool = False
    discord_webhook_url: str = None
    discord_webhook_username: str = None

    def __init__(self, protected_folders: List[ProtectedFolder] = list()) -> None:
        self.protected_folders = protected_folders

    def enable_discord_notifications(self, webhook_url: str, webhook_username: str):
        self.discord_notifications_enabled = True
        self.discord_webhook_url = webhook_url
        self.discord_webhook_username = webhook_username

    def add_protected_folder(self, folder: ProtectedFolder) -> None:
        self.protected_folders.append(folder)

    def set_backup_destination_device(self, device: BackupDestinationDevice):
        self.destination_device = device

    def _device_uuid_path(self) -> str:
        return "/".join([self.destination_device.disk_uuid_params.location_prefix, self.destination_device.disk_uuid_params.uuid])

    def _device_nfs_path(self) -> str:
        return f"{self.destination_device.nfs_params.host}:{self.destination_device.nfs_params.directory}"

    def destination_path(self) -> str:
        if self.destination_device.type == "disk_uuid":
            return self._device_uuid_path()
        elif self.destination_device.type == "nfs":
            return self._device_nfs_path()
        else:
            print("Failed to get destination path")
            exit()

    def _mount_device(self) -> None:
        path: str = None
        mount_point: str = self.destination_device.mount_point
        command: List[str] = []
        if self.destination_device.type == "nfs":
            path = self._device_nfs_path()
            command = ["mount", path,
                       self.destination_device.mount_point, "-t", "nfs"]
        elif self.destination_device.type == "disk_uuid":
            path = self._device_uuid_path()
            command = ["mount", path, self.destination_device.mount_point]
        if path:

            result = run(command,  stdout=PIPE, stderr=PIPE,
                         universal_newlines=True)
            print(result.stderr)
            if result.returncode == 0:
                print(
                    f"Successfully mounted backup drive: {path} on {mount_point}")
            else:
                print(
                    f"Failed to mount backup drive: {path} on {mount_point}")
                exit()
        else:
            exit()

    def _unmount_device(self) -> None:
        c = ["umount", self.destination_device.mount_point]
        result = run(c,  stdout=PIPE, stderr=PIPE, universal_newlines=True)
        if result.returncode == 0:
            print(
                f"Successfully unmounted backup folder: {self.destination_device.mount_point}")
        else:
            print(
                f"Failed to unmount backup folder: {self.destination_device.mount_point}")
            print(f"This might be because it wasn't mounted to begin with")

    def backup(self) -> None:
        self._unmount_device()
        self._mount_device()
        if self.discord_notifications_enabled:
            send_discord_notification(
                self.discord_webhook_url, subject="Backup: Started", username=self.discord_webhook_username)

        for pf in self.protected_folders:
            self.backup_protected_folder(folder=pf)
        self._unmount_device()

        if self.discord_notifications_enabled:
            send_discord_notification(self.discord_webhook_url, subject=f"Backup: Finished",
                                      username=self.discord_webhook_username)

    def rsync_folder(self, source_dir: str, destination_dir: str, exclusions: List[str] = None) -> Tuple[int, str, str]:
        backup_command = ['rsync', '-av', '--delete', source_dir,
                          destination_dir, '--stats', '-h']
        if self.destination_device.type == "nfs":
            backup_command = ['rsync', '-av', '--no-o', '--no-g', '--delete', source_dir,
                              destination_dir, '--stats', '-h']
        if exclusions:
            for x in exclusions:
                backup_command.append(f"--exclude={x}")
        print(" ".join(backup_command))
        result = run(backup_command, stdout=PIPE,
                     stderr=PIPE, universal_newlines=True)
        return result.returncode, result.stdout, result.stderr

    def backup_protected_folder(self, folder: ProtectedFolder):

        # send_discord_notification(discord_webhook_url, subject=f"Folder: {folder.source}",username=discord_webhook_username)
        destination_path = "/".join(
            [self.destination_device.mount_point, folder.destination])
        rc, stdout, stderr = self.rsync_folder(
            source_dir=folder.source, destination_dir=destination_path, exclusions=folder.exclusions)
        backup_status = "Failed"
        message = "Missing message"
        embed_title = "Missing embed title"
        color = "blue"
        if rc == 0 or rc == 23:
            backup_status = "Success"
            color = "green"
            message = "\n".join(
                [l for l in stdout.splitlines() if l.startswith(self.accepted_rsync_lines)])
            embed_title = "RSync Stats"
        else:
            message = stderr
            color = "red"
            embed_title = "RSync Error"
        print(f"Backup {backup_status}")
        if self.discord_notifications_enabled:
            send_discord_notification(self.discord_webhook_url, subject=f"Folder: {folder.source}",
                                        message=message, embed_title=embed_title, username=self.discord_webhook_username, color=color)
