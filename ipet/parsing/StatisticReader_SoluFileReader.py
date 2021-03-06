'''
The MIT License (MIT)

Copyright (c) 2016 Zuse Institute Berlin, www.zib.de

Permissions are granted as stated in the license file you have obtained
with this software. If you find the library useful for your purpose,
please refer to README.md for how to cite IPET.

@author: Gregor Hendel
'''
from .StatisticReader import StatisticReader
import re
import numpy as np

class SoluFileReader(StatisticReader):
    """
    a reader for solu file context information
    """
    name = 'SoluFileReader'
    actions = {}
    datakeys = ['OptVal', 'SoluFileStatus']
    statistics = {}
    columnwidth = 12
    columnheaderstr = 'SoluFile'.rjust(columnwidth)
    context = StatisticReader.CONTEXT_SOLUFILE

    def setTestRun(self, testrun):
        self.testrun = testrun
        if testrun != None:
            self.statistics = self.testrun.data

    def extractStatistic(self, line):
        assert self.testrun != None
        match = re.match("^=([a-zA-Z]+)=", line)
        if match:
            method = getattr(self, "new" + match.groups(0)[0] + "Instance")
            method(line)
        else:
            return None


    def storeToStatistics(self, instance, objval, status):
        if self.testrun.hasInstance(instance):
            self.testrun.addData(instance, self.datakeys, [float(objval), status])



    def newoptInstance(self, line):
        splittedline = line.split()
        assert splittedline[0] == '=opt='
        instance = splittedline[1]
        objval = splittedline[2]

        self.storeToStatistics(instance, objval, status = 'opt')

    def newinfInstance(self, line):
        splittedline = line.split()
        assert splittedline[0] == '=inf='
        instance = splittedline[1]
        objval = np.nan

        self.storeToStatistics(instance, objval, status = 'inf')

    def newunknInstance(self, line):
        splittedline = line.split()
        assert splittedline[0] == '=unkn='
        instance = splittedline[1]
        objval = np.nan

        self.storeToStatistics(instance, objval, status = 'unkn')


    def newbestInstance(self, line):
        splittedline = line.split()
        assert splittedline[0] == '=best='
        instance = splittedline[1]
        objval = splittedline[2]

        self.storeToStatistics(instance, objval, status = 'best')

    def newcutInstance(self, line):
        splittedline = line.split()
        assert splittedline[0] == '=cut='
        instance = splittedline[1]
        objval = splittedline[2]

        self.storeToStatistics(instance, objval, status = 'cut')

    def newfeasInstance(self, line):
        splittedline = line.split()
        assert splittedline[0] == '=feas='
        instance = splittedline[1]
        objval = np.nan

        self.storeToStatistics(instance, objval, status = 'feas')

    def newbestdualInstance(self, line):
        splittedline = line.split()
        assert splittedline[0] == '=bestdual='
        instance = splittedline[1]
        dualval = splittedline[2]

        # self.storeToStatistics(instance, objval, status='bestdual')
