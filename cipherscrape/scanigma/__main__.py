#!/usr/bin/env python3

"""
CLI application entry point for cipherscrape.

CLI utility used for scraping ciphersuite details.
"""

import argparse
import os
import sys
import json
import re

import requests

from cipherscrape import __version__


def main():
    parser = argparse.ArgumentParser(prog="cipherscrape.scanigma")
    parser.add_argument("--version", action="version", version=f"{__version__}")
    args = parser.parse_args()

    rows = []

    html = requests.get("https://scanigma.com/knowledge-base")
    matches = re.findall('<li><a href="(?P<url>.+)">Detailed info about (?P<iana>\w+) \((?P<hex>.+)\) cipher suite.</a></li>', html.text)

    for match in matches:
        rows.append({
            "Url": match[0],
            "Description": match[1],
            "Value": match[2].replace(' ', '').upper().replace('X', 'x')
        })

    print(json.dumps(rows, indent=4))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("")

