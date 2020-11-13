#!/usr/bin/python3

import argparse
import sys
import xml.etree.ElementTree as ET

import requests

OK = 0
WARN = 1
CRIT = 2

DEFAULT_STATUS_XPATH = ".//ProcessStatus/state"
DEFAULT_OK_STRING = "Functional"
DEFAULT_CRIT_STRING = "Non-Functional"

def parse_args():
    parser = argparse.ArgumentParser(description="Check Contrail node status via introspect API")
    parser.add_argument("url", help="URL for introspect API endpoint (e.g. http://localhost:8085/")
    parser.add_argument("-x", "--xpath", default=DEFAULT_STATUS_XPATH)
    parser.add_argument("-p", "--okay-string", default=DEFAULT_OK_STRING)
    parser.add_argument("-c", "--critical-string", default=DEFAULT_CRIT_STRING)
    return parser.parse_args()

def get_http_response_output(url):

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        print('The server couldn\'t fulfill the request.')
        print('URL: ' + url)
        print('Error code: ', response.status_code)
        print('Error text: ', response.text)
        print("CRITICAL")
        sys.exit(CRIT)
    except requests.exceptions.RequestException as e:
        print('Failed to reach destination')
        print('URL: ' + url)
        print('Reason: ', e)
        print("CRITICAL")
        sys.exit(CRIT)
    else:
        output = response.text
        response.close()
    return output

def get_status(xml_text, xpath=DEFAULT_STATUS_XPATH):
    # TODO: be aware of XML parsing vulns as outlined in:
    # https://docs.python.org/3/library/xml.etree.elementtree.html
    tree = ET.fromstring(xml_text)
    r = tree.find(xpath)
    if r is not None:
        return r.text
    else:
        return None

if __name__ == "__main__":
    args = parse_args()
    output = get_http_response_output(args.url)
    status = get_status(output, xpath=args.xpath)
    if status == args.okay_string:
        print("OK")
        sys.exit(OK)
    elif status == args.critical_string:
        print("CRITCAL. status: {}".format(status))
        sys.exit(CRIT)
    else:
        print("WARNING. HTTP payload unknown")
        sys.exit(WARN)
