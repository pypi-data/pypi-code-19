# -*- coding: utf-8 -*-
import abc

from oe_daemonutils.dossierservice.commands.actoren import RetrieveEmailsActorenCommand
from oe_daemonutils.dossierservice.commands.data import RetrieveDataCommand, RetrieveMasterdataCommand, \
    MasterdataNotFoundException, SaveDataCommand
from oe_daemonutils.dossierservice.commands.location import DetermineRegionRepsCommand, DetermineNiscodesCommand
from oe_daemonutils.dossierservice.utils import text_
from oe_geoutils import AdminGrenzenClient


class DossierService(object):
    def __init__(self, settings, logger, system_token, failure_threshold=5, timeout_default=60, max_timeout=300,
                 invocation_timeout=60):
        """
        Service which can be used for processing a feed entry to a dossier

        :param settings: daemon settings
        :param logger: logger object
        :param system_token: token for authentication in rest requests
        :param failure_threshold: the couples of times the daemon should failure before opening the circuit
        :param timeout_default: default sleep time while circuit is open
        :param max_timeout: max sleep time while circuit is open
        :param invocation_timeout: max time span an operation should take, before timing out
        """
        self.settings = settings
        self.logger = logger
        self.system_token = system_token
        self.admin_grenzen_client = AdminGrenzenClient(base_url=settings.get('daemon.administratievegrenzen.url'))
        self.regioverantwn_url = settings.get('daemon.regioverantwoordelijken.url')
        self.headers = {'OpenAmSSOID': self.system_token, 'Accept': 'application/json',
                        'Content-Type': 'application/json'}
        self.failure_threshold = failure_threshold
        self.timeout_default = timeout_default
        self.max_timeout = max_timeout
        self.invocation_timeout = invocation_timeout
        self.determine_region_reps_command = DetermineRegionRepsCommand(
            regioverantwoordelijken_url=self.regioverantwn_url,
            logger=self.logger,
            system_token=self.system_token
        )
        self.retrieve_emails_actoren_command = RetrieveEmailsActorenCommand(
            logger=self.logger,
            system_token=self.system_token
        )
        self.determine_niscodes_command = DetermineNiscodesCommand(
            logger=self.logger,
            admin_grenzen_client=self.admin_grenzen_client
        )
        self.retrieve_data_command = RetrieveDataCommand(
            logger=self.logger,
            system_token=self.system_token
        )
        self.retrieve_masterdata_command = RetrieveMasterdataCommand(
            logger=self.logger,
            system_token=self.system_token
        )
        self.save_data_command = SaveDataCommand(
            logger=self.logger,
            system_token=self.system_token
        )

    @abc.abstractmethod
    def create_dossier(self, entry, notifications_dict):
        """
        abstract method for creating a dossier

        :param entry: atom feed entry
        :param notifications_dict: dict with actors who must be notified about the created dossiers
        """
        pass
