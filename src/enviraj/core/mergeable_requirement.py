from .requirement import BaseRequirement
from abc import abstractmethod


class MergeableRequirement(BaseRequirement):
    _IS_BASE = True
    
    @abstractmethod
    def merge(self, other: MergeableRequirement) -> BaseRequirement:
        pass
