from admin.common import Common


class EventReporter(Common):

    def __init__(self):
        super().__init__()

    def start(self):
        super().start()
        super().get_signing_info()
        super().get_zone_id()
        try:
            print("\n\nProvide report filter criteria...")
            start_date = self.take_input("  Enter start date (optional=Y, default=1st day of current month) [YYYY-MM-DD [hh:mm:ss]]: ", False, "")
            end_date = self.take_input("  Enter end date (optional=Y, default=last day of current month) [YYYY-MM-DD [hh:mm:ss]]: ", False, "")
            remote_conn_ids = self.take_input("  Enter enterprise ids (optional=Y, default=all): ", False, "")
            conn_ids = self.take_input("  Enter connection ids (optional=Y, default=depends): ", False, "")
            event_types = self.take_input("  Enter event types (optional=Y, default=all) [1=con-sms-sent, 2=agent-created, 3=auth-req-sent]: ", False, "")
            executor_codes = self.take_input("  Executor codes (optional=Y, default=all) [A=Agency, R=Enterprise]: ", False, "")

            print("\nProvide report display criteria...")
            detailed = self.take_input("  Need detailed report (optional=Y, default=N) [Y/N]: ", False, "N")
            download = self.take_input("  Want to download as csv file (optional=Y, default=N) [Y/N]: ", False, "N")
            slice_by_type = self.take_input("  Slice by type (optional=Y, default=2) [1=years, 2=months, 3=days]: ", False, "2")
            slice_size = self.take_input("  Slice size (optional=Y, default=1): ", False, "1")
            zone_id = self.get_config("last_tz")

            challenge_dict = {
                "zoneId": zone_id,
                "startDate": start_date,
                "endDate": end_date,
                "remoteIds": remote_conn_ids,
                "ids": conn_ids,
                "types": event_types,
                "executorCodes": executor_codes,
                "detail": detailed,
                "download": download,
                "sliceByType": slice_by_type,
                "sliceSize": slice_size
            }

            filtered_challenge_dict = dict(
                (k, v) for k, v in challenge_dict.items() if v != "")

            url_path = "agent/id/{did}/event?challenge={challenge}&signature={signature}"
            response = self.execute_request(filtered_challenge_dict, url_path, "Y", "GET")
            self.process_response(response, download)
        except Exception as e:
            print("\nError occurred: {}\n".format(repr(e)))
        except KeyboardInterrupt:
            print("\n\nExited\n")
