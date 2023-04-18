#!/usr/bin/env python3

"""
CLI application entry point for cipherscrape.

CLI utility used for scraping ciphersuite information from gnutls manual and lib/algorithms/ciphersuites.c
and combine in to ciphersuite.info fixtures compatible 03_gnutls_ciphers.yaml.
"""


import argparse
# import os
# import sys
# import json
import re

from bs4 import BeautifulSoup
import requests
import yaml

from cipherscrape import __version__


def main():
    parser = argparse.ArgumentParser(prog="cipherscrape.gnutls")
    parser.add_argument("--version", action="version", version=f"{__version__}")
    args = parser.parse_args()

    ###############################################
    # Parse supported GNUTLS ciphersuites from docs
    ###############################################

    GNUTLS_URL = "https://gnutls.org/manual/html_node/Supported-ciphersuites.html#Supported-ciphersuites"
    #REGEX = "\s*(\S+)\s+(Not\ implemented.?|\S+)\s+(\(\S+\))?"

    doc_rows = []
    r = requests.get(GNUTLS_URL)
    soup = BeautifulSoup(r.text, 'html.parser')
    spans = soup.find_all('span')
    for span in spans:
        if span.attrs != {'id': 'Ciphersuites'}:
            continue
        table = span.next_sibling.next_sibling.next_sibling
        for row in table.find_all("tr"):
            columns = [str(c.contents[0]) for c in row.find_all("td")]
            if columns:
                doc_rows.append({"Value": ",".join(columns[1].split(' ')), "Description": columns[0]})


    #################################################
    # Parse supported GNUTLS ciphersuites from source
    #################################################

    DEFINE_DEFS = "\ *define (?P<Define>GNUTLS.+)\{(?P<Value>.+)\}"
    ENTRY_DEFS = "ENTRY(_PRF|_TLS13)?\((?P<Define>.+),\n?.+\"(?P<Description>.+)\","
    GNUTLS_SRC_URL = "https://raw.githubusercontent.com/gnutls/gnutls/master/lib/algorithms/ciphersuites.c"
    defines = {}
    c_rows = []

    r = requests.get(GNUTLS_SRC_URL)
    define_matches = re.findall(DEFINE_DEFS, r.text)
    for define_match in define_matches:
        define, value = define_match
        define = define.strip(' ')
        define = define.strip('\t')
        value = ",".join(value.rstrip(' ').lstrip(' ').split(', '))
        defines[define] = {"Value": value}

    for entry_matches in re.findall(ENTRY_DEFS, r.text):
        _, define, ciphersuite = entry_matches
        c_rows.append({"Description": ciphersuite, **defines[define]})

    #######################################
    # Combine lists of GNUTLS ciphersuites
    #######################################

    unique_rows = []
    for row in c_rows:
        hexcodes = {}
        for count, value in enumerate(row["Value"].split(','), start=1):
            hexcodes[f"hex_byte_{count}"] = value
        unique_rows.append({
            "model": "directory.GnutlsCipher",
            "pk": row["Description"],
            "fields": hexcodes
        })

    for row in doc_rows:
        if row not in c_rows:
            hexcodes = {}
            for count, value in enumerate(row["Value"].split(','), start=1):
                hexcodes[f"hex_byte_{count}"] = value
            unique_rows.append({
                "model": "directory.GnutlsCipher",
                "pk": row["Description"],
                "fields": hexcodes
            })

    print(yaml.dump(unique_rows, sort_keys=False))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("")

