import pvl


class HiRISE_Label(object):

    def __init__(self, fname):
        self.label = pvl.load(str(fname))

    @property
    def binning(self):
        return self.label['INSTRUMENT_SETTING_PARAMETERS']['MRO:BINNING']

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
