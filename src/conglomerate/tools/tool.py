from __future__ import absolute_import, division, print_function, unicode_literals

import cwltool.factory
import docker
import os
import pkg_resources
import yaml

from conglomerate.core.config import DEFAULT_JOB_OUTPUT_DIR, TMP_DIR, PULL_DOCKER_IMAGES, \
    USE_TEST_DOCKER_IMAGES
from conglomerate.core.constants import TEST_TOOL_SUFFIX
from conglomerate.core.types import PathStr, PathStrList
from conglomerate.core.util import ensureDirExists
from conglomerate.tools.jobparamsdict import JobParamsDict
from numbers import Number

__metaclass__ = type


class Tool(object):
    _cwlToolFactory = cwltool.factory.Factory()

    def __init__(self, toolName):
        self._toolName = toolName

        if USE_TEST_DOCKER_IMAGES:
            oldToolName = self._toolName
            self._toolName += TEST_TOOL_SUFFIX
            if not os.path.exists(self._getCWLFilePath()):
                self._toolName = oldToolName

        with open(self._getCWLFilePath(), 'r') as stream:
            self._yaml = yaml.load(stream)
        self._cwlTool = None

    def getCwlTool(self, jobOutputDir=DEFAULT_JOB_OUTPUT_DIR):
        if not self._cwlTool:
            if PULL_DOCKER_IMAGES:
                docker.from_env().images.pull('conglomerate/%s' % self._toolName, tag="latest")
            self._cwlTool = self._cwlToolFactory.make(self._getCWLFilePath())
            self._cwlTool.factory.execkwargs['use_container'] = True
            self._cwlTool.factory.execkwargs['no_read_only'] = True

            tmpDir = os.path.abspath(TMP_DIR)
            jobOutputDir = os.path.abspath(jobOutputDir)

            ensureDirExists(tmpDir)
            ensureDirExists(jobOutputDir)

            self._cwlTool.factory.execkwargs['tmpdir_prefix'] = tmpDir + '/'
            self._cwlTool.factory.execkwargs['tmp_outdir_prefix'] = jobOutputDir + '/'

        return self._cwlTool

    def _getDockerImagePullInfo(self):
        requirements = self._yaml['requirements']
        dockerRequirement = [r for r in requirements if r['class'] == 'DockerRequirement'][0]
        return dockerRequirement['dockerPull']

    def _getToolPath(self):
        return pkg_resources.resource_filename('conglomerate',
                                               '../cwl/{}'.format(self._toolName))

    def _getCWLFilePath(self):
        return pkg_resources.resource_filename('conglomerate',
                                               '../cwl/{}/tool.cwl'.format(self._toolName))

    def createJobParamsDict(self):
        inputs = self._yaml['inputs']
        paramDefDict = dict(
            [(inp, dict(type=self.getPythonType(inputs[inp]['type']),
                        mandatory=self.isMandatoryParameter(inputs[inp]['type'])))
             for inp in inputs])
        return JobParamsDict(paramDefDict)

    @staticmethod
    def getPythonType(cwlType):
        if isinstance(cwlType, dict) or isinstance(cwlType, list):
            return PathStrList
        typeStr = cwlType[:-1] if cwlType.endswith('?') else cwlType
        return {
            'int': int,
            'float': float,
            'long': Number,
            'string': str,
            'boolean': bool,
            'File': PathStr
        }[typeStr]

    @staticmethod
    def isMandatoryParameter(cwlType):
        if isinstance(cwlType, list):
            return 'null' not in cwlType
        else:
            return True if isinstance(cwlType, dict) else not cwlType.endswith('?')