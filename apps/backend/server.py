"""Example setting up a given FastAPIAgent """
from dosaku.agents import Dosaku
from dosaku.backend.server import Server


def app():
    server = Server(agent=Dosaku())  # Set agent to any FastAPIAgent object
    return server.app()
