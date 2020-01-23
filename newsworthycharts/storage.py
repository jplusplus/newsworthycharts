""" Storage classes. A Storage saves a byte stream representing an
image to e.g. a file or a database blob.
"""

from shutil import copyfileobj
import boto3
import os
from .lib.mimetypes import MIME_TYPES
from io import BytesIO, StringIO


class AmazonUploadError(Exception):
    """ Error uploading to Amazon S3 """
    pass


class Storage(object):
    """ Base class for storages. A storage is responsible for saving a
    image byte stream to a file, database blob or similar.

    A Storage subclass must implement a save() method.
    """
    def __init__(self):
        pass

    def save(self, key, stream, filetype):
        """
        :param key (str): A key for the save object
        :param stream (BytesIO): A stream containing the file data
        :param filetype (str): A filetype. See MIME_TYPES for valid values
        """
        raise NotImplementedError("The save class must be overwritten.")

    def __repr__(self):
        # Use type(self).__name__ to get the right class name for sub classes
        return "<{cls}: {name}>".format(cls=type(self).__name__,
                                        name=str(id(self)))


class DictStorage(Storage):
    """ Saves images as bytestring references in a dictionary.
        Mostly useful for testing.
    """
    def __init__(self, dict):
        """
        :param dict (dict): A dictionary that will be filled with
                            filename: bytestring
        """
        self.dict = dict

    def save(self, key, stream, filetype):
        """
        :param key (str): Disregarded.
        :param stream (BytesIO): A stream containing the file data
        :param filetype (str): File extension, used as dict key
        """
        stream.seek(0)
        self.dict[filetype] = stream


class LocalStorage(Storage):
    """ Save images as a file on the local file system.
    """
    def __init__(self, path="."):
        """
        :param path (str): Path to local folder where files are saved.
        """
        self.path = path

    def save(self, key, stream, filetype):
        """
        :param key (str): Used for creating filename. Files may be overwritten.
        :param stream (BytesIO|str): A stream containing the file data or a
            string.
        :param filetype (str): File extension
        """
        filename = os.path.join(self.path, key + "." + filetype)

        if isinstance(stream, BytesIO):
            stream.seek(0)

            with open(filename, "wb") as f:
                copyfileobj(stream, f, length=131072)

        elif isinstance(stream, str):
            with open(filename, "w") as f:
                f.write(stream)

        else:
            raise NotImplementedError(f"Unable to save {stream}")


class S3Storage(Storage):
    """ Save images to an S3 bucket.
    """
    def __init__(self, bucket, prefix=None):
        """
        :param bucket (str): An S3 bucket name.
        :param prefix (str): Optionally a S3 prefix (path)
        """
        s3_client = boto3.resource('s3')
        self.bucket = s3_client.Bucket(bucket)
        self.prefix = prefix

    def save(self, key, stream, filetype):
        """
        :param key (str): Used for creating filename. Files may be oberwritten.
        :param stream (BytesIO): A stream containing the file data
        :param filetype (str): File extension
        """
        stream.seek(0)
        if self.prefix is not None:
            filename = "/".join(x.strip("/")
                                for x in [self.prefix, key]) + "." + filetype
        else:
            filename = key + "." + filetype
        mime_type = MIME_TYPES[filetype]
        try:
            self.bucket.put_object(Key=filename, Body=stream,
                                   ACL='public-read', ContentType=mime_type)
        except Exception as e:
            raise AmazonUploadError(e)
