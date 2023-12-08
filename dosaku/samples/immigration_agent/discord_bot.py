import argparse

from dosaku.samples.immigration_agent.immigration_agent import ImmigrationAgent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, nargs='?', default='http://localhost:8080/')
    opt = parser.parse_args()

    agent = ImmigrationAgent(host=opt.host)
    agent.connect_to_discord()


if __name__ == '__main__':
    main()
