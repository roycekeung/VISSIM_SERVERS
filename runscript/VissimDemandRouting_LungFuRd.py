from xml.dom import minidom
import os

#----------------------------------------------------------#
# --- --- --- --- --- Class Definition --- --- --- --- --- #
#----------------------------------------------------------#

class ModVissimDemand():
    def __init__(self, vissimFolderPath):
        self.vissimFolderPath = vissimFolderPath
        self.dom = minidom.parse(os.path.join( vissimFolderPath,'LungFuRd.inpx'))
        net = self.dom.documentElement
        self.vehInputs = net.getElementsByTagName('vehicleInputs')[0]
        self.vehRoutes = net.getElementsByTagName('vehicleRoutingDecisionsStatic')[0]

    # unused
    def modDemandByRatio(self, rate):
        for input in self.vehInputs.getElementsByTagName('vehicleInput'):
            for vehVol in input.getElementsByTagName('timeIntVehVols')[0].getElementsByTagName('timeIntervalVehVolume'):
                vehVol.setAttribute('volume', str(int(round(int(vehVol.getAttribute('volume')) * rate))))

    def setDemand(self, arm, volume):
        for input in self.vehInputs.getElementsByTagName('vehicleInput'):
            if input.getAttribute('name') == arm:
                input.getElementsByTagName('timeIntVehVols')[0].getElementsByTagName('timeIntervalVehVolume')[0].setAttribute('volume', str(volume))
                break

    def setDemandBySec(self, arm, volume):
        for input in self.vehInputs.getElementsByTagName('vehicleInput'):
            if input.getAttribute('name') == arm:
                i = 0
                curr = 0
                for inputVol in input.getElementsByTagName('timeIntVehVols')[0].getElementsByTagName('timeIntervalVehVolume'):
                    inputVol.setAttribute('cont', 'false')
                    if i == round(curr):
                        needAdd = 1
                        curr += 3600/volume
                        while i == round(curr):
                            needAdd += 1
                            curr += 3600/volume
                        inputVol.setAttribute('volume', str(needAdd*3600))
                    else:
                        inputVol.setAttribute('volume', str(0))
                    i += 1

    def setTurningRatio(self, fromArm, movement, value):
        for vrds in self.vehRoutes.getElementsByTagName('vehicleRoutingDecisionStatic'):
            if vrds.getAttribute('name') == fromArm:
                for movementEntry in vrds.getElementsByTagName('vehRoutSta')[0].getElementsByTagName('vehicleRouteStatic'):
                    if movementEntry.getAttribute('name') == movement:
                        movementEntry.setAttribute('relFlow', '2 0:'+str(value))
                        break
                break

    def save(self):
        str0 = self.dom.toxml(encoding='UTF-8')
        wf = open(os.path.join( self.vissimFolderPath,'LungFuRd.inpx'), 'wb')
        wf.write(str0)
        wf.flush()
        wf.close()

#---------------------------------------------------------------#
# --- --- --- --- --- Convenience Functions --- --- --- --- --- #
#---------------------------------------------------------------#

def applyDmdAMPeak(vissimFolderPath, rate=1):
    mod = ModVissimDemand(vissimFolderPath)
    # Demand Input
    mod.setDemand('A-Entry', 3343*rate) #LungFuRd SB
    mod.setDemand('B-Entry', 314*rate) #LungMunRd SB
    mod.setDemand('C-Entry', 1292*rate) #LungMunRd NB
    mod.setDemand('D-Entry', 1186*rate) #TMCLKL NB
    # Turning Ratio
    mod.setTurningRatio('A-Entry', 'L', 0)
    mod.setTurningRatio('A-Entry', 'S', 2153)
    mod.setTurningRatio('A-Entry', 'R', 1190)
    mod.setTurningRatio('A-Entry', 'U', 0)

    mod.setTurningRatio('B-Entry', 'L1', 141) #exclusive turn (assume all LT using exclusive turn for now)
    mod.setTurningRatio('B-Entry', 'L2', 0) #through roundabout
    mod.setTurningRatio('B-Entry', 'S', 173)
    mod.setTurningRatio('B-Entry', 'R', 0)
    mod.setTurningRatio('B-Entry', 'U', 0)

    mod.setTurningRatio('C-Entry', 'L1', 650) #exclusive turn (assume all LT using exclusive turn for now)
    mod.setTurningRatio('C-Entry', 'L2', 0) #through roundabout
    mod.setTurningRatio('C-Entry', 'S', 433)
    mod.setTurningRatio('C-Entry', 'R', 209)
    mod.setTurningRatio('C-Entry', 'U', 0)

    mod.setTurningRatio('D-Entry', 'L1', 898) #exclusive turn (assume all LT using exclusive turn for now)
    mod.setTurningRatio('D-Entry', 'L2', 0) #through roundabout
    mod.setTurningRatio('D-Entry', 'S', 262)
    mod.setTurningRatio('D-Entry', 'R', 26)
    mod.setTurningRatio('D-Entry', 'U', 0)

    mod.save()
    
def applyDmdPMPeak(vissimFolderPath, rate=1):
    mod = ModVissimDemand(vissimFolderPath)
    # Demand Input
    mod.setDemand('A-Entry', 2134*rate) #LungFuRd SB
    mod.setDemand('B-Entry', 133*rate) #LungMunRd SB
    mod.setDemand('C-Entry', 1643*rate) #LungMunRd NB
    mod.setDemand('D-Entry', 2091*rate) #TMCLKL NB
    # Turning Ratio
    mod.setTurningRatio('A-Entry', 'L', 0)
    mod.setTurningRatio('A-Entry', 'S', 1108)
    mod.setTurningRatio('A-Entry', 'R', 1026)
    mod.setTurningRatio('A-Entry', 'U', 0)

    mod.setTurningRatio('B-Entry', 'L1', 60) #exclusive turn (assume all LT using exclusive turn for now)
    mod.setTurningRatio('B-Entry', 'L2', 0) #through roundabout
    mod.setTurningRatio('B-Entry', 'S', 73)
    mod.setTurningRatio('B-Entry', 'R', 0)
    mod.setTurningRatio('B-Entry', 'U', 0)

    mod.setTurningRatio('C-Entry', 'L1', 14) #exclusive turn (assume all LT using exclusive turn for now)
    mod.setTurningRatio('C-Entry', 'L2', 0) #through roundabout
    mod.setTurningRatio('C-Entry', 'S', 1371)
    mod.setTurningRatio('C-Entry', 'R', 258)
    mod.setTurningRatio('C-Entry', 'U', 0)

    mod.setTurningRatio('D-Entry', 'L1', 949) #exclusive turn (assume all LT using exclusive turn for now)
    mod.setTurningRatio('D-Entry', 'L2', 0) #through roundabout
    mod.setTurningRatio('D-Entry', 'S', 1102)
    mod.setTurningRatio('D-Entry', 'R', 40)
    mod.setTurningRatio('D-Entry', 'U', 0)

    mod.save()

# #---------------------------------------------------#
# # --- --- --- --- --- Test Code --- --- --- --- --- #
# #---------------------------------------------------#
# vissimFilePath = 'C:\\Users\\User\\Documents\\temp transfer\\temp\\LungFuRd_newLayout 2022-01-28 (AM)(HwD)(wSig)(AC2)\\' #to be updated
# rate=1  # Change this rate to apply multiplication factor

# applyDmdAMPeak(vissimFilePath, rate)
# #applyDmdPMPeak(vissimFilePath, rate)