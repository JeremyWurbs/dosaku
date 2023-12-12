from __future__ import annotations
from typing import Callable, Dict, List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from dosaku import Module
from dosaku import DosakuBase
from dosaku import ModuleInfo, ExecutorPermissionRequired, ServicePermissionRequired, ModuleForTaskNotFound


class ModuleManager(DosakuBase):
    """Module Manager Singleton.

    The ModuleManager class is meant to act as a singleton to manage all loaded modules on a single machine, even if
    they are used by multiple agents or other modules. The understanding is that there are likely to be many, possibly
    dozens, of modules which may be simultaneously loaded and called upon at any time, while there may be no more than
    a single GPU available.
    """
    def __init__(self, devices: Optional[Union[str, List[str]]] = None, **kwargs):
        super().__init__(**kwargs)
        if isinstance(devices, str):
            devices = [devices]
        self._devices: Dict[str, List[str]] = {device: [] for device in devices} if devices is not None else {}
        self._devices['cpu'] = []
        self._modules: Dict[str: Module] = {}
        self._modules_info: Dict[str: ModuleInfo] = {}

    @property
    def modules(self) -> List[str]:
        return list(self._modules.keys())

    def module(self, name: str) -> Optional[Module]:
        if name not in self._modules:
            raise RuntimeError(f'Module {name} is not loaded. Load it first.')
        return self._modules.get(name)

    def modules_on_device(self, device: str) -> List[str]:
        """Returns the module names of the modules currently loaded on the given device."""
        return self._devices[device]

    def module_location(self, module: str) -> Optional[str]:
        """Returns the device name where the given module is currently loaded or None, if the module is not loaded."""
        if module not in self.modules:
            return None
        for device, modules in self._devices.items():
            if module in modules:
                return device

    def register_builder(self, module: str, builder: Callable, dependencies: Optional[List[str]] = None):
        if module not in self._modules_info:
            self._modules_info[module] = ModuleInfo(builder=builder, dependencies=dependencies)
        else:
            self._modules_info[module].builder = builder
            if dependencies is not None:
                self._modules_info[module].dependencies = dependencies

    def _create(self, module: str, device: str = 'cpu', force_device: bool = True, **kwargs) -> Module:
        module_info = self._modules_info.get(module)
        if module_info is None:
            raise ValueError(f'A module by the name {module} has not been registered. Unable to create one.')
        if module_info.builder is None:
            raise ValueError(f'A builder for the module {module} has not been registered. Unable to create one.')
        try:
            module_instance = module_info.builder(device=device, **kwargs)
        except Exception as err:
            if 'out of memory' in str(err) and force_device is True:
                # If other modules are currently on this device, remove them all and try to load this module again:
                if len(self._devices[device]) > 0:
                    self.logger.warn(
                        f'Encountered Out of Memory error while attempting to load module {module} on device {device}. '
                        f'Moving all modules on this device to CPU and trying again.')
                    for module_name in self._devices[device]:
                        self.move(module_name, device='cpu')
                    try:
                        module_instance = self._create(module=module, device=device, **kwargs)
                    except Exception as err:
                        if 'out of memory' in str(err):
                            raise RuntimeError(
                                f'Unable to load module {module} onto device {device} even after removing all other '
                                f'modules. It is likely that the device is out of memory. Try loading the module onto '
                                f'a different device with more memory or run on CPU.')
                        else:
                            raise err
                    return module_instance
                raise RuntimeError(
                    f'Unable to load module {module} onto device {device}. It is likely that the device is out of '
                    f'memory. Try loading the module onto a different device.')
            else:
                raise err

        return module_instance

    def load(
            self,
            module: str,
            device: str = 'cpu',
            share_device: bool = True,
            force_device: bool = True,
            force_reload: bool = False,
            allow_services: bool = False,
            allow_executors: bool = False,
            **kwargs):
        """Load the given module onto the desired device.

        Args:
            module: The name of the module to load.
            device: The device to load the module onto, generally of the form 'cuda:0', 'cuda:1', etc. If 'cuda' is
                passed in, the first available cuda device will be used. If 'cpu' is passed in, the module will be
                loaded to the cpu.
            share_device: If True, will try to share the device if other modules are already using it. If false, will
                always move other modules off the device to the cpu before using it. In case both the requested and
                previous modules cannot be loaded onto the device, the module that claims the device will be set
                according to the force_device flag.
            force_device: If True, will prioritize trying to load the requested module onto the requested device, even
                if it forces other modules off the device. If False, previous models on the device will not be moved off
                if sharing fails.
            force_reload: If True, will reload the module even if it is already loaded.
            allow_services: If True, will allow loading of Service modules. If False, will raise an error if the
                module is a Service.
            allow_executors: If True, will allow loading of Executor modules. If False, will raise an error if the
                module is an Executor.
            **kwargs: Any additional kwargs to pass to the module's builder.
        """

        if module not in self._modules or self.module_location(module) != device or force_reload:
            """
            If we are loading the module onto a (gpu) device, we need to do the following before it can be loaded:
                1. Determine a device if a generic (e.g. 'cuda') was passed in, which could refer to any device
                2. Check that this module manager is responsible for managing the given device
                3. If share_device is False, move any current module on the device to the cpu.
            """
            if device != 'cpu':  # if we are loading the module to a gpu
                if device == 'cuda':  # 'cuda' refers to any cuda device; find the first unused cuda device
                    device = self._fetch_unused_cuda_device(force_device=True)
                if device not in self._devices.keys():  # check that we are managing the given device
                    raise RuntimeError(f'{self.name} is not managing device {device}.')
                elif self.num_modules_on_device(device) > 0 and share_device is False:  # remove current modules
                    for module_name in self._devices[device]:
                        self.move(module_name, device='cpu')

            """
            To actually load the module, we need to do the following:
                1. Load the module as requested
                2. Check if this module is a Service or Executor (which cannot be determined before it is loaded). If it 
                    is either, assert that we have been given permission to load it. Raise an error if not.
                3. Check the module dependencies and raise a warning if any are not loaded.
            """
            try:
                module_instance = self._create(module, device=device, force_device=force_device, **kwargs)
            except Exception as err:
                raise RuntimeError(f'Unable to load module {module}. Could not instantiate module.\n\n{err}')
            if module_instance.is_service and allow_services is False:
                raise ServicePermissionRequired(
                    f'Loaded module was a service, but services have not been enabled. Enable services or load a '
                    f'non-service module.')
            if module_instance.is_executor and allow_executors is False:
                raise ExecutorPermissionRequired(
                    f'Loaded module was an executor, but executors have not been enabled. Enable executors or load a '
                    f'non-executor module.')
            self._modules[module] = module_instance

            # Remove association of the module with its current device
            for device_name, modules in self._devices.items():
                if module in modules:
                    modules.remove(module)
                    break

            # Associate the module to the new device
            self._devices[device].append(module)

            dependencies = self._modules_info[module].dependencies
            if dependencies is not None:
                for dependency in dependencies:
                    if dependency not in self._modules:
                        try:
                            self.load(dependency)
                        except Exception as err:
                            self.logger.warn(
                                f'Attempted to load {module} dependency {dependency} but failed with the error printed'
                                f'below. The {module} module has loaded but may not work correctly.\n\n{err}')

        else:
            self.logger.warn(f'Module {module} is already loaded and will not be loaded again.')

        return self._modules[module]

    @property
    def num_gpu_devices(self) -> int:
        return len([device for device in self._devices.keys() if 'cuda' in device])

    def num_modules_on_device(self, device: str) -> int:
        return len(self._devices[device])

    @property
    def unloaded_modules(self) -> List[str]:
        return [module for module in self._modules_info.keys() if module not in self._modules]

    def _least_utilized_device(self) -> Optional[str]:
        """Returns the least utilized device, or None if none are available.

        TODO: Not yet implemented. Currently always returns the first cuda device found, even if it is already in use.
        """
        for device, module in self._devices.items():
            if 'cuda' in device:
                return device
        return None

    def _fetch_unused_cuda_device(self, force_device: bool = False) -> Optional[str]:
        """Returns the first available cuda device, or None if none are available.

        If force_device is True, will return the least utilized cuda device, even if it is already in use.
        """
        for device, module in self._devices.items():
            if module is None:
                return device
        if force_device:
            return self._least_utilized_device()
        return None

    def move(self, module: str, device: str):
        """Move the given module to the given device."""
        if module not in self._modules:
            raise RuntimeError(f'Module {module} is not loaded and cannot be moved.')
        if device == 'cuda':
            device = self._fetch_unused_cuda_device(force_device=True)
            if device is None:
                raise RuntimeError(f'No cuda devices are available to move module {module} to.')
        if device not in self._devices:
            raise RuntimeError(f'Device {device} is not managed by {self.name}.')
        if module in self._devices[device]:
            self.logger.warn(f'Module {module} is already on device {device} and will not be moved.')
            return
        try:
            self._modules[module].to(device)
        except NotImplementedError as err:
            self.logger.warn(f'Unable to move module {module} to device {device}.\n\n{err}')
        except Exception as err:
            raise err

        # Remove the module from being associated with its current device
        for device_name, modules in self._devices.items():
            if module in modules:
                modules.remove(module)
                break

        # Associate the module to the new device
        self._devices[device].append(module)

    def unload(self, module: str):
        """Unload the given module from any device, including the cpu."""
        if module not in self._modules:
            raise RuntimeError(f'Module {module} is not loaded and cannot be removed.')
        for device, modules in self._devices.items():
            if module in modules:
                try:
                    self._modules[module].remove_from_device()
                except NotImplementedError:
                    self.logger.warn(
                        f'Request to remove module {module}, but it does not implement remove_from_device(). The '
                        f'module will be removed manually, but it may not be fully removed or the device cache '
                        f'cleared.')
                finally:
                    del self._modules[module]
                self._devices[device].remove(module)

    def get_module_attr(self, module: str, attr: str) -> Callable:
        return getattr(self._modules[module], attr)

    def summary(self) -> str:
        """Return a summary of the devices and modules managed by this manager."""
        summary = (f'{self.name} is managing {self.num_gpu_devices} GPU devices and {len(self._modules_info)} modules, '
                   f'{len(self._modules)} of which have been loaded and are ready to use.\n')
        for device, modules in self._devices.items():
            if device == 'cpu':
                summary += f'  CPU: {modules}\n'
            else:
                summary += f'  {device}: {modules}\n'
        summary += f'  Unloaded modules: {self.unloaded_modules}'

        return summary


module_manager = ModuleManager()
