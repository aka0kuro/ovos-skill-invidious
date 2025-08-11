#!/usr/bin/env python3
from os import walk, path
from os.path import dirname, join

from setuptools import setup
import os
import json

URL = "https://github.com/aka0kuro/skill-invidious"
SKILL_CLAZZ = "InvidiousSkill"  # needs to match __init__.py class name
PYPI_NAME = "skill-invidious"  # pip install PYPI_NAME

# below derived from github url to ensure standard skill_id
SKILL_AUTH, SKILL_BRANCH = URL.split(".com/")[-1].split("/")
SKILL_ID = f"{SKILL_AUTH}-{SKILL_BRANCH}-{PYPI_NAME}"
PLUGIN_ENTRY_POINT = f"{SKILL_ID} = {SKILL_CLAZZ}"

# skill_id=package_name:SkillClass

def find_resource_files():
    # add any folder with files your skill uses here! 
    resource_base_dirs = ("locale", "res", "vocab", "dialog", "regex", "skill")
    base_dir = path.dirname(__file__)
    package_data = ["*.json"]
    for res in resource_base_dirs:
        if path.isdir(path.join(base_dir, res)):
            for (directory, _, files) in walk(path.join(base_dir, res)):
                if files:
                    package_data.append(
                        path.join(directory.replace(base_dir, "").lstrip('/'),
                                  '*'))
    return package_data


# Function to parse requirements.txt
def parse_requirements(filename):
    with open(filename, 'r') as f:
        requirements = []
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                requirements.append(line)
        return requirements

# Function to recursively find package files
def package_files(directory):
    paths = []
    for (path, directories, filenames) in walk(directory):
        for filename in filenames:
            paths.append(('..', path, filename))
    return paths

# Function to get version from version.py
def get_version():
    version_dict = {}
    with open("version.py", "r") as f:
        exec(f.read(), version_dict)
    return version_dict.get("VERSION_MAJOR", 0), version_dict.get("VERSION_MINOR", 0), version_dict.get("VERSION_BUILD", 0)

VERSION_MAJOR, VERSION_MINOR, VERSION_BUILD = get_version()
VERSION = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_BUILD}"

setup(
    name=PYPI_NAME,
    version=VERSION,
    url=URL,
    package_dir={PYPI_NAME: ''},
    package_data={PYPI_NAME: ['locale/*', 'res/*']},
    packages=[PYPI_NAME],
    description='ovos common play invidious skill plugin by aka0kuro',
    author='aka0kuro',
    author_email='',
    license='Apache-2.0',
    include_package_data=True,
    install_requires=parse_requirements('requirements.txt'),
    keywords='ovos skill plugin invidious youtube alternative aka0kuro',
    entry_points={
        'ovos.plugin.skill': [
            PLUGIN_ENTRY_POINT
        ]
    }
)
