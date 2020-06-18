import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="DockerENT",
    version="0.0.1",
    author="Rohit Sehgal",
    author_email="rohitsehgal1994@gmail.com",
    description="A tool to analyse issues with running docker container(s)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LazyOffSec/DockerENT",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)