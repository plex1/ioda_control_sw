import socket
import time

class GepinPhyTcp(object):

    def __init__(self, ip, port):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.settimeout(5.0)
            self.s.connect((ip, port))
        except:
            self.s = None
            print("Error: Could not connect to interface")
        self.debug = 0


    def write_list(self, wl):
        try:
            if self.debug>0:
                print("sent bytes: " + str(wl))
            self.s.send(bytearray(wl))
        except:
            print("Phy TCP, Write error")

    def read_list(self, len_requested):
        try:
            if self.debug > 0:
                print("length requested: "+ str(len_requested))
            recl = []
            timeout = time.time()+5 # 10 sec from now
            while len(recl) < len_requested:
                recl = recl + list(self.s.recv(len_requested-len(recl)))
                if time.time() > timeout:
                    break
        except Exception as e:
            if self.debug > 0:
                print("length received: " + str(recl))
            print("Phy tcp, read error: " + str(e))
        else:
            if self.debug > 0:
                print("received bytes: " + str(recl))
            return recl

    def clear_if(self):
        self.s.setblocking(0)
        try:
            while self.s.recv(1024):
                pass
        except:
            pass
        self.s.setblocking(1)


    def close_if(self):
        self.s.close()