#!/usr/bin/env python
"""Example creating custom loggers for different Dosaku components."""
import logging
from logging.handlers import RotatingFileHandler

from dosaku.core.context import Context
from dosaku.modules import GPT


def main():
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create a stream handler to pass all logging events to pass to stdout
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)  # DEBUG is the lowest level
    stream_handler.setFormatter(formatter)

    # Create a file handler to log events at the INFO level or higher.
    file_handler = logging.handlers.RotatingFileHandler('logs.txt')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Log GPT events to both file and stdout
    GPT.logger.setLevel(logging.DEBUG)
    GPT.logger.addHandler(stream_handler)
    GPT.logger.addHandler(file_handler)

    # Log Context events only to stream, but only if they are at the INFO level or higher
    Context.logger.setLevel(logging.INFO)
    Context.logger.addHandler(stream_handler)

    with Context(suppress=True) as context:
        gpt = GPT()  # Module initialization logged at the INFO level. I.e. will both log to stdout and log to file.
        response = gpt.message('Tell me an English lit joke.')  # Module methods do not, in general, log any output.
        print(f'response: {response}')

        x = 1 / 0  # Exception will be caught and logged by the context. I.e. will only log to stdout and continue.

    print('This line will still run.')


if __name__ == "__main__":
    main()
