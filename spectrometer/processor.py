# -*- coding: utf-8 -*-
'''
At the moment processing only works with jpg images.

TODO: Make processing module work with 64 bit numpy arrays.

'''
import cv2
import matplotlib.pyplot as plt
import numpy as np
import os.path
import pickle


class Processor(object):
    def __init__(self):
        pass

    def load_image(self, filename):
        '''Loads the image file.

        :params filename: The image file
        :type filename: str
        :returns: None

        '''
        assert os.path.isfile(filename)

        self.data = cv2.imread(filename)

    def show_image(self):
        '''Displays the image data.

        :raises: AssertionError

        '''
        assert hasattr(self, 'data'), 'No data found.'

        rgb = cv2.cvtColor(self.data, cv2.COLOR_BGR2RGB)
        plt.imshow(rgb)
        plt.show()

    def load(self, filename):
        '''Unpickles data from pickle file.

        :params filename: The pickle filename.
        :type filename: str
        :returns: None
        :raises: AssertionError, pickle.UnpicklingError

        '''
        assert os.path.isfile(filename)

        with open(filename, 'rb') as outf:
            self.data = pickle.load(outf)

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
        assert hasattr(self, 'data'), 'Data not found.'

        roi = self.data[300:500, 1000:]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        self.spectrum2d = np.where(gray >= threshold, gray, 0)
        self.spectrum1d = np.sum(self.spectrum2d, axis=0)
        self.threshold = threshold

    def show_result(self):
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

    def write(self, filename):
        '''Writes the processed 1d spectrum to a text file.

        The format is specified by the filename extension.
        Currently supported formats are:
            - csv: Writes a file with values seperated by comma.
            - xy: Write a file with values seperated by two spaces.
            - dat: Same as xy.

        :params filename: Name of file
        :type filename: str
        :returns: None

        '''
        assert hasattr(self, 'spectrum1d'), 'One dimensional data not found.'
        assert isinstance(filename, str), 'Incorrect filename.'

        ext = filename.split('.')[-1]
        if ext == 'csv':
            header = '"Pixel", "Value"\n'
            seperator = ','
        elif ext in ['xy', 'dat']:
            header = '# x  y\n'
            seperator = '  '
        else:
            string = 'WARNING: Unknown file format: .{}. No output written.'.format(ext)
            print('\033[93m' + string + '\033[0m')
            return

        with open(filename, 'w') as outf:
            outf.write(header)
            for pixel, value in enumerate(self.spectrum1d):
                outf.write('{}{}{}\n'.format(pixel, seperator, value))

        print('Output written to file: {}'.format(filename))


if __name__ == '__main__':
    p = Processor()
    p.load_image('spectrum.jpg')
    #p.show_image()
    p.process(10)
    p.show_result()
    p.write('test.csv')
    p.write('test.xy')
    p.write('test.dat')
    p.write('test.abc')
