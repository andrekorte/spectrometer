from detector import Detector
from spectrum import Spectrum, write, load
from processor import Processor

d = Detector(0)
p = Processor()

b = d.measure_background(1, 10, kind='background', name='background')
write(b)
b.show()

s = d.measure_spectrum(1, 10, kind='background2', name='background2')
write(s)
s.show()

s.subtract(b)
write(s)
s.show()

p.load('spectrum.npy')
p.process(10)
p.write('spectrum.csv')
p.show()


#import os
#import time

#from spectrometer import Spectrometer


#def experiment_from_file(filename):
#    pass

#class Experiment(object):
#    def __init__(self):
#        self.settings = {}
#        self.created = time.localtime()
#        self.settings['created'] = time.asctime(self.created)
#        self.spectra = []
#        self.spectrometer = None

#    def setup(self):
#        self._make_dirs()
#        self._set_file_prefix()
#        self._set_num_frames()

#        self.spectrometer = Spectrometer()

#        for k, v in self.settings.items():
#            self.write_setting(k, v)

#    def _make_dirs(self):
#        current_dir = os.getcwd()
#        path_created = False

#        while not path_created:
#            name = input('Experiment name: ')
#            path = os.path.join(current_dir, name)
#            if os.path.exists(path):
#                print('Experiment exists on path!\nPlease choose different name.')
#            else:
#                spectra_path = os.path.join(path, 'spectra')
#                os.mkdir(path)
#                os.mkdir(spectra_path)
#                self.name = name
#                self.path = path
#                path_created = True

#        self.settings['path'] = self.path
#        self.settings['name'] = self.name

#    def _set_file_prefix(self):
#        prefix = input('Enter file prefix [{}]:'.format(self.name))
#        if not prefix:
#            self.prefix = self.name
#        else:
#            self.prefix = prefix

#        self.settings['prefix'] = self.prefix

#    def _set_num_frames(self):
#        num_frames_set = False
#        num_dropped_frames_set = False
#        while not num_frames_set:
#            num_frames = input('Enter number of frames to collect: ')
#            if isinstance(int(num_frames), int):
#                self.num_frames = num_frames
#                num_frames_set = True
#        while not num_dropped_frames_set:
#            num_dropped_frames = input('Enter number of frames to drop: ')
#            if isinstance(int(num_dropped_frames), int):
#                self.num_dropped_frames = num_dropped_frames
#                num_dropped_frames_set = True

#        self.settings['num_frames'] = self.num_frames
#        self.settings['num_dropped_frames'] = self.num_dropped_frames

#    def write_setting(self, parameter, value):
#        filename = os.path.join(self.path, 'settings.py')
#        with open(filename, 'a') as outf:
#            outf.write('{} : {}\n'.format(parameter, value))

#    def run(self):
#        pass

#if __name__ == '__main__':
#    ex = Experiment()
#    ex.setup()
