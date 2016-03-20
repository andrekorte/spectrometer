# -*- coding: utf-8 -*-
'''
TODO: Make a satisfying save method. Using jpgs loses spectral depth.
Pickling creates huge (up to 50MB) files.

'''
import copy
import cv2
import matplotlib.pyplot as plt
import numpy as np
import os.path
import pickle


class Spectrum(object):
    '''This class provides a way to hold and manipulate spectral data.

    When spectrum is read from an image file there is no way to determine
    num_frames and the data value range is restricted to 8 bit unsigned int.
    Although, the data array ist typecasted to 64 bit signed int.
    This is done to easily perform arithmetics on the data.

    However, a spectrum recorded with the detector module can fully utilize
    the 64 bit range and also populates the num_frames attribute.
    It is therefore preffered to process a spectrum immediatly
    and use the image file only when in a pinch.

    A satisfying method to save the numpy array with it's full 64 bit range is
    not yet implemented.

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

    def write(self, filename):
        '''Writes spectrum data to file.

        This function writes a .jpg image to file.

        :params filename: The filename
        :type filename: str
        :params data: The image data
        :type data: numpy.ndarry
        :returns: None
        :raises: AssertionError

        '''
        assert isinstance(filename, str)

        extension = 'jpg'
        filename = '.'.join([filename, extension])
        cv2.imwrite(filename, self.data)

        print('Output written to file: {}'.format(filename))

    def read(self, filename):
        '''Reads an image from disk.

        :params filename: The input file.
        :type filename: str
        :returns: None
        :raises: AssertionError

        '''
        assert os.path.isfile(filename)

        image_data = cv2.imread(filename)
        # Cast array to int64.
        # Then we can do arithmetic.
        image_data = np.cast['int64'](image_data)

        self.add_data(image_data)

    def dump(self, filename):
        '''Dumps spectral data to file.

        Uses th pickle module to save data array.

        :params filename: The pickle filename.
        :type filename: str
        :returns: None
        :raises: AssertionError

        '''
        assert isinstance(filename, str)

        with open(filename, 'wb') as outf:
            pickle.dump(self.data, outf)

        print('Spectrum dumped to file: {}'.format(filename))

    def load(self, filename):
        '''Unpickles data from pickle file.

        :params filename: The pickle filename.
        :type filename: str
        :returns: None
        :raises: AssertionError

        '''
        assert os.path.isfile(filename)

        with open(filename, 'rb') as outf:
            self.data = pickle.load(outf)

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

if __name__ == '__main__':
    s = Spectrum()
    s.read('spectrum.jpg')
    s.dump('spectrumtest.pk')
