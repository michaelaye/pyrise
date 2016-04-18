import numpy as np
import pvl
from pathlib import Path
from six.moves.urllib.error import HTTPError
from six.moves.urllib.parse import urlunparse
from six.moves.urllib.request import urlretrieve

mosaic_extensions = '.cal.norm.map.equ.mos.cub'
# mosaic_extensions = '.cal.des.map.cub'


def hirise_dropbox():
    home = Path.home()
    return home / 'Dropbox' / 'data' / 'hirise'


def labels_root():
    dropbox = hirise_dropbox()
    return dropbox / 'labels'


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
    def s(self):
        return self.__str__()

    def get_upper_orbit_folder(self):
        '''
        get the upper folder name where the given orbit folder is residing on the
        hisync server
        '''
        lower = int(self.orbit) // 100 * 100
        return "_".join(["ORB", str(lower).zfill(6), str(lower + 99).zfill(6)])

    @property
    def storage_path_stem(self):
        s = "{phase}/{orbitfolder}/{obsid}".format(phase=self.phase,
                                                   orbitfolder=self.get_upper_orbit_folder(),
                                                   obsid=self.s)
        return s


class PRODUCT_ID(object):
    """Manage storage paths for HiRISE RDR products (also EXTRAS.)

    Attributes `jp2_path` and `label_path` get you the official RDR product,
    with `kind` steering if you get the COLOR or the RED product.
    All other properties go to the RDR/EXTRAS folder.

    """
    kinds = ['RED', 'BG', 'IR', 'COLOR', 'IRB','MIRB', 'MRGB', 'RGB']

    def __init__(self, initstr=None):
        if initstr is not None:
            tokens = initstr.split('_')
            self.obsid = OBSERVATION_ID('_'.join(tokens[:3]))
            try:
                self.kind = tokens[3]
            except IndexError:
                self._kind = None
        else:
            self._kind = None

    @property
    def kind(self):
        return self._kind

    @kind.setter
    def kind(self, value):
        if value not in self.kinds:
            raise ValueError("kind must be in {}".format(self.kinds))
        self._kind = value

    def __str__(self):
        return "{}_{}".format(self.obsid, self.kind)

    def __repr__(self):
        return self.__str__()

    @property
    def s(self):
        return self.__str__()

    @property
    def storage_stem(self):
        return '{}/{}'.format(self.obsid.storage_path_stem, self.s)

    @property
    def label_fname(self):
        return '{}.LBL'.format(self.s)


    @property
    def label_path(self):
        return 'RDR/' + self.storage_stem + '.LBL'

    @property
    def jp2_fname(self):
        return self.s + '.JP2'

    @property
    def jp2_path(self):
        prefix = 'RDR/'
        postfix = ''
        if self.kind not in ['RED', 'COLOR']:
            prefix += 'EXTRAS/'
        if self.kind in ['IRB']:
            postfix = '.NOMAP'
        return prefix + self.storage_stem + postfix + ".JP2"

    @property
    def nomap_jp2_path(self):
        if self.kind in ['RED', 'IRB', 'RGB']:
            return 'RDR/EXTRAS/' + self.storage_stem + '.NOMAP.JP2'
        else:
            raise AttributeError("No NOMAP exists for {}.".format(self.kind))

    @property
    def quicklook_path(self):
        if self.kind in ['COLOR', 'RED']:
            return Path('EXTRAS/RDR/') / (self.storage_stem + ".QLOOK.JP2")
        else:
            raise AttributeError("No quicklook exists for {} products.".format(self.kind))

    @property
    def abrowse_path(self):
        if self.kind in ['COLOR', 'MIRB', 'MRGB', 'RED']:
            return Path('EXTRAS/RDR/') / (self.storage_stem + '.abrowse.jpg')
        else:
            raise AttributeError("No abrowse exists for {}".format(self.kind))

    @property
    def browse_path(self):
        inset = ''
        if self.kind in ['IRB', 'RGB']:
            inset = '.NOMAP'
        if not self.kind in ['COLOR', 'MIRB', 'MRGB', 'RED', 'IRB', 'RGB']:
            raise AttributeError("No browse exists for {}".format(self.kind))
        else:
            return Path('EXTRAS/RDR/') / (self.storage_stem + inset + '.browse.jpg')

    @property
    def thumbnail_path(self):
        if self.kind in ['BG', 'IR']:
            raise AttributeError("No thumbnail exists for {}".format(self.kind))
        inset = ''
        if self.kind in ['IRB', 'RGB']:
            inset = '.NOMAP'
        return Path('EXTRAS/RDR/') / (self.storage_stem + inset + '.thumb.jpg')

    @property
    def nomap_thumbnail_path(self):
        if self.kind in ['RED', 'IRB', 'RGB']:
            return Path('EXTRAS/RDR') / (self.storage_stem + '.NOMAP.thumb.jpg')
        else:
            raise AttributeError("No NOMAP thumbnail exists for {}".format(self.kind))

    @property
    def nomap_browse_path(self):
        if self.kind in ['RED', 'IRB', 'RGB']:
            return Path('EXTRAS/RDR') / (self.storage_stem + '.NOMAP.browse.jpg')


class SOURCE_PRODUCT_ID(object):

    red_ccds = ['RED'+str(i) for i in range(10)]
    ir_ccds = ['IR10', 'IR11']
    bg_ccds = ['BG12', 'BG13']
    ccds = red_ccds + ir_ccds + bg_ccds

    def __init__(self, sprodid=None):
        if sprodid is not None:
            tokens = sprodid.split('_')
            obsid = '_'.join(tokens[:3])
            ccd = tokens[3]
            color, ccdno = self._parse_ccd(ccd)
            self.prodid = PRODUCT_ID('_'.join([obsid, color]))
            self.ccd = ccd
            self.channel = tokens[4]
        else:
            self.prodid = None
            self._channel = None
            self._ccd = None

    def _parse_ccd(self, value):
        sep = 2 if value[:2] in PRODUCT_ID.kinds else 3
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
        return self._ccd

    @ccd.setter
    def ccd(self, value):
        if value not in self.ccds:
            raise ValueError("CCD value must be in {}.".format(self.ccds))
        self._ccd = value
        self.prodid.color = self.color

    @property
    def color(self):
        return self._parse_ccd(self.ccd)[0]

    @property
    def ccdno(self):
        offset = len(self.color)
        return self.ccd[offset:]

    def __str__(self):
        return "{}{}_{}".format(self.prodid, self.ccdno, self.channel)

    def __repr__(self):
        return self.__str__()

    @property
    def s(self):
        return self.__str__()

    @property
    def fname(self):
        return self.s + '.IMG'


class HiRISE_Basename(object):

    def __init__(self, basename):
        self.basename = Path(basename)
        self.prodid = PRODUCT_ID(self.basename.stem)


class HiRISE_URL(object):
    initurl = ('http://hirise-pds.lpl.arizona.edu/PDS/RDR/'
               'ESP/ORB_011400_011499/ESP_011491_0985/ESP_'
               '011491_0985_RED.LBL')
    scheme = 'http'
    netloc = 'hirise-pds.lpl.arizona.edu'
    pdspath = Path('/PDS')

    def __init__(self, product_path, params=None, query=None, fragment=None):
        self.product_path = product_path
        self.params = params
        self.query = query
        self.fragment = fragment

    @property
    def path(self):
        path = self.pdspath / self.product_path
        return str(path)


    @property
    def labelurl(self):
        return urlunparse([self.scheme, self.netloc, self.path,
                           self.params, self.query, self.fragment])


def get_rdr_red_label(obsid):
    """Download the RED PRODUCT_ID label for `obsid`.

    Parameters
    ----------
    obsid : str
        HiRISE obsid in the standard form of ESP_012345_1234

    Returns
    -------
    None
        Storing the label file in the `labels_root` folder.
    """
    prodid = PRODUCT_ID(obsid)
    prodid.kind = 'RED'
    url = HiRISE_URL(prodid.s)
    savepath = labels_root() / Path(prodid.label_fname)
    savepath.parent.mkdir(exist_ok=True)
    print("Downloading\n", url.rdr_labelurl, 'to\n', savepath)
    try:
        urlretrieve(url.rdr_labelurl, str(savepath))
    except HTTPError as e:
        print(e)


def get_rdr_color_label(obsid):
    """Download the RED PRODUCT_ID label for `obsid`.

    Parameters
    ----------
    obsid : str
        HiRISE obsid in the standard form of ESP_012345_1234

    Returns
    -------
    None
        Storing the label file in the `labels_root` folder.
    """
    prodid = PRODUCT_ID(obsid)
    prodid.kind = 'COLOR'
    url = HiRISE_URL(prodid.s)
    savepath = labels_root() / Path(prodid.label_fname)
    savepath.parent.mkdir(exist_ok=True)
    print("Downloading\n", url.rdr_labelurl, 'to\n', savepath)
    try:
        urlretrieve(url.rdr_labelurl, str(savepath))
    except HTTPError as e:
        print(e)


class HiRISE_Label(object):

    def __init__(self, fname):
        self.label = pvl.load(str(fname))

    @property
    def binning_red(self):
        return self.label['INSTRUMENT_SETTING_PARAMETERS']['MRO:BINNING'][4]

    @property
    def binning_color(self):
        return self.label['INSTRUMENT_SETTING_PARAMETERS']['MRO:BINNING'][-1]

    @property
    def lines(self):
        return self.label['UNCOMPRESSED_FILE']['IMAGE']['LINES']

    @property
    def line_samples(self):
        return self.label['UNCOMPRESSED_FILE']['IMAGE']['LINE_SAMPLES']

    @property
    def l_s(self):
        return self.label['VIEWING_PARAMETERS']['SOLAR_LONGITUDE'].value

    @property
    def map_scale(self):
        return self.label['IMAGE_MAP_PROJECTION']['MAP_SCALE'].value


def get_color_from_path(path):
    basename = HiRISE_Basename(path)
    return basename.prodid.color


def get_obsid_from_path(path):
    basename = HiRISE_Basename(Path(path).name)
    return basename.prodid.obsid


def rebin(a, newshape):
    """Rebin an array to a new shape."""
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
