#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    requests_cache.backends.filesystem
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ``filesystem`` cache backend
"""
from .base import BaseCache
from .storage.filesystemdict import FilesystemDict


class FilesystemCache(BaseCache):
    """ ``filesystem`` cache backend.
    """
    def __init__(self, name, **options):
        super(FilesystemCache, self).__init__(**options)

        fs_class = FilesystemDict(
            options.get('cache_dir', name),
            options.get('mode', 0o600),
            options.get('threshold', 110)) # max number of cached files to maintain

        self.responses = fs_class
        self.keys_map = fs_class
