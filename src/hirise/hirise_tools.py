from pathlib import Path
import numpy as np
from os.path import join as pjoin
from urllib.request import urlretrieve

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


class OBSERVATION_ID(object):
    # ESP_012345_1234

    def __init__(self, obsid=None):
        if obsid is not None:
            phase, orbit, targetcode = obsid.split('_')
            self._orbit = int(orbit)
            self._targetcode = targetcode
        else:
            self._orbit = None
            self._targetcode = None

    @property
    def orbit(self):
        return str(self._orbit).zfill(6)

    @orbit.setter
    def orbit(self, value):
        if value > 999999:
            raise ValueError("Orbit cannot be larger than 999999")
        self._orbit = value

    @property
    def targetcode(self):
        return self._targetcode

    @targetcode.setter
    def targetcode(self, value):
        if len(str(value)) != 4:
            raise ValueError('Targetcode must be exactly 4 characters.')
        self._targetcode = value

    @property
    def phase(self):
        return 'PSP' if int(self.orbit) < 11000 else 'ESP'

    def __str__(self):
        return '{}_{}_{}'.format(self.phase, self.orbit, self.targetcode)

    def __repr__(self):
        return self.__str__()

    @property
    def obsid(self):
        return self.__str__()

    def get_upper_orbit_folder(self):
        '''
        get the upper folder name where the given orbit folder is residing on the
        hisync server
        '''
        lower = self.orbit // 100 * 100
        return "_".join(["ORB", str(lower).zfill(6), str(lower + 99).zfill(6)])


class PRODUCT_ID(OBSERVATION_ID):
    # ESP_012345_1234_RED

    colors = ['RED', 'BG', 'IR']
    ccdnumbers = dict(RED=range(10), IR=[10, 11], BG=[12, 13])

    def __init__(self, initstr=None):
        if initstr is not None:
            tokens = initstr.split('_')
            super().__init__('_'.join(tokens[:3]))
            try:
                self._color = tokens[3]
            except IndexError:
                self._color = None
        else:
            self._color = None

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if value not in self.colors:
            raise ValueError("Color must be in {}".format(self.colors))
        self._color = value

    def __str__(self):
        return "{}_{}".format(super().__str__(), self.color)

    def __repr__(self):
        return self.__str__()

    @property
    def pid(self):
        return self.__str__()


class SOURCE_PRODUCT_ID(PRODUCT_ID):

    red_ccds = ['RED'+str(i) for i in range(10)]
    ir_ccds = ['IR10', 'IR11']
    bg_ccds = ['BG12', 'BG13']
    ccds = red_ccds + ir_ccds + bg_ccds

    def __init__(self, sprodid=None):
        if sprodid is not None:
            tokens = sprodid.split('_')
            obsid = '_'.join(tokens[:3])
            self._ccd = tokens[3]
            color, ccdno = self._parse_colorccdno(tokens[3])
            prodid = '_'.join([obsid, color])
            super().__init__(prodid)
            self._channel = tokens[4]

        else:
            super().__init__(None)
            self._channel = None

    def _parse_colorccdno(self, value):
        sep = 2 if value[:2] in PRODUCT_ID.colors else 3
        return value[:sep], value[sep:]

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, value):
        if int(value) not in [0, 1]:
            raise ValueError("channel must be in [0, 1]")
        self._channel = value

    @property
    def ccd(self):
        return str(self._ccd)

    @ccd.setter
    def ccd(self, value):
        if value not in self.ccds:
            raise ValueError("CCD value must be in {}.".format(self.ccds))
        self._ccd = value

    def __str__(self):
        return "{}{}_{}".format(super().__str__()[:-3], self.ccd, self.channel)


class HiRISE_Basename(object):

    def __init__(self, basename):
        self.obsid = HiRISE_Obsid(obsid[15])
        self.color = basename


class HiRISE_Path(object):

    @classmethod
    def from_str(cls, s):
        return cls()


class HiRISE_URL(object):
    initurl = ('http://hirise-pds.lpl.arizona.edu/PDS/RDR/'
               'ESP/ORB_011400_011499/ESP_011491_0985/ESP_'
               '011491_0985_RED.LBL')

    def __init__(self, phase, RDR=True, parse_result=None):
        if parse_result is None:
            parse_result = urlparse(self.initurl)
        self.scheme = parse_result.scheme
        self.netloc = parse_result.netloc
        self.path = parse_result.path
        self.params = parse_result.params
        self.query = parse_result.query
        self.fragment = parse_result.fragment

    def get_url(self):
        return urlunparse([self.scheme, self.netloc, self.path,
                           self.params, self.query, self.fragment])

    @classmethod
    def from_url(cls, url):
        return cls(urlparse(url))


def getCCDColourFromMosPath(path):
    basename = Path(path).parent
    firstpart = basename.partition('.')[0]
    try:
        return firstpart.split('_')[3]
    except:
        print(path)


def getObsIDFromPath(path, instr='hirise'):
    basename = Path(path).parent
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
    if in_work is True:
        folder = 'maye'
    path = pjoin(DEST_BASE, folder, idString)
    return path


def getMosPathFromIDandCCD(obsID, ccd, in_work=False):
    root = getStoredPathFromID(obsID, in_work)
    path = os.path.join(root, '_'.join([obsID, ccd]) + mosaic_extensions)
    return path


def rebin(a, newshape):
    '''Rebin an array to a new shape.
    '''
    assert len(a.shape) == len(newshape)

    slices = [slice(0, old, float(old) / new) for old, new in zip(a.shape, newshape)]
    coordinates = np.mgrid[slices]
    indices = coordinates.astype('i')  # choose the biggest smaller integer index
    print(len(indices), indices.max())
    return a[tuple(indices)]


def rebin_factor(a, newshape):
    '''Rebin an array to a new shape.
    newshape must be a factor of a.shape.
    '''
    assert len(a.shape) == len(newshape)
    assert not np.sometrue(np.mod(a.shape, newshape))

    slices = [slice(None, None, old / new) for old, new in zip(a.shape, newshape)]
    return a[slices]
