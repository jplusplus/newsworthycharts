from setuptools import setup
from version import version, name, authors, email, short_desc


def readme():
    """Import README for use as long_description."""
    with open("README.rst") as f:
        return f.read()


repo = "https://github.com/jplusplus/newsworthycharts"

setup(
    name=name,
    version=version,
    description=short_desc,
    long_description=readme(),
    long_description_content_type='text/x-rst',
    url=repo,
    author=authors,
    author_email=email,
    license="MIT",
    packages=[name],
    zip_safe=False,
    python_requires='~=3.5',
    install_requires=[
        "boto3>=1.6",
        "matplotlib>=2",
        "langcodes>=1.1",
        "Babel>=2.6",
        "PyYAML>=3",
        "adjustText>=0.4",
        "numPy",
        "python-dateutil>=2",
        "pillow>=1.3.3",
    ],
    include_package_data=True,
    download_url="{}/archive/{}.tar.gz".format(repo, version),
)
