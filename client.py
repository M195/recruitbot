'''Module to deal with new clients'''
import socket
import csv
import os
from threading import Thread
from datetime import datetime

class Client(Thread):
    '''A class that handles new client connections, handling them on a new thread'''

    def __init__(self, sock, addr):
        Thread.__init__(self)
        self.sock = sock
        self.addr = addr
        self.data = {}
        self.buffer_size = 1024

        self.start()

    def run(self):
        try:
            self.get_all_data([
                ['What is your name?', 'name', 'string'],
                ['How old are you?', 'age', 'int'],
                ['What education do you have?', 'education', 'string'],
                ['What are your hobbies? (seperate with commas)', 'hobbies', 'list'],
                ['What is your favourite flavour of ice cream?', 'icecream', 'string']
            ])
            self.data['time'] = datetime.now().strftime('%b %d, %Y, %I:%M%p')

            self.send_message('Thank you!\n\n', )
            self.save_data()
        except Exception: # pylint: disable=W0703
            self.send_message('Sorry, an error occurred')

        self.sock.shutdown(socket.SHUT_RDWR)

    def get_input(self):
        '''Get data from the socket, decoding it and stripping whitespace'''
        return self.sock.recv(self.buffer_size).decode().strip()

    def get_all_data(self, questions):
        '''Batch call self.get_input for each question in the list'''
        for question in questions:
            self.get_data(question[0], question[1], question[2])

    def get_data(self, msg, data_name, question_type='string', required=True):
        '''Get data by asking a question and adding the result to self.data'''
        self.send_message(msg)
        user_input = self.get_input()
        while required == True and user_input == '':
            self.send_message('This question is required')
            user_input = self.get_input()

        if question_type == 'string':
            self.data[data_name] = user_input
        elif question_type == 'list':
            self.data[data_name] = user_input.split(',')
        elif question_type == 'int':
            try:
                self.data[data_name] = int(user_input)
            except ValueError:
                self.send_message('That\'s not a number!')
                self.get_data(msg, data_name, question_type)

    def send_message(self, msg):
        '''Send an encoded message through the socket'''
        self.sock.send(bytearray(msg + '\n', 'ascii'))

    def save_data(self, filename='interviews.csv'):
        '''Save self.data into a csv file'''
        file_exists = os.path.isfile(filename)

        with open(filename, 'a', newline='') as csvfile:
            fieldnames = list(self.data)
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect='excel')

            self.data['hobbies'] = ",".join(self.data['hobbies'])
            if not file_exists:
                writer.writeheader()
            writer.writerow(self.data)
