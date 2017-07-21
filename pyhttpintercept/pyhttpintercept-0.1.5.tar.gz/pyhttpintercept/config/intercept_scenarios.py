
import logging_helper
from configurationutil import Configuration, cfg_params, CfgItems, CfgItem
from .._metadata import __version__, __authorshort__, __module_name__
from ..resources.templates import intercept_template
from ..resources.schema import intercept_schema
from .constants import ScenarioConstant, INTERCEPT_SCENARIO_CONFIG

logging = logging_helper.setup_logging()

# Register Config details (These are expected to be overwritten by an importing app)
cfg_params.APP_NAME = __module_name__
cfg_params.APP_AUTHOR = __authorshort__
cfg_params.APP_VERSION = __version__

TEMPLATE = intercept_template.scenario
SCHEMA = intercept_schema.scenario


def _register_scenario_config():

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=INTERCEPT_SCENARIO_CONFIG,
                 config_type=cfg_params.CONST.json,
                 template=TEMPLATE,
                 schema=SCHEMA)

    return cfg


class Modifier(CfgItem):

    def __init__(self,
                 **parameters):
        super(Modifier, self).__init__(**parameters)

    def save_changes(self):

        updated_item = self.__dict__.copy()

        # remove any hidden parameters
        for k in [key for key in updated_item.keys()
                  if str(key).startswith(u'_')]:
            del updated_item[k]

        self._cfg[self._cfg_root][self._key_attr] = updated_item


class Scenario(CfgItem):

    def __init__(self,
                 **parameters):
        super(Scenario, self).__init__(**parameters)

        self._load_modifiers()

    def _load_modifiers(self):

        for i, modifier in enumerate(self.modifiers):
            self.modifiers[i] = Modifier(cfg_fn=_register_scenario_config,
                                         cfg_root=u'{k}.{c}'.format(k=self._cfg_root,
                                                                    c=ScenarioConstant.modifiers),
                                         key=i,
                                         **modifier)

    def get_active_modifiers(self):
        return [modifier for modifier in self.modifiers if modifier.active]


class Scenarios(CfgItems):

    def __init__(self):
        super(Scenarios, self).__init__(cfg_fn=_register_scenario_config,
                                        cfg_root=INTERCEPT_SCENARIO_CONFIG,
                                        key=ScenarioConstant.name,
                                        has_active=False,
                                        item_class=Scenario)
