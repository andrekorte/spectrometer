# -*- coding: utf-8 -*-
'''
TODO: Make a satisfying save method. Using jpgs loses spectral depth.
Pickling creates huge (up to 100MB) files.

'''
import copy
import cv2
import matplotlib.pyplot as plt
import numpy as np
import os.path
import pickle
import sys


class Spectrum(object):
    '''This class provides a way to hold and manipulate spectral data.

    When spectrum data is read from an image file there is no way to determine
    num_frames and the data value range is restricted to image format limits.

    However, a spectrum recorded with the detector module can fully utilize
    the 64 bit range and also populates the num_frames attributes.
    It is therefore preffered to process a spectrum immediatly
    and use the image file only when in a pinch.

    A satisfying method to save the numpy array is not yet implemented.

    '''
    def __init__(self, **kwargs):
        '''Initializes a spectrum opbject.

        :params data: The spectral data.
        :type data: numpy.ndarray
        :params num_frames: The number of collected frames (-1 if not set).
        :type num_frames: int
        :params original: A backup copy of the spectral data
        :type original: numpy.ndarray
        :params kind: The spectrum kind (i.e. background, spectrum, ...)
        :type kind: str
        :params name: The spectrum's name
        :type name: str

        '''
        self.data = None
        self.original = None
        self.num_frames = -1  # The number of summed frames
        self.kind = kwargs.get('kind', None)  # One of spectrum, background, ...
        self.name = kwargs.get('name', None)
        self.modified = False  # Track if the original data was modified

    def add_data(self, data):
        '''Sets the data and original data.

        Convinience function for setting data and the data backup copy at once.

        :params data: The spectral data
        :returns: None
        :raises: AssertionError

        '''
        assert isinstance(data, np.ndarray)

        self.data = data
        self.original = copy.deepcopy(data)

    def load(self, filename):
        '''Loads the spectrum data.
        
        Possible input files are pickle files, saved numpy arrays
        or images files (jpg or png).

        :params filename: The pickle filename.
        :type filename: str
        :returns: None
        :raises: AssertionError, pickle.UnpicklingError

        '''
        
        assert os.path.isfile(filename)

        name, ext = os.path.splitext(filename)
        
        if ext == '.pk':
            with open(filename, 'rb') as outf:
                data = pickle.load(outf)
        elif not ext or ext == '.npy':
            data = np.load(filename)
        elif ext in ['.jpg', '.png']:
            data = cv2.imread(filename)
        else:
            sys.exit('Unknown file format')

        self.add_data(data)

    def save(self, filename):
        '''Saves the spectrum data to file.
        
        The file format is based on the extension.
        If no extension is given a .npy file is written.
        
        :params filename: The output filename.
        :type filename: str
        :returns: None
        :raises: AssertionError
        
        '''
        assert isinstance(filename, str)
        
        name, ext = os.path.splitext(filename)
        
        if not ext or ext == '.npy':
            np.save(filename, self.data)
        elif ext == '.pk':
            with open(filename, 'wb') as outf:
                pickle.dump(self.data, outf)
        elif ext in ['.jpg', '.png']:
            cv2.imwrite(filename, self.data)

    def show_raw(self):
        '''Shows the raw image data.
        
        '''
        data = self.data.astype('uint8')
        cv2.namedWindow('raw')
        cv2.imshow('raw', data)

        k = cv2.waitKey(-1) & 0xFF
        if k == ord('q'):
            cv2.destroyWindow('raw')

    def process(self, threshold):
        '''Calculates the spectrum.

        At the moment the passed array is converted to grayscale and masked
        with the value of threshold.
        Returned spectra are not calibrated.
        At the moment the roi is hard coded.

        Steps that should be implemented:
            0. color space and resolution? 8bit? 10bit?
            1. Subtract dark current and adc noise
            2. Correct flat field and pixel defects
            3. Subtract background
            4. Normalise
            5. Calibrate

        :params threshold: Value to mask the array with
        :type threshold: int
        :returns: None

        '''
        assert isinstance(threshold, int), 'Threshold must be of type int.'

        roi = self.data
#        roi = self.data[300:500, 1000:]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
#        gray = self.data
        self.spectrum2d = np.where(gray >= threshold, gray, 0)
        self.spectrum1d = np.sum(self.spectrum2d, axis=0)
        self.threshold = threshold

    def show(self):
        '''Plots the processed spectra.

        TODO: Axis labels are not displayed

        '''
        assert hasattr(self, 'spectrum1d'), 'Data must be processed before plotting.'
        assert hasattr(self, 'spectrum2d'), 'Data must be processed before plotting.'
        assert hasattr(self, 'threshold'), 'Data must be processed before plotting.'

        from matplotlib import gridspec
        fig = plt.figure()
        grid = gridspec.GridSpec(2, 1, height_ratios=[1, 1])

        ax0 = fig.add_subplot(grid[0])
        ax0.imshow(self.spectrum2d)
        ax0.xaxis.set_ticks_position('none')
        ax0.xaxis.set_label('Pixel')
        ax0.yaxis.set_ticks_position('none')
        ax0.set_title('masked spectrum | threshold={0}'.format(self.threshold))

        ax1 = fig.add_subplot(grid[1], sharex=ax0)
        ax1.plot(self.spectrum1d)
        ax1.yaxis.set_label('Count')
        ax1.xaxis.set_ticks_position('none')
        ax1.yaxis.set_ticks_position('none')
        ax1.set_title('Spectrum')

        plt.tight_layout()
        plt.show()

    def subtract(self, other):
        '''Subtract a spectrum or value.

        :params other: The spectrum or value to subtract
        :type other: Either int or spectrum.Spectrum
        :returns: None
        :raises: AssertionError

        '''
        if isinstance(other, Spectrum):
            assert self.num_frames == other.num_frames, 'Both spectra must have same frame numbers.'
            assert self.data.shape == other.data.shape, 'Data must be of same length.'

            self.data = self.data - other.data
        else:
            assert isinstance(other, (int, float))
            self.data = self.data - other
            
        self.modified = True

    def normalize(self):
        pass

    def average(self):
        '''Averages the spectrum data.

        Averaging is done by dividing the data array by num_frames.
        Raises an AssertionError when num_frames is not set (i.e. -1).

        :returns: None
        :raises: AssertionError

        '''
        assert self.num_frames is not -1, 'num_frames not set.'
        assert hasattr(self, 'data')

        self.data = self.data / self.num_frames
        self.modified = True


def write(spec, filename=None):
    '''Writes the spectrum object to file.
    
    '''
    if not filename:
        filename = spec.name + '.pks'
    with open(filename, 'wb') as outf:
        pickle.dump(spec, outf, pickle.HIGHEST_PROTOCOL)

    print('Wrote spectrum file: {}'.format(filename))

def load(filename):
    '''Loads the pickled spectrum object from file.
    
    '''
    with open(filename, 'rb') as inf:
         spec = pickle.load(inf)
    return spec

if __name__ == '__main__':
    from detector import Detector
    d = Detector()
    b = d.measure_background(1, 1, kind='background', name='test')
    s = d.measure_spectrum(10, 1, kind='spectrum', name='test')
    s.process(10)
    #write(s)
    s.show()
    #s.show_raw()
