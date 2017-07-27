from admin.common import Common


class ConfigManager(Common):

    def __init__(self):
        super().__init__()

    def start(self):
        super().start()
        super().get_signing_info()

        def show_current_config_value(target_id, key):
            get_config_dict = {
                "identifier": target_id,
                "key": key
            }

            url_path = "agent/id/{did}/config?challenge={challenge}&signature={signature}"
            response = self.execute_request(get_config_dict, url_path, "N", "GET")
            current_value = ""
            print("\nCurrent config value (fetching ...): ", end="")
            if response.status_code == 204:
                current_value = "not yet set"
            else:
                current_value = str(response.content.decode())
            print(current_value + "\n")

        try:
            target_id = self.take_input("\n\nEnter target identifier for which you want to update config (optional=Y, default=general): ", False, "general")
            key = self.take_input("Enter config key: ", True)
            show_current_config_value(target_id, key)

            new_value = self.take_input("\nEnter new config value: ", True)
            refresh_cache = self.take_input("\nDo you want to update cache immediately (optional=Y, default=Y) [Y/N]: ", False, "Y")
            update_config_dict = {
                "identifier": target_id,
                "key": key,
                "value": new_value,
                "refreshCache": refresh_cache
            }
            url_path = "agent/id/{did}/config"
            response = self.execute_request(update_config_dict, url_path, "Y", "PUT")

            if response.status_code == 200:
                print("Done\n")
                print("NOTE: On server side, these configs are cached, so new value may take some time (around 5 min or so) to be in effect.")
            else:
                print("Error: {}\n".format(str(response)))

            show_current_config_value(target_id, key)

        except Exception as e:
            print("\nError occurred: {}\n".format(repr(e)))
        except KeyboardInterrupt:
            print("\n\nExited\n")
