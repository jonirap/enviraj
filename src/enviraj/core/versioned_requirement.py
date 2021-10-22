from .requirement import BaseRequirement


class VersionedRequirement(BaseRequirement):
    _IS_BASE = True
    _REQUIRED_CLASS_PARAMS = BaseRequirement._REQUIRED_CLASS_PARAMS + \
        ('VERSION',)
