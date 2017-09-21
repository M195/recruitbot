'''Module to deal with new clients'''
import csv
import os
import logging
from threading import Thread
from datetime import datetime

class Client(Thread):
    '''A class that handles new client connections, handling them on a new thread'''
    __id = 0

    def __init__(self, sock, addr):
        logging.info('New client connected (%s:%s) with id %s', addr[0], addr[1], Client.__id)
        logging.debug('Creating new thread')

        Thread.__init__(self)
        logging.debug('Thread created')

        self.__id = Client.__id
        Client.__id += 1

        self.sock = sock
        self.addr = addr
        self.data = {}
        self.buffer_size = 1024

        self.start()
        logging.debug('Thread started')

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
        except Exception as error: # pylint: disable=W0703
            self.send_message('Sorry, an error occurred')
            logging.error(error)

        self.sock.close()
        logging.debug('Closed client#%s', self.__id)

    def get_input(self):
        '''Get data from the socket, decoding it and stripping whitespace'''
        user_input = self.sock.recv(self.buffer_size).decode().strip()
        logging.debug('Message `%s` received from client#%s', user_input, self.__id)
        return user_input

    def get_all_data(self, questions):
        '''Batch call self.get_input for each question in the list'''
        for question in questions:
            self.get_data(question[0], question[1], question[2])

    def get_data(self, msg, data_name, question_type='string', required=True):
        '''Get data by asking a question and adding the result to self.data'''
        self.send_message(msg)
        user_input = self.get_input()
        while required and user_input == '':
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
        logging.debug('Sent message `%s` to client#%s', msg, self.__id)

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
            logging.debug('Data from client#%s saved to %s', self.__id, filename)
