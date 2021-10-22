from abc import ABCMeta
from typing import Iterable

_UNSET = object()


class RequirementMetaclass(ABCMeta):
    def __new__(mcs, name: str, bases: Iterable, dct: dict):
        cls = super().__new__(mcs, name, bases, dct)
        is_base_type = dct.get('_IS_BASE', False)
        if is_base_type:
            return cls
        params = []
        for param in cls._REQUIRED_CLASS_PARAMS:
            p = dict(original=param,
                     name=getattr(cls, f"{param}_NAME", _UNSET),
                     type=getattr(cls, f"{param}_TYPE", _UNSET),
                     default=getattr(cls, f"{param}_DEFAULT", _UNSET))
            assert p['name'] is not _UNSET, f"Must set {param}_NAME"
            assert p['type'] is not _UNSET, f"Must set {param}_TYPE"
            p['arg_string'] = f"{p['name']}: {p['original']}_TYPE" + \
                (f"={p['original']}_DEFAULT" if p['default'] is not _UNSET else "")
            params.append(p)
        assert len(params) == len(
            {p['name'] for p in params}), "You have parameters with the same name!"
        eval_context = {f"{p['original']}_DEFAULT": p['default'] for p in params
                        if p['default'] is not _UNSET}
        eval_context.update({f"{p['original']}_TYPE": p['type'] for p in params})
        params.sort(key=lambda p: p['default'] is not _UNSET)
        inner_init = '\n    '.join(
            f"self.{p['name']} = {p['name']}" for p in params)
        eval(compile(f"""
def __init__(self, {', '.join(p['arg_string'] for p in params)}):
    {inner_init}
                     """,
                     f"auto-generated-{name}-__init__.py", "exec"), eval_context)
        cls.__init__ = eval_context['__init__']
        return cls


class BaseRequirement(metaclass=RequirementMetaclass):
    _IS_BASE = True
    _REQUIRED_CLASS_PARAMS = ('ID', 'DEPENDENCIES')
    DEPENDENCIES_NAME = "dependencies"
    DEPENDENCIES_DEFAULT = ()


BaseRequirement.DEPENDENCIES_TYPE = Iterable[BaseRequirement]
