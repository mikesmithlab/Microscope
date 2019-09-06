from ParticleTracking import dataframes
from Generic.filedialogs import load_filename
from Generic.fitting import Fit
import trackpy as tp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import gamma
from ParticleTracking.postprocessing import subtract_drift

class MicroRheology:

    def __init__(self, filename=None, mpp=1, fps=30.0, rad=None, max_lag=100,temp=293):
        '''

        :param filename: DataStore filename
        :param mpp: microns per pixel
        :param fps: frames per second of movie
        :param rad: radius of particles in microns
        :param max_lag: maximum lag time in seconds - NB this is different to trackpy which measures this in frames
        :param temp: temperature of experiment

        All output quantities such as emsd and creep are in microns and seconds.
        Creep in SI.

        '''
        if filename is None:
            filename = load_filename(file_filter='*.hdf5')
        self.filename=filename
        self.data=dataframes.DataStore(filename)
        self.df = self.data.df
        self.df_subset = self.df.copy()

        self.mpp = mpp
        self.fps = fps
        self.rad=rad
        self.max_lag = int(max_lag*fps)
        self.temp = temp

    def subtract_mean_drift(self):
        self.df=subtract_drift(self.df)

    def plot_tracks(self):
        if 'frame' not in self.df.columns:
            self.df['frame'] = self.df.index
        tp.plot_traj(self.df)



    def single_traj(self, particle_num):
        traj = self.df[self.df['particle'] == particle_num].copy()
        return traj

    
    def save_modified_df(self):
        filename_op = self.filename[:-5] + '_mod.hdf5'
        self.data.df = self.df
        self.data.save(filename=filename_op)

    def calc_imsd(self, classifier=None, stat='msd', show=False):
        #see http://soft-matter.github.io/trackpy/dev/generated/trackpy.motion.imsd.html
        self.select_subset(classifier=classifier)
        self.imsd = tp.motion.emsd(self.df_subset, self.mpp, self.fps,
                                   max_lagtime=self.max_lag)

    def calc_emsd(self, classifier=None, show=False):
        # see http://soft-matter.github.io/trackpy/dev/generated/trackpy.motion.emsd.html
        self.select_subset(classifier=classifier)
        self.emsd = tp.motion.emsd(self.df_subset, self.mpp, self.fps, max_lagtime=self.max_lag).to_frame()
        self.emsd['ln_t'] = np.log(self.emsd.index)
        self.emsd['ln_msd']=np.log(self.emsd['msd'])

        if show:
            self.plot_emsd()

    def calc_complex_mod(self):
        kB = 1.38E-23
        t = self.emsd.index.values
        msd = self.emsd['msd'].values
        fit_obj=Fit('axb', x=t, y=msd)
        fit_obj.add_params()
        fit_obj.fit(interpolation_factor=1)
        fit_obj.plot_fit()

        G = pd.DataFrame(index=fit_obj.fit_x)

        G['msd'] = fit_obj.fit_y
        G['J_t'] = G['msd'] * 1E-12 * 3 * np.pi * self.rad / (2 * kB * self.temp)

        a, b = fit_obj.fit_params

        G['ln_t'] = np.log(G.index)
        G['alpha_t'] = np.log(a*(G.index)**b)/G['ln_t']
        G['G*'] = (kB*self.temp)/(np.pi*self.rad*G['msd']*1E-12*gamma(1+G['alpha_t']))
        G['ln_G*'] = np.log(np.abs(G['G*']))
        G['omega'] = 1/G.index
        G['ln_omega'] = np.log(G['omega'])
        G['delta'] = (np.pi/2)*(np.gradient((G['ln_G*']),G['ln_omega']))
        G['G_storage'] = np.abs(G['G*'])*np.cos(G['delta'])
        G['G_loss'] = np.abs(G['G*'])*np.sin(G['delta'])

        plt.figure()
        plt.loglog(G['omega'],G['G_storage'],'rx')
        plt.loglog(G['omega'], G['G_loss'], 'bx')
        plt.show()




    def plot_emsd(self):

        print(self.emsd.index)
        plt.figure()
        plt.plot(np.log10(self.emsd.index),np.log10(self.emsd.values),'rx')
        plt.show()


if __name__ == '__main__':
    filename = '/media/ppzmis/data/ActiveMatter/Microscopy/190820bacteriaand500nmparticles/videos/joined/StreamDIC003.hdf5'
    mr = MicroRheology(filename=filename, mpp=0.1613, fps=(1/0.03), rad=500E-9, max_lag=10)
    #mr.plot_tracks()
    mr.subtract_mean_drift()
    mr.calc_emsd(show=False)
    mr.calc_complex_mod()

    #mr.plot_tracks()
    #mr.save_modified_df()