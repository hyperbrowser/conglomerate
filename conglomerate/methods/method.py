from __future__ import absolute_import, division, print_function, unicode_literals

from future.utils import with_metaclass
from abc import ABCMeta, abstractmethod
from conglomerate.methods.interface import UniformInterface
# from conglomerate.methods.typecheck import takes
from conglomerate.tools.exceptions import MissingMandatoryParameters
from conglomerate.tools.job import Job
from conglomerate.tools.tool import Tool

__metaclass__ = type


class Method(UniformInterface):
    def __init__(self):
        self._params = self._getTool().createJobParamsDict()
        self._setDefaultParamValues()
        self._resultFilesDict = None
        self._ranSuccessfully = None

    def _getTool(self):
        return Tool(self._getToolName())

    def setManualParam(self, key, val):
        """
        For setting tool parameters directly, without going through properties (like allowOverlaps)
        """
        self._params[key] = val

    def createJobs(self):
        absentMandatoryParameters = self._params.getAbsentMandatoryParameters()
        if absentMandatoryParameters:
            raise MissingMandatoryParameters(absentMandatoryParameters)
        return [Job(self._getTool(), self._params)]

    def setResultFilesDict(self, resultFilesDict):
        self._resultFilesDict = resultFilesDict
        self._parseResultFiles()

    def getResultFilesDict(self):
        return self._resultFilesDict

    def ranSuccessfully(self):
        #Needs to be set to specific value before this method is called..
        assert hasattr(self, '_ranSuccessfully') and self._ranSuccessfully in [False, True], self._ranSuccessfully
        return self._ranSuccessfully

    def getErrorDetails(self):
        return 'Error message parsing not implemented for this tool'

    def __repr__(self):
        return self.__class__.__name__

class SingleQueryTrackMethodMixin(with_metaclass(ABCMeta, object)):
    def setQueryTrackFileNames(self, trackFnList):
        assert len(trackFnList) == 1
        self._setQueryTrackFileName(trackFnList[0])

    @abstractmethod
    def _setQueryTrackFileName(self, trackFn):
        pass


class SingleReferenceTrackMethodMixin(with_metaclass(ABCMeta, object)):
    def setReferenceTrackFileNames(self, trackFnList):
        assert len(trackFnList) == 1
        self._setReferenceTrackFileName(trackFnList[0])

    @abstractmethod
    def _setReferenceTrackFileName(self, trackFn):
        pass

    def setPredefinedTrackIndexAndCollection(self, trackIndex, trackCollection):
        pass


class MultipleQueryTracksMethodMixin(with_metaclass(ABCMeta, object)):
    def setQueryTrackFileNames(self, trackFnList):
        assert len(trackFnList) > 0
        self._setQueryTrackFileNames(trackFnList)

    @abstractmethod
    def _setQueryTrackFileNames(self, trackFnList):
        pass


class MultipleReferenceTracksMethodMixin(with_metaclass(ABCMeta, object)):
    def setReferenceTrackFileNames(self, trackFnList):
        assert len(trackFnList) > 0
        self._setReferenceTrackFileNames(trackFnList)

    @abstractmethod
    def _setReferenceTrackFileNames(self, trackFnList):
        pass

    def setPredefinedTrackIndexAndCollection(self, trackIndex, trackCollection):
        pass


class CollectionReferenceTracksMethodMixin(with_metaclass(ABCMeta, object)):
    def setReferenceTrackFileNames(self, trackFnList):
        assert len(trackFnList) == 0

    # @takes(str, str)
    def setPredefinedTrackIndexAndCollection(self, trackIndex, trackCollection):
        self._setPredefinedTrackIndexAndCollection(trackIndex, trackCollection)

    @abstractmethod
    def _setPredefinedTrackIndexAndCollection(self, trackIndex, trackCollection):
        pass


class OneVsOneMethod(SingleQueryTrackMethodMixin,
                     SingleReferenceTrackMethodMixin,
                     Method):
    pass


class OneVsManyMethod(SingleQueryTrackMethodMixin,
                      MultipleReferenceTracksMethodMixin,
                      Method):
    pass


class ManyVsManyMethod(MultipleQueryTracksMethodMixin,
                       MultipleReferenceTracksMethodMixin,
                       Method):
    pass


class OneVsCollectionMethod(SingleQueryTrackMethodMixin,
                            CollectionReferenceTracksMethodMixin,
                            Method):
    pass


class ManyVsCollectionsMethod(MultipleQueryTracksMethodMixin,
                              CollectionReferenceTracksMethodMixin,
                              Method):
    pass
