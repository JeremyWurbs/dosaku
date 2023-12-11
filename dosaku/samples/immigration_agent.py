#!/usr/bin/env python
"""Example creating an Immigration assistant."""
import argparse

from dosaku.modules import GPT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--filenames', nargs='+',
                        default=[
                            'gsc_immigration_guide.pdf',
                            'visa_extension.pdf'
                        ])
    parser.add_argument('--queries', nargs='+',
                        default=[
                            'What do I need for a tourist visa?',
                            'How do I apply for a student visa?',
                            'What is the allowable period of sojourn for a C-4 visa?'  # 90 days
                        ])
    parser.add_argument('--instructions', type=str, nargs='?',
                        default='Use the provided documents to answer user queries.')
    parser.add_argument('--prompt', type=str, nargs='?', default='old person in a red blazer and green scottish kilt',
                        help='Prompt used to edit the masked portrait image.')

    opt = parser.parse_args()
    print(f'Using the following documents:')
    for filename in opt.filenames:
        print(filename)

    with GPT(filenames=opt.filenames, instructions=opt.instructions) as gpt:
        for query in opt.queries:
            response = gpt.message(query)
            print(f'Query: {query}:\n\nResponse: {response.text}\n\n')


if __name__ == "__main__":
    main()
