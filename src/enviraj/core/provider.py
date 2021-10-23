from abc import ABCMeta, abstractmethod
from typing import Iterable, Type
from enum import Flag, auto
from .requirement import BaseRequirement


REQUIREMENT_TO_PROVIDERS = {}


class ProviderMetaclass(ABCMeta):
    def __new__(mcs, name: str, bases: Iterable, dct: dict):
        cls = super().__new__(mcs, name, bases, dct)
        is_base_type = dct.get('_IS_BASE', False)
        if is_base_type:
            return cls
        provides = getattr(cls, 'PROVIDES')
        assert provides, 'The provider must decalare an iterable of requirement types that it can provide!'
        for p in provides:
            REQUIREMENT_TO_PROVIDERS.setdefault(p, []).append(cls)
        return cls


class State(Flag):
    SHOULD_UNINSTALL = auto()
    SHOULD_INSTALL = auto()


class BaseProvider(metaclass=ProviderMetaclass):
    _IS_BASE = True
    PROVIDES: Iterable[Type[BaseRequirement]] = ()

    @abstractmethod
    def install(self, requirement: BaseRequirement):
        pass

    @abstractmethod
    def uninstall(self, requirement: BaseRequirement):
        pass

    @abstractmethod
    def get_state(self, requirement: BaseRequirement) -> Optional[State]:
        pass
