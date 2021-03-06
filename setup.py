# Auto-generated by easyPyPI: https://github.com/PFython/easypypi
# Preserve current formatting to ensure easyPyPI compatibility.

from pathlib import Path
from setuptools import find_packages
from setuptools import setup

NAME = "stargazer"
GITHUB_USERNAME = "Pfython"
VERSION = "0.21"
DESCRIPTION = "Utility to crape emails and names of Github users ('Stargazers') who have starred a particular repository.  Includes a general purpose Repository class and (Github) User class."
LICENSE = "MIT License"
AUTHOR = "Peter Fison"
EMAIL = "peter@southwestlondon.tv"
URL = "https://github.com/Pfython/stargazer"
KEYWORDS = "stargazer, Github, stars, scraper, email, selenium"
CLASSIFIERS = ""
REQUIREMENTS = "cleverutils"


def comma_split(text: str):
    """
    Returns a list of strings after splitting original string by commas
    Applied to KEYWORDS, CLASSIFIERS, and REQUIREMENTS
    """
    if type(text) == list:
        return [x.strip() for x in text]
    return [x.strip() for x in text.split(",")]


if __name__ == "__main__":
    setup(
        name=NAME,
        packages=find_packages(),
        version=VERSION,
        license=LICENSE,
        description=DESCRIPTION,
        long_description=(Path(__file__).parent / "README.md").read_text(),
        long_description_content_type="text/markdown",
        author=AUTHOR,
        author_email=EMAIL,
        url=URL,
        download_url=f"{URL}/archive/{VERSION}.tar.gz",
        keywords=comma_split(KEYWORDS),
        install_requires=comma_split(REQUIREMENTS),
        classifiers=comma_split(CLASSIFIERS),
    )
