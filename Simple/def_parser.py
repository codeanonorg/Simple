"""
 Copyright (c) 2021 aq
 
 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
"""

import logging
from bs4 import BeautifulSoup, ResultSet


def get_all_named_components(name: str, html_file: str) -> ResultSet:
    with open(html_file, 'r') as fp:
        parsed_soup = BeautifulSoup(fp, 'html.parser')
    extracted_components = parsed_soup.find_all(name)
    # DEBUG
    for element in extracted_components:
        print(f"String: {element.string}")
        print(f"element.attrs: {element.attrs}")
        for i in element.attrs.keys():
            print(element.attrs[i])
    return extracted_components