from __future__ import absolute_import, division, print_function, unicode_literals

import os
from tempfile import mkstemp

from conglomerate.core.config import TMP_DIR

__metaclass__ = type


TMP_FILENAME_STORAGE = []


def getTemporaryFileName(suffix='.bed'):
    tmpFileName = mkstemp(suffix=suffix, dir=TMP_DIR)[1]
    TMP_FILENAME_STORAGE.append(tmpFileName)
    return tmpFileName


def deleteAllTmpFiles():
    while TMP_FILENAME_STORAGE:
        os.unlink(TMP_FILENAME_STORAGE.pop())


def ensureDirExists(dirPath):
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)
