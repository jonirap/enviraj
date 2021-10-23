from .requirement import BaseRequirement
from .provider import BaseProvider, State
from typing import Iterable, Set, Optional, Dict, Type


class RequirementResolverEngine:
    def get_requirement_stages(self, requirements: Iterable[BaseRequirement]) -> Iterable[Set[BaseRequirement]]:
        yet_to_be_installed_requirements = self._merge_all_requirements(
            self._get_all_requirements(requirements))
        installed_requirements = set()
        while yet_to_be_installed_requirements:
            current_stage = set(self._get_next_requirements(yet_to_be_installed_requirements,
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
    def _merge_all_requirements(cls, requirements: Iterable[BaseRequirement]) -> Set[BaseRequirement]:
        merged_requirements = {}
        for req in requirements:
            if req in merged_requirements:
                other = merged_requirements.pop(req)
                if isinstance(req, MergeableRequirement):
                    req = req.merge(other)
                else:
                    raise ValueError(
                        f"Both {req} and {other} specified but can't be merged")
            merged_requirements[req] = req
        return set(merged_requirements)

    @classmethod
    def _get_next_requirements(cls, yet_to_be_installed_requirements: Iterable[BaseRequirements],
                               installed_requirements: Iterable[BaseRequirement] = None) -> Iterable[BaseRequirement]:
        for r in yet_to_be_installed_requirements:
            if not set(getattr(r, r.DEPENDENCIES_NAME)).difference(installed_requirements or []):
                yield r


class ExtractorEngine:
    def run_extractors(self, extractors: Iterable[BaseExtractor]) -> Iterable[BaseRequirement]:
        for e in extractors:
            yield from e.extract()


class ProviderEngine:
    def __init__(self, providers: Dict[Type[BaseRequirement], BaseProvider]):
        self.providers = providers

    def _get_provider(self, requirement: BaseRequirement) -> Optional[BaseProvider]:
        for cls in requirement.__class__.mro():
            if cls in self.providers:
                return self.providers[cls]

    def install_requirement(self, requirement: BaseRequirement,
                            provider: Optional[BaseProvider] = None) -> Optional[BaseProvider.install]:
        provider = provider or self._get_provider(requirement)
        state = provider.get_state(requirement)
        if State.SHOULD_UNINSTALL & state:
            provider.uninstall(requirement)
        if state:
            return provider.install(requirement)


class Engine:
    def __init__(self, provider_engine: ProviderEngine,
                 requirement_resolver_engine: Optional[RequirementResolverEngine] = None):
        self.provider_engine = provider_engine
        self.requirement_resolver_engine = requirement_resolver_engine

    def install(self, requirements: Iterable[BaseRequirement]) -> Iterable[BaseProvider.install]:
        for stage in self.requirement_resolver_engine.get_requirement_stages(requirements):
            for req in stage:  # TODO: Can be done in parallel
                yield self.provider_engine.install_requirement(req)
