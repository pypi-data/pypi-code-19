from core.api.request import Request
from core.services.onyxerp_service import OnyxErpService


class SimuladorService(Request, OnyxErpService):

    jwt = None

    def __init__(self, base_url):
        super(SimuladorService, self).__init__(base_url)

    def tempo_geral(self):
        response = self.post("/v1/aposentadoria/simulacao/geral/tempo/")

        status = response.get_status_code()

        if status == 200:
            return response.get_decoded()
        else:
            return {
                "status": status,
                "response": response.get_content()
            }
