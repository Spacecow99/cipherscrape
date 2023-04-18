#!/usr/bin/env python3

"""
CLI application entry point for cipherscrape.

CLI utility used for scraping ciphersuite details.
"""

import argparse
import os
import sys
import csv
import copy
import json

import requests

from cipherscrape import __version__


def main():
    parser = argparse.ArgumentParser(prog="cipherscrape.iana")
    parser.add_argument("--version", action="version", version=f"{__version__}")
    args = parser.parse_args()

    rows = []

    try:
        r = requests.get("https://www.iana.org/assignments/tls-parameters/tls-parameters-4.csv")
    except requests.Error as e:
        sys.stderr.write(f"{str(e)}\n")
        sys.exit(127)


    #with open('tls-parameters-4.csv', 'r') as f:
    f = r.text.split('\n')
    csv_reader = csv.DictReader(f)
    #rows = []
    for line in csv_reader:
        #print(line)
        #if '-' in line["Value"]:
        first, second = line["Value"].split(',')
        # If dash in first byte, generate all permutations
        if '-' in first:
            start, stop = first.split('-')
            start = int(start, base=16)
            stop = int(stop, base=16)
            if start > stop:
                print("Error, order doesn't compute")
            for value in range(start, stop+1):
                for i in range(0x00, 0xff+1):
                    new_line = copy.copy(line)
                    new_line["Value"] = f"{hex(value).upper().replace('X', 'x')},{hex(i).upper().replace('X', 'x')}"

                    rows.append(new_line)
        elif '-' in second:
            start, stop = second.split('-')
            start = int(start, base=16)
            stop = int(stop, base=16)
            for value in range(start, stop+1):
                new_line = copy.copy(line)
                new_line["Value"] = f"{first},{hex(value).upper().replace('X', 'x')}"
                rows.append(new_line)
        else:
            rows.append(line)


    print(json.dumps(rows, indent=4))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("")

