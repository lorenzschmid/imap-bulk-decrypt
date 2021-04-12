from setuptools import setup


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="imap-bulk-decrypt",
    version="0.1.0",
    description="Bulk-decrypt GPG encrypted messages via IMAP",
    long_description=readme(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/lorenzschmid/imap-bulk-decrypt",
    author="Lorenz Schmid",
    author_email="lorenzschmid@users.noreply.github.com",
    license="MIT",
    packages=["imapbulkdecrypt"],
    package_dir={"imapbulkdecrypt": "lib"},
    scripts=["bin/imap-bulk-decrypt"],
    install_requires=[
        "python-gnupg",
    ],
)
