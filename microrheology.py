from ParticleTracking import dataframes
from Generic.filedialogs import load_filename


class MicroRheology:

    def __init__(self, filename=None):
        if filename is None:
            filename = load_filename(file_filter='*.hdf5')
        data=dataframes.DataStore(filename)
        self.df = data.df

    def subtract_mean_drift(self):
        pass

    def calc_msd(self):
        pass

