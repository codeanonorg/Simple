"""
 Copyright (c) 2021 aq
 
 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
"""

import os
import logging
import copy
from bs4 import BeautifulSoup, ResultSet


def simplifier(html_file: str):

    logger = logging.getLogger(__name__)

    # Get paths from included files
    included_components = []
    with open(html_file, "r") as fp:
        main_html = BeautifulSoup(fp, "html.parser")
    extracted_include_components = main_html.find_all("include")
    for element in extracted_include_components:
        included_components.append(element.attrs["src"])
        element.extract()

    # load included files
    included_components_body = {}
    for file in included_components:
        component_path = os.path.join("examples", file)
        with open(component_path, "r") as fp:
            logger.info(f"found component @ {component_path}")
            included_components_body[file] = BeautifulSoup(fp, "html.parser")

    # Get position and include into main tree
    for component_path in included_components_body:
        included_components_body[component_path].find("def").replaceWithChildren()
        file_name: str = os.path.basename(component_path)
        component: str = os.path.splitext(file_name)[0].lower()
        placeholders = main_html.find_all(component)
        for placeholder in placeholders:
            placeholder.replaceWith(copy.copy(included_components_body[component_path]))

    # Write file to public
    public_path = "public/"
    if not os.path.exists(public_path):
        os.makedirs(public_path)
    with open(public_path + str(html_file).split("/")[-1], "w") as fp:
        fp.writelines(main_html.prettify())
