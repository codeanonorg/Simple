"""
 Copyright (c) 2021 aq
 
 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
"""

import os
import logging
from bs4 import BeautifulSoup, ResultSet


def simplifier(html_file: str):
    # Get paths from included files 
    included_components = []
    with open(html_file, 'r') as fp:
        parsed_soup = BeautifulSoup(fp, 'html.parser')
    extracted_include_components = parsed_soup.find_all('include')
    for element in extracted_include_components:
        included_components.append(element.attrs['src'])
        element.extract()

    # load included files
    included_components_body = {}
    for file in included_components:
        with open("examples/" + file, 'r') as fp:
            included_components_body[file] = BeautifulSoup(fp, 'html.parser')

    # Get position and include into main tree
    for component in included_components_body:
        included_components_body[component].find('def').replaceWithChildren()
        # TODO: Remove prefix in a more clean way
        parsed_soup.find(
            component.removeprefix('./').removesuffix('.html').lower()
        ).replaceWith(included_components_body[component])

    # Write file to public
    public_path = 'public/'
    if not os.path.exists(public_path):
        os.makedirs(public_path)
    with open(public_path + str(html_file).split('/')[-1], 'w') as fp:
        fp.writelines(parsed_soup.prettify())
