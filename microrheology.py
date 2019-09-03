from ParticleTracking import dataframes
from Generic.filedialogs import load_filename
import trackpy as tp
import pandas as pd
import numpy as np

class MicroRheology:

    def __init__(self, filename=None, mpp=1, fps=30.0, max_lag=100):
        if filename is None:
            filename = load_filename(file_filter='*.hdf5')
        self.filename=filename
        self.data=dataframes.DataStore(filename)
        self.df = self.data.df
        self.df_subset = self.df.copy()

        self.mpp = mpp
        self.fps = fps
        self.max_lag = max_lag


    def subtract_mean_drift(self):
        print('Subtracting mean drift')
        self.df.index.name = 'None'
        self.df['frame'] = self.df.index
        self.df_subset.index.name = None
        self.df_subset['frame']=self.df_subset.index
        drift = tp.motion.compute_drift(self.df_subset)
        corrected_traj = tp.motion.subtract_drift(
            self.df[['frame', 'x', 'y', 'particle']].copy(), drift)
        
        self.df['x old'] = self.df['x'].copy()
        self.df['y old'] = self.df['y'].copy()
        self.df = self.df.drop(columns=['x', 'y'])
        corrected_traj.index.name = None
        self.df = pd.merge(self.df, corrected_traj,
                      on=['particle', 'frame'])
        self.df.set_index('frame', drop=True, inplace=True)
        self.df.sort_values(by=['frame', 'particle'], inplace=True)
        num_particles = np.size(self.df_subset['particle'].unique())
        print('This is based on %d particles', num_particles)



    def plot_tracks(self):
        if 'frame' not in self.df.columns:
            self.df['frame'] = self.df.index
        tp.plot_traj(self.df)

    def plot_msd(self):
        pass

    def save_modified_df(self):
        filename_op = self.filename[:-5] + '_mod.hdf5'
        self.data.df = self.df
        self.data.save(filename=filename_op)

    def select_subset(self, classifier=None):
        if classifier is None:
            self.df_subset = self.df.copy()
        self.df_subset = self.df[self.df['classifier'] == classifier].copy()
        return self.df.subset

    def calc_imsd(self, classifier=None):
        pass


if __name__ == '__main__':
    filename = '/media/ppzmis/data/ActiveMatter/Microscopy/190820bacteriaand500nmparticles/videos/joined/StreamDIC003.hdf5'
    mr = MicroRheology(filename=filename)
    #mr.plot_tracks()
    mr.subtract_mean_drift()
    #mr.plot_tracks()
    #mr.save_modified_df()