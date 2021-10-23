from abc import ABC, abstractmethod
from typing import Iterable
from .requirement import BaseRequirement


class BaseExtractor(ABC):
    @abstractmethod
    def extract(self) -> Iterable[BaseRequirement]:
        pass
