
import matplotlib.pyplot as plt
import pandas as pd
import pvl

from .downloads import hirise_dropbox


def get_rdr_index_names():
    lblfile = hirise_dropbox() / 'RDRCUMINDEX.LBL'
    label = pvl.load(lblfile)
    table = label['RDR_INDEX_TABLE']
    names = []
    for item in table:
        second = item[1]
        if isinstance(second, pvl.PVLObject):
            names.append(second['NAME'])
    return names


def get_rdr_index():
    names = get_rdr_index_names()
    indexfile = hirise_dropbox() / 'RDRCUMINDEX.TAB'
    df = pd.read_csv(indexfile, names=names)
    return df


class PolyPlotter(object):
    """For plotting the outline of HiRISE RDR polygons.
    """
    # note, that last point needs to repeat 1 point to close polygon
    lat_indices = ['CORNER1_LATITUDE',
                   'CORNER2_LATITUDE',
                   'CORNER3_LATITUDE',
                   'CORNER4_LATITUDE',
                   'CORNER1_LATITUDE']
    lon_indices = ['CORNER1_LONGITUDE',
                   'CORNER2_LONGITUDE',
                   'CORNER3_LONGITUDE',
                   'CORNER4_LONGITUDE',
                   'CORNER1_LONGITUDE']

    def __init__(self):
        self.df = get_rdr_index()
        self.df.set_index('PRODUCT_ID', inplace=True)

        print("Loaded RDR index file.")

    def plot_prodid(self, product_id, ax=None, **kwargs):
        if ax is None:
            _, ax = plt.subplots()
        ax.plot(self.df.loc[product_id][self.lon_indices],
                self.df.loc[product_id][self.lat_indices], **kwargs)
