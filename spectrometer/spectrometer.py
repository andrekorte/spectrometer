# -*- coding: utf-8 -*-
import serial
import sys
from detector import Detector
from source import Source


class Spectrometer(object):
    '''This class represents the whole spectrometer.

    It bundles the detector and source in one object.

    :params detector: the selected detector (0 - builtin, default)
    :type detector: int
    :params source: the selected light source ('blue' is default)
    :type source: str

    '''

    def __init__(self, **kwargs):
        self.init_components(**kwargs)

    def init_components(self, **kwargs):
        print('Setting up spectrometer')

        source = kwargs.get('source', 'blue')
        detector = kwargs.get('detector', 0)
        assert isinstance(source, str)
        assert isinstance(detector, int)

        self.source = Source(source)
        self.detector = Detector(detector)

    def measure(self, num_frames, num_dropped_frames, kind, **kwargs):
        '''Executes a measurment.

        :params num_frames: number of captured frames
        :type num_frames: int
        :params num_dropped_frames: number of frames to drop before collecting spectrum frames
        :type num_dropped_frames: int
        :params kind: The type of measurment. Choices are: 'background', 'spectrum', 'stream'
        :type kind: str

        '''
        if kind == 'spectrum':
            #self.source_on()
            self.detector.measure_spectrum(num_frames, num_dropped_frames, **kwargs)
            #self.source_off()
        elif kind == 'background':
            #self.source_on()
            self.detector.measure_background(num_frames, num_dropped_frames, **kwargs)
            #self.source_off()
        elif kind == 'stream':
            #self.source_on()
            self.detector.stream()
            #self.source_off()
        else:
            sys.exit('Measurment type unknow.')


if __name__ == '__main__':
    spectrometer = Spectrometer()
    spectrometer.measure(10, 10, kind='background', name='backgroundtest')
    spectrometer.measure(25, 10, kind='spectrum', name='spectrumtest')
