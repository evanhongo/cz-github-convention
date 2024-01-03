from setuptools import setup

# read the contents of your README file
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="cz_github_convention",
    version="1.0.0",
    py_modules=["cz_github_convention"],
    entry_points={
        "commitizen.plugin": ["cz_github_convention = cz_github_convention:GithubConventionPluginCz"]
    },
    author="evanhongo",
    author_email="evanhongo@gmail.com",
    license="MIT",
    url="https://github.com/evanhongo/cz-github-convention",
    install_requires=["commitizen"],
    description="Extend the commitizen tools to create conventional commits and README that link to GitHub.",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
