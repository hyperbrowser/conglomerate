from __future__ import absolute_import, division, print_function, unicode_literals

from collections import OrderedDict

from conglomerate.methods.method import OneVsOneMethod
from conglomerate.tools.SingleResultValue import SingleResultValue
from conglomerate.tools.constants import STEREOGENE_TOOL_NAME
import os

__metaclass__ = type


class StereoGene(OneVsOneMethod):
    def __init__(self):
        self._results = None
        super(StereoGene, self).__init__()

    def _getToolName(self):
        return STEREOGENE_TOOL_NAME

    def _setDefaultParamValues(self):
        self._params['tracks'] = []

    def setGenomeName(self, genomeName):
        pass

    def setChromLenFileName(self, chromLenFileName):
        self._params['chrom'] = chromLenFileName

    def _setQueryTrackFileName(self, trackFile):
        bedPath = self._getBedExtendedFileName(trackFile.path)
        self._addTrackTitleMapping(os.path.basename(bedPath), trackFile.title)
        self._params['tracks'] += [bedPath]


    def _setReferenceTrackFileName(self, trackFile):
        assert trackFile not in ['prebuilt', 'LOLACore_170206']
        bedPath = self._getBedExtendedFileName(trackFile.path)
        self._addTrackTitleMapping(os.path.basename(bedPath), trackFile.title)
        self._params['tracks'] += [bedPath]

    def setAllowOverlaps(self, allowOverlaps):
        assert allowOverlaps is True

    def _parseResultFiles(self):
        self._results = self._parseStatisticsFile(dirpath=self._resultFilesDict['output'])

    def getPValue(self):
        return self.getRemappedResultDict(OrderedDict([
            (key, SingleResultValue(self._getNumericFromStr(x['pVal']),
                                    x['pVal'])) for key, x in self._results.items()]))

    def getTestStatistic(self):
        return self.getRemappedResultDict(
            OrderedDict([(key,
                          SingleResultValue(self._getNumericFromStr(x['totCorr']),
                                            '<span title="' + \
                                            self.getTestStatDescr() \
                                            + '">'+'%.1f'%x['totCorr']+'</span>'))
            for key, x in self._results.items()]))

    @classmethod
    def getTestStatDescr(cls):
        return 'Correlation coefficient'

    def getFullResults(self):
        fullResults = open(self._resultFilesDict['stdout']).read().replace('\n','<br>\n')
        return self.getRemappedResultDict(OrderedDict([(key, fullResults) for key in self._results.keys()]))

    def preserveClumping(self, preserve):
        pass

    def setRestrictedAnalysisUniverse(self, restrictedAnalysisUniverse):
        assert restrictedAnalysisUniverse is None, restrictedAnalysisUniverse

    def setColocMeasure(self, colocMeasure):
        from conglomerate.methods.interface import ColocMeasureCorrelation
        assert isinstance(colocMeasure, ColocMeasureCorrelation), type(colocMeasure)

    def setHeterogeneityPreservation(self, preservationScheme, fn=None):
        pass

    def _parseStatisticsFile(self, dirpath):
        import xml.etree.ElementTree as et
        from os.path import join
        tree = et.parse(join(dirpath, 'statistics.xml'))
        root = tree.getroot()
        runsDict = OrderedDict()
        for run in root:
            parsedRun = self._parseRun(run)
            runsDict[(parsedRun['track1'], parsedRun['track2'])] = parsedRun
        return runsDict

    def _parseRun(self, run):
        resDict = OrderedDict()
        inputTag = run.find('input')
        resDict['track1'] = inputTag.attrib['track1']
        resDict['track2'] = inputTag.attrib['track2']
        res = run.find('res')
        resDict['totCorr'] = res.attrib['totCorr']
        resDict['pVal'] = res.attrib['pVal']
        return resDict

    def _printResults(self):
        print(self._results)

    def getResults(self):
        return self._results

    def getErrorDetails(self):
        assert not self.ranSuccessfully()
        #Not checked if informative
        if self._resultFilesDict is not None and 'stderr' in self._resultFilesDict:
            return open(self._resultFilesDict['stderr']).read().replace('\n','<br>\n')
        else:
            return 'Genometricorr did not provide any error output'

    def setRuntimeMode(self, mode):
        #also set corrOnly!?
        if mode =='quick':
            numPerm = 100
        elif mode == 'medium':
            numPerm = 1000
        elif mode == 'accurate':
            numPerm = 10000
        else:
            raise Exception('Invalid mode')
        self.setManualParam('nShuffle', numPerm)
