#!/usr/bin/env python
import pygame
from pygame.locals import *
import display
import threading
import queue
import time
from bleak import BleakScanner
import asyncio
import struct
from math import *

class BLE_async():

    def __init__(self):
        self._devices = None
        self._done = True
        self._last_shot_number = -1

    async def _scan(self):
        self._devices = await BleakScanner.discover(2.0, return_adv=True)

    def _digiball_parser(self, devices):
        for device in devices:
            d = devices[device][1]
            rssi = d.rssi
            manuf = d.manufacturer_data
            for manuf_id in manuf:
                if manuf_id == 0x03DE: #NRLLC
                    mdata = manuf[manuf_id]

                    data_ready = (int(mdata[17]) >> 6) == 1;
                    shot_number = int(mdata[6]) & 0x3F

                    if data_ready:
                        data = {}
                        data["Charging"] = int(mdata[7])>>6
                        data["Gyro Clipping"] = (int(mdata[6])>>7)==1
                        data["Motionless"] = (int(mdata[7]) & 0x03) + int(mdata[8])
                        data["Shot Number"] = shot_number
                        data["Tip Percent"] = int(mdata[11])
                        speed_factor = int(mdata[12])
                        spin_horz_dps = struct.unpack('>h', mdata[13:15])[0]
                        spin_vert_dps = struct.unpack('>h', mdata[15:17])[0]
                        spin_mag_rpm = sqrt(spin_horz_dps ** 2 + spin_vert_dps ** 2) / 6
                        data["Speed MPH"] = 0.06 * speed_factor
                        spin_degrees = 180 / pi * atan2(spin_horz_dps, spin_vert_dps)
                        data["Spin RPM"] = spin_mag_rpm
                        data["Tip Angle"] = spin_degrees

                        return data
        return None


    def async_task(self,q):
        try:
            asyncio.run(self._scan())
            q.put(self._digiball_parser(self._devices))
        except:
            pass

def gui_main():

    ble = BLE_async()
    q = queue.Queue()

    thread = threading.Thread(target=ble.async_task, args=(q,))
    thread.start()

    # initialize pygame
    pygame.init()
    pygame.font.init()

    scaffold = display.Scaffold()

    # Variable to keep our game loop running
    gameOn = True

    # Our game loo
    i = 0
    while gameOn:
        # for loop through the event queue
        for event in pygame.event.get():

            # Check for KEYDOWN event
            if event.type == KEYDOWN:

                if event.key == K_BACKSPACE:
                    gameOn = False

            # Check for QUIT event
            elif event.type == QUIT:
                gameOn = False

            # Check for window resize
            elif event.type == VIDEORESIZE:
                scaffold.update_size(event.w, event.h)


        if not q.empty():
            digiball_data = q.get()
            if digiball_data is not None:

                # Update display information. Needs MAC filtering
                scaffold.update_data(digiball_data)


            thread = threading.Thread(target=ble.async_task, args=(q,))
            thread.start()

        scaffold.draw()
        pygame.display.flip()


if __name__ == '__main__':

    gui_main()

