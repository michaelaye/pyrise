from pathlib import Path
from six.moves.urllib.parse import urlunparse
from six.moves.urllib.error import HTTPError
from six.moves.urllib.request import urlretrieve
import logging


logger = logging.getLogger(__name__)


class HiRISE_URL(object):
    """Manage HiRISE URLs.

    Provide a storage path as calculated from above objects and put together the full
    URL to the HiRISE product.

    Parameters
    ----------
    product_path : str or pathlib.Path
        Storage path to the product


    """
    initurl = ('https://hirise-pds.lpl.arizona.edu/PDS/RDR/'
               'ESP/ORB_011400_011499/ESP_011491_0985/ESP_'
               '011491_0985_RED.LBL')
    scheme = 'https'
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
    def url(self):
        return urlunparse([self.scheme, self.netloc, self.path,
                           self.params, self.query, self.fragment])


class OBSERVATION_ID(object):
    """Manage HiRISE observation ids.

    For example PSP_003092_0985.

    `phase` is set to PSP for orbits < 11000, no setting required.

    Parameters
    ----------
    obsid : str, optional
        One can optionally also create an 'empty' OBSERVATION_ID object and set the
        properties accordingly to create a new obsid.
    """

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

    Parameters
    ----------
    initstr : str, optional

    Note
    ----
    The "PDS" part of the path is handled in the HiRISE_URL class.

    """
    kinds = ['RED', 'BG', 'IR', 'COLOR', 'IRB', 'MIRB', 'MRGB', 'RGB']

    @classmethod
    def from_path(cls, path):
        path = Path(path)
        return cls(path.stem)

    def __init__(self, initstr=None):
        if initstr is not None:
            tokens = initstr.split('_')
            self._obsid = OBSERVATION_ID('_'.join(tokens[:3]))
            try:
                self.kind = tokens[3]
            except IndexError:
                self._kind = None
        else:
            self._kind = None

    @property
    def obsid(self):
        return self._obsid

    @obsid.setter
    def obsid(self, value):
        self._obsid = OBSERVATION_ID(value)

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

    def _make_url(self, obj):
        path = getattr(self, f"{obj}_path")
        return HiRISE_URL(path).url

    def __getattr__(self, item):
        tokens = item.split('_')
        try:
            if tokens[-1] == 'url':
                return self._make_url('_'.join(tokens[:-1]))
        except IndexError:
            raise ValueError(f"No attribute named '{item}' found.")

    # TODO: implement general self.obj_url for all paths.

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
        if self.kind not in ['COLOR', 'MIRB', 'MRGB', 'RED', 'IRB', 'RGB']:
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

    @property
    def edr_storage_stem(self):
        return 'EDR/' + self.storage_stem


class SOURCE_PRODUCT_ID(object):
    """Manage SOURCE_PRODUCT_ID.

    Example
    -------
    'PSP_003092_0985_RED4_0'
    """

    red_ccds = ['RED' + str(i) for i in range(10)]
    ir_ccds = ['IR10', 'IR11']
    bg_ccds = ['BG12', 'BG13']
    ccds = red_ccds + ir_ccds + bg_ccds

    def __init__(self, spid=None, saveroot=None):
        if spid is not None:
            tokens = spid.split('_')
            obsid = '_'.join(tokens[:3])
            ccd = tokens[3]
            color, ccdno = self._parse_ccd(ccd)
            self.pid = PRODUCT_ID('_'.join([obsid, color]))
            self.ccd = ccd
            self.channel = tokens[4]
            self.saveroot = saveroot
        else:
            self.pid = None
            self._channel = None
            self._ccd = None

    def __getattr__(self, value):
        return getattr(self.pid, value)

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
        if self.pid is not None:
            self.pid.color = self.color

    @property
    def color(self):
        return self._parse_ccd(self.ccd)[0]

    @property
    def ccdno(self):
        offset = len(self.color)
        return self.ccd[offset:]

    def __str__(self):
        return "{}: {}{}_{}".format(self.__class__.__name__, self.pid, self.ccdno, self.channel)

    def __repr__(self):
        return self.__str__()

    @property
    def s(self):
        return "{}{}_{}".format(self.pid, self.ccdno, self.channel)

    @property
    def fname(self):
        return self.s + '.IMG'

    @property
    def local_cube(self):
        return self.local_path.with_suffix('.cub')

    @property
    def fpath(self):
        return Path(self.pid.edr_storage_stem).parent / self.fname

    @property
    def furl(self):
        hiurl = HiRISE_URL(self.fpath)
        return hiurl.url

    @property
    def stitched_cube_name(self):
        return f"{self.pid.obsid.s}_{self.ccd}.cub"

    @property
    def local_path(self):
        savepath = self.saveroot / str(self.obsid) / self.fname
        return savepath

    def download(self, overwrite=False):
        savepath = self.local_path
        if savepath.exists() and not overwrite:
            logger.warning("File exists and I'm not allowed to overwrite:"
                           " %s", savepath)
            return
        savepath.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Downloading\n{self.furl}\nto\n{savepath}")
        try:
            urlretrieve(self.furl, str(savepath))
        except HTTPError as e:
            logger.error(e.__str__())


class RED_PRODUCT_ID(SOURCE_PRODUCT_ID):
    def __init__(self, obsid, ccdno, channel, **kwargs):
        self.ccds = self.red_ccds
        super().__init__('{}_RED{}_{}'.format(obsid, ccdno, channel),
                         **kwargs)


class IR_PRODUCT_ID(SOURCE_PRODUCT_ID):
    def __init__(self, obsid, ccdno, channel):
        self.ccds = self.ir_ccds
        super().__init__('{}_IR{}_{}'.format(obsid, ccdno, channel))
