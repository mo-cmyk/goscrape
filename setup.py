from setuptools import find_packages, setup


__author__ = "Moritz Steigerwald"
__version__ = "0.1.1"
__license__ = "MIT"

name = 'goscrape'

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name                          = name,
    version                       = __version__,
    author                        = __author__,
    author_email                  = "moritz.steigerwald@studmail.uni-wuerzburg.de",
    description                   = "A universal scraping tool to acquire CS:GO demofiles from professional esports events provided by hltv.org",
    long_description              = long_description,
    long_description_content_type = 'text/markdown',
    project_urls={
        "Issues": "https://github.com/mo-cmyk/goscrape/issues",
        "GitHub": "https://github.com/mo-cmyk/goscrape",
    },
    entry_points={
    'console_scripts': [
        f'{name}=src.main:main',
    ],
},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages                      = find_packages(),
    install_requires=[
          'beautifulsoup4',
          'requests',
          'tqdm',
    ]
)
