'''Main module that starts a socket server and creates new clients for each client that connects'''
import os
import sys
import socket
import logging
from datetime import datetime
from client import Client

TCP_IP = '127.0.0.1'
TCP_PORT = int(os.environ.get('PORT', 8080))
BUFFER_SIZE = 2048

logging.basicConfig(level=logging.DEBUG)

def start():
    '''Starts listening'''
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.bind((TCP_IP, TCP_PORT))
    soc.listen(1)
    logging.info('Server listening on %s:%s', TCP_IP, TCP_PORT)

    while 1:
        try:
            conn, addr = soc.accept()
            logging.debug('Accepted connection from %s', addr)

            Client(conn, addr)
        except KeyboardInterrupt:
            logging.info('Shutting down...')
            try:
                soc.close()
                sys.exit(0)
            except SystemExit:
                logging.error('Error shutting down')
                os._exit(0) # pylint: disable=W0212
    conn.close()
