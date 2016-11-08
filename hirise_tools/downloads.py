from pathlib import Path
from .products import PRODUCT_ID, HiRISE_URL, hirise_dropbox
from six.moves.urllib.request import urlretrieve
from six.moves.urllib.error import HTTPError


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
    url = HiRISE_URL(prodid.label_path)
    savepath = labels_root() / Path(prodid.label_fname)
    savepath.parent.mkdir(exist_ok=True)
    print("Downloading\n", url.url, 'to\n', savepath)
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
    url = HiRISE_URL(prodid.label_path)
    savepath = labels_root() / Path(prodid.label_fname)
    savepath.parent.mkdir(exist_ok=True)
    print("Downloading\n", url.rdr_labelurl, 'to\n', savepath)
    try:
        urlretrieve(url.rdr_labelurl, str(savepath))
    except HTTPError as e:
        print(e)


def download_product(prodid_path, saveroot=None):
    saveroot = Path(saveroot)
    if saveroot is None:
        saveroot = hirise_dropbox()
    elif not saveroot.is_absolute():
        saveroot = hirise_dropbox() / saveroot

    url = HiRISE_URL(prodid_path)
    savepath = saveroot / prodid_path.name
    print("Downloading\n", url.url, 'to\n', savepath)
    try:
        urlretrieve(url.url, str(savepath))
    except HTTPError as e:
        print(e)
    return savepath
