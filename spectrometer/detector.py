# -*- coding: utf-8 -*-
import cv2
import numpy as np
import os.path
import sys

from spectrum import Spectrum
from source import Source


class Detector(object):
    '''Actually, this class is a webcam.

    :params device: the X in /dev/videoX
    :type device: int
    :params cap: opencv video capture
    :type cap: cv2.VideoCapture
    :params width: video capture frame width
    :type width: int
    :params height: video capture frame height
    :type height: int

    '''

    def __init__(self, device=None):
        if device:
            self.device = device
        else:
            self.device = self._find_video_device()
        self.cap = cv2.VideoCapture(self.device)
        self.width = self.cap.get(3)
        self.height = self.cap.get(4)

    def measure_background(self, num_frames, num_dropped_frames, **kwargs):
        '''Measures and returns the background and writes an image file to disk.

        :params num_frames: number of captured frames
        :type num_frames: int
        :params num_dropped_frames: number of dropped frames before collecting background spectrum
        :type num_dropped_frames: int
        :params show: If true show last grabbed frame
        :type show: bool
        :params name: The spectrum name
        :type name: str
        :returns: background_avg (ndarry): the averaged background spectrum

        '''
        show = kwargs.get('show', False)
        name = kwargs.get('name')
        assert isinstance(show, bool), 'show must be of type bool.'
        assert isinstance(name, str), 'name must be of type str.'

        background = Spectrum(kind='background', name=name)
        background.add_data(self._measure(num_frames, num_dropped_frames, kind='background', show=show))
        background.num_frames = num_frames
        return background

    def measure_spectrum(self, num_frames, num_dropped_frames, **kwargs):
        '''Measures a spectrum.

        :params num_frames: number of captured frames
        :type num_frames: int
        :params num_dropped_frames: number of frames to drop before collecting spectrum frames
        :type num_dropped_frames: int
        :params show: If true show last grabbed frame
        :type show: bool
        :params name: The spectrum name
        :type name: str
        :returns: spectrum_avg (ndarry): the averaged spectrum
        :raises: AssertionError

        '''
        show = kwargs.get('show', False)
        name = kwargs.get('name', None)
        assert isinstance(show, bool), 'show must be of type bool.'
        assert isinstance(name, str), 'name must be of type str.'

        spectrum = Spectrum(kind='spectrum', name=name)
        spectrum.add_data(self._measure(num_frames, num_dropped_frames, kind='spectrum', show=show))
        spectrum.num_frames = num_frames
        return spectrum

    def stream(self):
        '''Provides a stream from the detector.

        '''
        cv2.namedWindow('stream')

        while True:
            ret, frame = self.cap.read()
            cv2.imshow('stream', frame)

            k = cv2.waitKey(1) & 0xFF
            if k == ord('q'):
                self.cap.release()
                cv2.destroyWindow('stream')
                break

    def _measure(self, num_frames, num_dropped_frames, kind, show):
        '''Records a spectrum.

        Used to carry out the background and spectrum measurments.

        :params num_frames: number of captured frames
        :type num_frames: int
        :params num_dropped_frames: number of frames to drop before collecting spectrum frames
        :type num_dropped_frames: int
        :params show: If true show last grabbed frame
        :type show: bool
        :returns: data (ndarry): the collected data
        :raises: AssertionError

        '''
        assert isinstance(num_frames, int), 'num_frames must be of type int.'
        assert isinstance(num_dropped_frames, int), 'num_dropped_frames must be of type int.'
        assert isinstance(show, bool), 'show must be of type bool.'
        assert isinstance(kind, str), 'kind must be of type str.'

        if show is True:
            cv2.namedWindow(kind)
            cv2.namedWindow('frame')

#        data = np.ndarray(shape=(self.height, self.width, 3), dtype=np.int64)
#        data = np.ndarray(shape=(self.height, self.width), dtype=np.uint16)
        data = np.ndarray(shape=(self.height, self.width, 3), dtype=np.float32)

        if not self.cap.isOpened():
            self.cap.open(0)
        print('\033[1m' + 'Measuring {}'.format(kind) + '\033[0m')
        print('Dropping first {} frames'.format(num_dropped_frames))
        if show is True:
            print('Press q to abort.')
        for i in range(num_dropped_frames):
            ret, dropped = self.cap.read()

        for i in range(num_frames):
            print('Capturing frame {}\r'.format(i), end='')
            ret, frame = self.cap.read()
            data += frame

            if show is True:
                cv2.imshow('frame', frame)
                cv2.imshow(kind, data)

                k = cv2.waitKey(1) & 0xFF
                if k == ord('q'):
                    self.cap.release()
                    cv2.destroyWindow(kind)
                    break
        return data

    def _find_video_device(self):
        if os.path.exists('/dev/video0'):
            return 0
        elif os.path.exists('/dev/video1'):
            return 1
        return None


if __name__ == '__main__':
    d = Detector()
    #s = Source()
    background = d.measure_background(10, 10, name='backgroundtest')
    spectrum = d.measure_spectrum(128, 10, name='spectrumtest_gray')
