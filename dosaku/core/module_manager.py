from __future__ import annotations
from typing import Callable, Dict, List, Optional, TYPE_CHECKING
from warnings import warn

if TYPE_CHECKING:
    from dosaku import Module
from dosaku import ModuleInfo


class ModuleManager:
    def __init__(self):
        self._modules: Dict[str: Module] = {}
        self._modules_info: Dict[str: ModuleInfo] = {}

    @property
    def modules(self):
        return list(self._modules.keys())

    def register_builder(self, module: str, builder: Callable, dependencies: Optional[List[str]] = None):
        if module not in self._modules_info:
            self._modules_info[module] = ModuleInfo(builder=builder, dependencies=dependencies)
        else:
            self._modules_info[module].builder = builder
            if dependencies is not None:
                self._modules_info[module].dependencies = dependencies

    def _create(self, module: str, **kwargs):
        module_info = self._modules_info.get(module)
        if module_info is None:
            raise ValueError(f'A module by the name {module} has not been registered. Unable to create one.')
        if module_info.builder is None:
            raise ValueError(f'A builder for the module {module} has not been registered. Unable to create one.')
        return module_info.builder(**kwargs)

    def load_module(self, module: str, force_reload: bool = False, allow_services: bool = False, **kwargs):
        if module not in self._modules or force_reload:
            try:
                module_instance = self._create(module, **kwargs)
            except Exception as err:
                raise RuntimeError(f'Unable to load module {module}. Could not instantiate module.\n\n{err}')
            if module_instance.is_service and allow_services is False:
                raise RuntimeError(f'Loaded module was a service, but services have not been enabled. Enable services '
                                   f'or load a non-service module.')
            self._modules[module] = module_instance

            dependencies = self._modules_info[module].dependencies
            if dependencies is not None:
                for dependency in dependencies:
                    if dependency not in self._modules:
                        try:
                            self.load_module(dependency)
                        except Exception as err:
                            warn(f'Attempted to load {module} dependency {dependency} but failed with the error printed'
                                 f'below. The {module} module has loaded but may not work correctly.\n\n{err}')

        else:
            warn(f'Module {module} is already loaded and will not be loaded again.')

    def get_module_attr(self, module: str, attr: str) -> Callable:
        return getattr(self._modules[module], attr)


module_manager = ModuleManager()
