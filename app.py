

from discord_webhook import webhook
from src.models.backup import (BackupClient, parse_destination_device_config, BackupDestinationDevice,
                               BackupDestinationDiskUUIDParams,
                               BackupDestinationNFSParams, ProtectedFolder)

import json
import os
config_path = os.path.join(os.path.dirname(__file__), 'config.json')

def main():

    if os.path.exists(config_path) == False:
        print("Could not find the backup config file (config.json)")
        exit()

    bc = BackupClient()
    with open(config_path) as json_file:
        config = json.load(json_file)

        config_notifications = config["notifications"]
        if config_notifications["discordEnabled"] == True:
            assert config_notifications["discordWebhook"] != None
            assert config_notifications["discordUsername"] != None
            bc.enable_discord_notifications(
                webhook_url=config_notifications["discordWebhook"],
                webhook_username=config_notifications["discordUsername"]
            )

        config_destination_device = config["destinationDevice"]
        destination_device = parse_destination_device_config(
            config_destination_device)
        bc.set_backup_destination_device(destination_device)

        config_protected_folders = config["protectedFolders"]
        protected_folders = [ProtectedFolder(
            pf["source"], pf["destination"], pf["exclusions"]) for pf in config_protected_folders]
        for protected_folder in protected_folders:
            bc.add_protected_folder(folder=protected_folder)

        bc.backup()



if __name__ == "__main__":
    main()
