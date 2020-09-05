"""Setup script."""
import DockerENT
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

_version = DockerENT.__version__
_requires = open('requirements.txt').read().splitlines()

setuptools.setup(
    name="DockerENT",
    version=_version,
    description="A tool to analyse issues with running docker container(s)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/r0hi7/DockerENT",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=_requires,
    entry_points={
        'console_scripts': {
            'DockerENT = DockerENT.__main__:start'
        }
    },

    keywords='docker runtime scanning framework'
)
