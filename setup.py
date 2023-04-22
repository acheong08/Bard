from setuptools import find_packages
from setuptools import setup

setup(
    name="GoogleBard",
    version="1.0.0",
    license="MIT License",
    author="Antonio Cheong",
    author_email="acheong@student.dalat.org",
    description="Reverse engineering of Google's Bard chatbot",
    packages=find_packages("src"),
    package_dir={"": "src"},
    url="https://github.com/acheong08/Bard",
    project_urls={"Bug Report": "https://github.com/acheong08/Bard/issues/new"},
    install_requires=["requests", "prompt_toolkit", "rich"],
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    py_modules=["Bard"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
