import argparse
import logging
import os

from dosaku import Config
from dosaku.samples.immigration_agent.immigration_agent import ImmigrationAgent
from dosaku.utils import default_logger


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, nargs='?', default='http://localhost:8080/')
    opt = parser.parse_args()

    agent = ImmigrationAgent(host=opt.host)
    agent.logger = default_logger(
        name=agent.name,
        stream_level=logging.DEBUG,
        file_level=logging.INFO,
        file_name=os.path.join(Config()['DIR_PATHS']['LOGS'], 'immigration_agent_discord_bot_logs.txt')
    )
    agent.connect_to_discord()


if __name__ == '__main__':
    main()
