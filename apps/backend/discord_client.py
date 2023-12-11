import argparse

from dosaku import DiscordBot


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, nargs='?', default='http://localhost:8000/')
    opt = parser.parse_args()

    db = DiscordBot(host=opt.host)
    db.run()


if __name__ == '__main__':
    main()
