import os.path
from django.core.files.storage import FileSystemStorage


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        self.delete(name)
        return name

    def size(self, name):
        if self.exists(name):
            return os.path.getsize(self.path(name))
        else:
            return 0
