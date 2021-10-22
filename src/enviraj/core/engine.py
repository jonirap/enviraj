from .requirement import BaseRequirement
from typing import Iterable, Set


class RequirementInstallerEngine:
    def get_requirement_stages(self, requirements: Iterable[BaseRequirement]) -> Iterator[Set[BaseRequirement]]:
        yet_to_be_installed_requirements = set(self._get_all_requirements(requirements))
        installed_requirements = set()
        while yet_to_be_installed_requirements:
            current_stage = set(self._get_next_requirement(yet_to_be_installed_requirements,
                                                           installed_requirements))
            yield current_stage
            installed_requirements.update(current_stage)
            yet_to_be_installed_requirements.difference_update(current_stage)
    
    @classmethod
    def _get_all_requirements(cls, requirements: Iterable[BaseRequirement]) -> Iterable[BaseRequirement]:
        for r in requirements:
            yield from cls._get_all_requirements(getattr(r, r.DEPENDENCIES_NAME) or ())
            yield r
    
    
    @classmethod
    def _get_next_requirements(cls, yet_to_be_installed_requirements: Iterable[BaseRequirements], 
                               installed_requirements: Iterable[BaseRequirement] = None):
        for r in yet_to_be_installed_requirements:
            if not set(getattr(r, r.DEPENDENCIES_NAME)).difference(installed_requirements or []):
                yield r
            