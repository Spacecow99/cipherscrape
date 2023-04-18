#!/usr/bin/env python3

"""
CLI application entry point for cipherscrape.

CLI utility used for scraping ciphersuite details.
"""

import argparse
import os
import sys

from cipherscrape import __version__


def main():
    parser = argparse.ArgumentParser(prog="cipherscrape")
    parser.add_argument("--version", action="version", version=f"{__version__}")
    args = parser.parse_args()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("")

