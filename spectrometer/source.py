# -*- coding: utf-8 -*-
'''
For this module to work an arduino needs to be connected over serial.

The code running on the arduino should look something like this:

    void setup() {
      Serial.begin(115200);
      pinMode(13, OUTPUT); // blue led
    }

    void loop() {
      if (Serial.available()) {
        char c = (char)Serial.read();
        if (c == '0') {
          digitalWrite(13, LOW);
        } else if (c == '1') {
          digitalWrite(13, HIGH);
        } else {
          Serial.println('Unknown command');
        }
      }
    }

'''
import os.path
import sys
import serial


class Source(object):
    '''This class represents the light sources of a spectrometer.

    To toggle the light source a byte is send over serial.
    This code needs to be modified if you want to use more than one light source.

    '''

    def __init__(self, emitter='blue', device=None):
        '''
        :params emitter: The name of the selected light source
        :type source: str
        :params device: The serial device
        :type device: str

        '''
        # {led color : arduino pin}
        color_pin = {'blue': 13}
        if emitter in color_pin:
            self.pin = color_pin[emitter]
            self.emitter = emitter
        else:
            sys.exit('Missing source')

        if device:
            self.device = device
        else:
            self.device = self._find_device()
        self._connect()

    def _connect(self):
        '''Establishes the serial connection.

        '''
        if self.device:
            self.connection = serial.Serial(self.device)
        else:
            print('\033[93m' + 'WARNING: No serial device selected.' + '\033[0m')

    def _find_device(self):
        '''Searches for serial devices.

        '''
        if os.path.exists('/dev/ttyACM0'):
            self.device = '/dev/ttyACM0'
        elif os.path.exists('/dev/ttyACM1'):
            self.device = '/dev/ttyACM1'

    def on(self):
        '''Turns the light source on.

        '''
        self.connection.write(b'1')

    def off(self):
        '''Turns the light source off.

        '''
        self.connection.write(b'0')

    def brightness(self, val):
        '''Set source brightness to val.

        Val is a 10-bit value which is send to the arduino
        '''
        if val >= 0 and val <= 1023:
            self.conection.write(b'val')


if __name__ == '__main__':
    import time
    s = Source()
    #s.on()
    #time.sleep(5)
    #s.off()
