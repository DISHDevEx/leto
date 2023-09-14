import shutil
import tempfile
import os
import subprocess

class TemporaryDirectory(object):
    """Context manager for tempfile.mkdtemp() so it's usable with "with" statement."""
    def __enter__(self):
        self.name = tempfile.mkdtemp(dir="")
        return self.name

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self.name)