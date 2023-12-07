"""Defines the FastAPI immigration agent app."""
from dosaku.agents import Dosaku
from dosaku.backend.server import Server


def app():
    server = Server(agent=Dosaku())  # agent may be any Agent that implements the BackendAgent protocol
    return server.app()
