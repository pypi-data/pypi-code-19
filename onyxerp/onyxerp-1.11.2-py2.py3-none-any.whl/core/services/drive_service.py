from onyxerp.core.api.request import Request
from onyxerp.core.services.onyxerp_service import OnyxErpService


class DriveService(Request, OnyxErpService):

    jwt = None

    def __init__(self, base_url):
        super(DriveService, self).__init__(base_url)

    def upload_files(self, ref_cod, app_mod_cod):
        response = self.post("/v1/{0}/modulo/{1}/".format(ref_cod, app_mod_cod))

        status = response.get_status_code()

        if status == 200:
            return True
        else:
            return {
                "status": status,
                "response": response.get_content()
            }
