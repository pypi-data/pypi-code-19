from .deployments import Deployments
from .spots import Spots
from .executions import Executions
from .profiles import Profiles

Deployments.register_class()
Spots.register_class()
Executions.register_class()
Profiles.register_class()
