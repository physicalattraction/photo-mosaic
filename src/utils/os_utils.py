import os
import shutil


def ensure_empty_dir(dirname: str):
    """
    Ensure that the given directory exists and is empty

    :param dirname: Full path
    """

    if os.path.exists(dirname):
        shutil.rmtree(dirname)
    os.mkdir(dirname)
