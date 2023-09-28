from __future__ import annotations
from typing import Callable, Dict, TYPE_CHECKING
from warnings import warn

if TYPE_CHECKING:
    from dosaku import Module


class ModuleManager:
    def __init__(self):
        self._modules: Dict[str: Module] = {}
        self._builders = {}

    @property
    def modules(self):
        return list(self._modules.keys())

    def register_builder(self, module: str, builder: Callable):
        self._builders[module] = builder

    def _create(self, module: str, **kwargs):
        builder = self._builders.get(module)
        if not builder:
            raise ValueError(f'There is no record of a Module {module}. Unable to create one.')
        return builder(**kwargs)

    def load_module(self, module: str, force_reload=False, **kwargs):
        if module not in self._modules or force_reload:
            try:
                module_instance = self._create(module, **kwargs)
            except Exception as err:
                raise RuntimeError(f'Unable to load module {module}. Could not instantiate module.\n\n{err}')
            self._modules[module] = module_instance

        else:
            warn(f'Module {module} is already loaded and will not be loaded again.')

    def get_module_attr(self, module: str, attr: str) -> Callable:
        return getattr(self._modules[module], attr)


module_manager = ModuleManager()
