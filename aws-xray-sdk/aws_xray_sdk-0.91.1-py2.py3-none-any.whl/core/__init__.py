from .recorder import AWSXRayRecorder
from .patcher import patch_all, patch


xray_recorder = AWSXRayRecorder.instance()

__all__ = [
    'patch',
    'patch_all',
    'xray_recorder',
    'AWSXRayRecorder',
]
