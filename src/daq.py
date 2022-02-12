import socket, json, sys, traceback
from threading import Thread
import random
import time

class DAQ(object):
    """ UDP Broadcast Packet Listener 
    Listens for Horuslib UDP broadcast packets, and passes them onto a callback function
    """

    def __init__(
        self,
        callback=None,
    ):

        self.callback = callback
       
        self.listener_thread = None
        self.udp_listener_running = False
        self.data = []

    def acquisition(self):
        """ Process a received UDP packet """
        try:
            if self.callback is not None:
                self.callback(self.data)

        except Exception as e:
            print("Could not parse packet: %s" % str(e))
            traceback.print_exc()

    def daq_thread(self):
        """ Listen for Broadcast UDP packets """

        print("Started UDP Listener Thread.")
        self.udp_listener_running = True

        while self.udp_listener_running:
            try:
                time.sleep(10)
                self.data = []
                for i in range(0,3):
                    self.data.append((random.randint(0, 360),random.randint(100, 25000) ))
                self.acquisition()
            except:
                traceback.print_exc()
        print("Closing UDP Listener")

    def start(self):
        if self.listener_thread is None:
            self.listener_thread = Thread(target=self.daq_thread)
            self.listener_thread.start()

    def close(self):
        self.udp_listener_running = False
        self.listener_thread.join()