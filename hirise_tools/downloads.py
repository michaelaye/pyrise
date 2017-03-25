from pathlib import Path

from six.moves.urllib.error import HTTPError
from six.moves.urllib.request import urlretrieve

from .products import PRODUCT_ID, RED_PRODUCT_ID, HiRISE_URL


def hirise_dropbox():
    return Path.home() / 'Dropbox' / 'data' / 'hirise'


def labels_root():
    return hirise_dropbox() / 'labels'


def get_rdr_some_label(kind, obsid):
    """Download `some` PRODUCT_ID label for `obsid`.

    Note
    ----
    The RED channel is also called the B&W channel on the HiRISE website.

    Parameters
    ----------
    kind : {'RED', 'COLOR'}
        String that determines the kind of color looking for.
    obsid : str
        HiRISE obsid in the standard form of ESP_012345_1234

    Returns
    -------
    None
        Storing the label file in the `labels_root` folder.
    """
    pid = PRODUCT_ID(obsid)
    pid.kind = kind
    savepath = labels_root() / Path(pid.label_fname)
    savepath.parent.mkdir(exist_ok=True)
    print("Downloading\n", pid.label_url, 'to\n', savepath)
    try:
        urlretrieve(pid.label_url, str(savepath))
    except HTTPError as e:
        print(e)


def get_rdr_red_label(obsid):
    """Download the RED PRODUCT_ID label for `obsid`.

    Note
    ----
    The RED channel is also called the B&W channel on the HiRISE website.

    Parameters
    ----------
    obsid : str
        HiRISE obsid in the standard form of ESP_012345_1234

    Returns
    -------
    None
        Storing the label file in the `labels_root` folder.
    """
    get_rdr_some_label('RED', obsid)


def get_rdr_color_label(obsid):
    """Download the COLOR PRODUCT_ID label for `obsid`.

    Parameters
    ----------
    obsid : str
        HiRISE obsid in the standard form of ESP_012345_1234

    Returns
    -------
    None
        Storing the label file in the `labels_root` folder.
    """
    get_rdr_some_label('COLOR', obsid)


def download_product(prodid_path, saveroot=None):
    if saveroot is None:
        saveroot = hirise_dropbox()
    else:
        saveroot = Path(saveroot)
        if not saveroot.is_absolute():
            saveroot = hirise_dropbox() / saveroot

    saveroot.mkdir(exist_ok=True)
    url = HiRISE_URL(prodid_path)
    savepath = saveroot / prodid_path.name
    print("Downloading\n", url.url, 'to\n', savepath)
    try:
        urlretrieve(url.url, str(savepath))
    except HTTPError as e:
        print(e)
    return savepath


def download_RED_product(obsid, ccdno, channel, saveroot=None, overwrite=False):
    if saveroot is None:
        saveroot = hirise_dropbox()
    else:
        saveroot = Path(saveroot)
        if not saveroot.is_absolute():
            saveroot = hirise_dropbox() / saveroot

    pid = RED_PRODUCT_ID(obsid, ccdno, channel)
    savepath = saveroot / obsid / pid.fname
    savepath.parent.mkdir(parents=True, exist_ok=True)

    # if file already is there:
    if savepath.exists() and not overwrite:
        return savepath

    print("Downloading\n", pid.furl, '\nto\n', savepath)
    try:
        urlretrieve(pid.furl, str(savepath))
    except HTTPError as e:
        print(e)
    return savepath
