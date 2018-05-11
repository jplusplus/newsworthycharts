from setuptools import setup
from version import version, name, authors, email, short_desc


def readme():
    """Import README for use as long_description."""
    with open("README.rst") as f:
        return f.read()


setup(
    name=name,
    version=version,
    description=short_desc,
    long_description=readme(),
    long_description_content_type='text/x-rst',
    url="https://github.com/jplusplus/newsworthycharts",
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
        "Babel>=2",
        "PyYAML>=3",
    ],
    include_package_data=True,
    download_url="https://github.com/jplusplus/newsworthycharts/archive/%s.tar.gz" % version,
)
