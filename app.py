'''Main module that starts a socket server and creates new clients for each client that connects'''
import os
import sys
import socket
from datetime import datetime
from client import Client
from log import Logger

TCP_IP = '127.0.0.1'
TCP_PORT = int(os.environ.get('PORT', 8080))
BUFFER_SIZE = 2048

def start():
    '''Starts listening'''
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.bind((TCP_IP, TCP_PORT))
    soc.listen(1)
    print('Server listening')

    log = Logger()

    while 1:
        try:
            conn, addr = soc.accept()
            print('Connection to:', addr)
            log[addr] = datetime.now()

            Client(conn, addr)
        except KeyboardInterrupt:
            print('Shutting down...')
            try:
                soc.close()
                sys.exit(0)
            except SystemExit:
                os._exit(0) # pylint: disable=W0212
    conn.close()
