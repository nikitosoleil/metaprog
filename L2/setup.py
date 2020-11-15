from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="pythonccf",
    packages=["pythonccf"],
    entry_points={
        "console_scripts": ['pythonccf = pythonccf.pythonccf:main']
    },
    version='0.1.1',
    description="A simple tool for renaming and documenting Python code according to PEP",
    long_description=long_description,
    author="Mykyta Oliinyk",
    author_email="nikiolei@gmail.com",
    url="https://github.com/nikitosoleil/metaprog/tree/lab/2-python/L2",
)
