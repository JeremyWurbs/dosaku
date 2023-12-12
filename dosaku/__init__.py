"""Dosaku namespace."""
from dosaku.core.exceptions import (ActionDoesNotExist,
                                    CodingError,
                                    ExecutorPermissionRequired,
                                    InterpreterError,
                                    ModuleForTaskNotFound,
                                    NameAttributeNotFound,
                                    OptionNotSupported,
                                    ServicePermissionRequired,
                                    UnsupportedActionType)
from dosaku.config.config import Config
from dosaku.core.actor import Actor
from dosaku.core.dosaku_base import DosakuBase
from dosaku.core.module_info import ModuleInfo
from dosaku.core.module_manager import ModuleManager
from dosaku.core.task import Task
from dosaku.core.module import Module
from dosaku.core.service import Service
from dosaku.core.executor import Executor
from dosaku.core.agent import Agent
from dosaku.backend.server import Server
from dosaku.backend.backend_agent import BackendAgent
from dosaku.discord.discord_bot import DiscordBot
from .dosaku_setup import initial_dosaku_setup

initial_dosaku_setup()
