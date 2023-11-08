import importlib
import inspect
from types import ModuleType
from typing import Literal, Type

from loguru import logger

from ..hook import BaseHook
from ..plugin import BasePlugin
from ..util.config import config


def get_subclasses(module: ModuleType, base_class: Type) -> Type:
    for name, obj in inspect.getmembers(module, lambda o: type(o) is type):
        # class a:
        #   pass
        # Question: Why inspect.isclass(tuple) returns True
        # But issubclass(tuple,a) raised "issubclass() arg 1 must be a class" error
        # Even more puzzling issubclass(tuple,a) is on my computer it returns False. Why?
        if issubclass(obj, base_class) and obj is not base_class:
            return obj


class Package:
    plugin: dict[str, BasePlugin] = {}
    hook: dict[str, BaseHook] = {}

    def init(self):
        self.load_plugins()
        self.load_hooks()

    def __getitem__(self, item):
        # Compatibility with the old version
        return self.__getattribute__(item)

    def __setitem__(self, key, value):
        # Compatibility with the old version
        self.__setattr__(key, value)

    def _load(
            self,
            _dir: Literal["plugin"],
            _type: Type[BasePlugin],
    ):
        base = __package__.split(".")[0] + "." + _dir
        for plugin in getattr(config, _dir, []):
            if plugin.startswith("_"):
                logger.warning(f"Skip loading protected {_dir} {plugin}")
                continue
            try:
                package = f"{base}.{plugin}"
                logger.info(f"Loading {_dir}: {plugin}")
                temp = importlib.import_module(package)
                self[_dir][plugin] = get_subclasses(temp, BasePlugin)
            except ImportError as e:
                logger.trace(e)
                logger.error(f"Failed to import {_dir}: {plugin}")
            except IndexError:
                logger.error(f"Imported {_dir} but no {_type.__name__} found: {plugin}")

    def load_plugins(self):
        self._load("plugin", BasePlugin)

    def load_hooks(self):
        if config["hook"] is None:
            logger.warning(f"All hooks are disabled")
            return
        for plugin in getattr(config, "hook", []):
            try:
                logger.info(f"Loading hook: {plugin}")
                temp = importlib.import_module(f"yamlgenerator_hook_{plugin}")
                self["hook"][plugin] = get_subclasses(temp, BaseHook)
            except ImportError as e:
                logger.trace(e)
                logger.error(f"Failed to import hook: {plugin}")
            except IndexError:
                logger.error(f"Imported hook but no BaseHook found: {plugin}")


pkg = Package()
