from setuptools import setup
from newsworthycharts import __version__ as version


def readme():
    """Import README for use as long_description."""
    with open("README.rst") as f:
        return f.read()


repo = "https://github.com/jplusplus/newsworthycharts"

setup(
    name="newsworthycharts",
    version=version,
    description="Matplotlib wrapper to create charts and publish them on Amazon S3",
    long_description=readme(),
    long_description_content_type='text/x-rst',
    url=repo,
    author="Jens Finnäs and Leo Wallentin, J++ Stockholm",
    author_email="stockholm@jplusplus.org",
    license="MIT",
    packages=["newsworthycharts"],
    zip_safe=False,
    python_requires='>=3.5',
    install_requires=[
        "boto3>=1.6",
        "matplotlib==3.6.3",
        "langcodes>=3.3",
        "Babel>=2.11",
        "PyYAML>=3",
        "adjustText==0.7.3",
        "numpy>=1.19.1,<2",
        "python-dateutil>=2",
        "Pillow>=8",
        "requests>=2.22",
        "matplotlib-label-lines==0.5.1",
        "geopandas==0.12.2",
        "mapclassify==2.5.0",
    ],
    include_package_data=True,
    download_url="{}/archive/{}.tar.gz".format(repo, version),
)
