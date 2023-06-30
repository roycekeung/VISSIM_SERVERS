


import sys



import DISCO2_PyModule_Vissim

# implement override class
class implVissimRunner(DISCO2_PyModule_Vissim.Runner_VissimAsync):
    # called per (sub)generation, must complete all cases at method return
    def pyRunAll(self):
        # returns the count of cases that have not had its eval value set
        n = self.getRemainingRunCaseNum()
        # relies on TDSigConvertor Vissim sig file mappings, will always modify the same files
        tId = self.makeNextSigFiles()
        evalValue = 900
        # should no throw, getRemainingRunCaseNum()-- iff caseId && evalValue are valid
        self.setEvalValue(tId, evalValue)

holder = DISCO2_PyModule_Vissim.Holder()
holder.loadTdSigData("mkTdSigData.xml") 
holder.clearSigFilePath()
holder.addSigFilePath("PokOi1.sig")  
holder.addSigFilePAth("PokOi2.sig")

# put in the override class
runnerVissim = implVissimRunner()
holder.setVissimRunner(runnerVissim)
holder.setUseCustomRunner(True)

excludeList = DISCO2_PyModule_Vissim.vecInt()
excludeList[:] = []
holder.initGA(0, excludeList)

newPlanId = holder.runGA(numOfGen, popSize)





if __name__ == '__main__':
    try:
        # LoadBalancer('localhost', 5555, 'round robin').start()
        print('run')
    except KeyboardInterrupt:
        print ("Ctrl C - Stopping load_balancer")
        sys.exit(1)
        
        