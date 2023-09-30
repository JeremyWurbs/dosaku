from __future__ import annotations
from typing import Dict, List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from dosaku import Module


class TaskInfo:
    def __init__(
            self,
            name: str,
            api: List[str],
            docs: Optional[Dict[str, str]] = None,
            modules: Union[str, Module, List[str], List[Module]] = None):
        self.name: str = name
        self.api: List[str] = api
        self.docs: Dict[str, str] = docs
        self.modules: Optional[List[str]] = modules

        if modules is not None:
            if isinstance(modules, str):
                self.modules = [modules]
            elif isinstance(modules, Module):
                self.modules = [modules.name]
            elif isinstance(modules, List):
                if isinstance(modules[0], str):
                    self.modules = modules
                elif isinstance(modules[0], Module):
                    self.modules = [module.name for module in modules]

    def register_module(self, module: Union[str, Module]):
        if not isinstance(module, str):  # Must be of type Module
            module = module.name
        if self.modules is None:
            self.modules = list()
        if module not in self.modules:
            self.modules.append(module)

    def __eq__(self, other):
        return self.name == other.name
