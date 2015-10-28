import numpy as np
from os.path import join as pjoin

mosaic_extensions = '.cal.norm.map.equ.mos.cub'
# mosaic_extensions = '.cal.des.map.cub'

class Coordinates:
    path = ''
    obsID = 0
    sample = 0
    line = 0
    latitude = 0
    longitude = 0
    x = 0
    y = 0

def getCCDColourFromMosPath(path):
    basename = Path(path).parent
    firstpart = basename.partition('.')[0]
    try:
        return firstpart.split('_')[3]
    except:
        print(path)

    if instr == 'hirise':
        obsID = basename[:15]
        try:
            phase, orbit, targetcode = obsID.split('_')
        except ValueError:
            print("Path does not have standard ObsID, returning first 15 characters.")
        return obsID
    if instr == 'ctx':
        try:
            obsID = basename.split('_')[1]
        except IndexError:
            print("Path does not have CTX file name format. Returning empty")
            return ''
            

def getUpperOrbitFolder(orbitNumber):
    '''
    get the upper folder name where the given orbit folder is residing on the 
    hisync server
    input: orbitNumber(int)
    '''
    lower = int(orbitNumber) / 100 * 100
    return "_".join(["ORB", str(lower).zfill(6), str(lower + 99).zfill(6)])

def getEDRFolder(orbitNumber):
    '''
    get the upper folder name where the given orbit folder is stored on hirise
    input: orbitNumber(int)
    '''
    lower = int(orbitNumber) / 1000 * 1000
    return "_".join(["EDRgen", str(lower).zfill(6), str(lower + 999).zfill(6)])

def getUsersProcessedPath():
    path = DEST_BASE
    if sys.platform == 'darwin':
        # on the Mac, don't create extra folder for processed files
        pass
    else:
        path = pjoin(path, os.environ['LOGNAME'])
    return path

def getSourcePathFromID(idString):
    sciencePhase, orbitString, targetCode = idString.split("_")
    path = FROM_BASE
    if not sys.platform == 'darwin':
        path = pjoin(path, getEDRFolder(int(orbitString)))
        path = pjoin(path, getUpperOrbitFolder(int(orbitString)))
    path = pjoin(path, idString)
    return path

def getDestPathFromID(idString):
    path = getUsersProcessedPath()
    path = pjoin(path, idString)
    return path

def getStoredPathFromID(idString, in_work=False):
    folder = ''
        folder = 'maye'
    path = pjoin(DEST_BASE, folder, idString)
    return path

def getMosPathFromIDandCCD(obsID, ccd, in_work=False):
    root = getStoredPathFromID(obsID, in_work)
    path = os.path.join(root, '_'.join([obsID, ccd]) + mosaic_extensions)
    return path


def rebin(a, newshape):


def rebin_factor(a, newshape):
