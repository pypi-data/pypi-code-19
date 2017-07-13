from admin.common import Common


class AgentConfigUpdater(Common):

    def __init__(self):
        super().__init__()

    def start(self):
        super().start()
        super().get_signing_info()

        try:
            target_id = self.take_input("\n\nEnter target identifier for which you want to update config: ", True)
            key = self.take_input("Enter config key: ", True)

            get_config_dict = {
                "targetId": target_id,
                "key": key
            }

            url_path = "agent/id/{did}/config?challenge={challenge}&signature={signature}"
            response = self.execute_request(get_config_dict, url_path, "N", "GET")
            current_value = ""
            print("Current config value (fetching ...): ", end="")
            if response.status_code == 404:
                current_value = "not yet set"
            else:
                current_value = str(response.content.decode())
            print(current_value)

            new_value = self.take_input("\nEnter new config value: ", True)
            update_config_dict = {
                "targetId": target_id,
                "key": key,
                "value": new_value
            }
            url_path = "agent/id/{did}/config"
            response = self.execute_request(update_config_dict, url_path, "Y", "PUT")

            if response.status_code == 200:
                print("Done\n")
                print("NOTE: On server side, these configs are cached, so new value may take some time (around 5 min or so) to be in effect.")
            else:
                print("Error: {}\n".format(str(response)))

        except Exception as e:
            print("\nError occurred: {}\n".format(repr(e)))
        except KeyboardInterrupt:
            print("\n\nExited\n")
