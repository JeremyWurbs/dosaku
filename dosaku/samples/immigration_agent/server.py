"""Defines the FastAPI immigration agent app."""
import logging
import os

from dosaku import Config
from dosaku.agents import Dosaku
from dosaku.backend.server import Server
from dosaku.utils import default_logger


def app():
    server = Server(agent=Dosaku())  # agent may be any Agent that implements the BackendAgent protocol
    server.logger = default_logger(
        name=server.name,
        stream_level=logging.DEBUG,
        file_level=logging.INFO,
        file_name=os.path.join(Config()['DIR_PATHS']['LOGS'], 'immigration_agent_server_logs.txt')
    )
    return server.app()
