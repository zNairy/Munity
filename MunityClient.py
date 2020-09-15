#!/usr/bin/python3
# coding: utf-8

__author__ = 'Nairy'
__version__ = '2.0'
__contact__ = '__Nairy__#7181 or https://www.github.com/zNairy'

import socket
from threading import Thread
from termcolor import colored
from os import system
from platform import uname
from sys import exit

class MunityClient(object):
    def __init__(self, host, port):
        self.Address = (host, port)
        self.client = None
        self.nick = None
        self.buffer = 1024
        self.clearCommand = None
        self.nameColor = 'white'
        self.Colors = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
    
    def Start(self):
        self.CheckSystemName()
        self.CreateSocket()
        self.main()

    def VerifyColor(self, color):
        for c in self.Colors:
            if(color.strip() == c):
                return True
        return False
    
    def ChangeNameColor(self, color):
        self.nameColor = color.strip()

    def CheckSystemName(self):
        if('win' in uname()[0].lower()):
            self.clearCommand = 'cls'
        elif('linux' in uname()[0].lower()):
            self.clearCommand = 'clear'
    
    def CheckBultinCommands(self, command):
        if(command.strip() == '/clear'):
            system(self.clearCommand)
            return True
        elif(command.strip()[:10] == '/namecolor'):
            if(command.strip()[11:] != ''):
                if(self.VerifyColor(command.strip()[11:])):
                    self.ChangeNameColor(command.strip()[11:])
                else:
                    print(colored('Color not exist or not found...', 'red'), colored(' Colors: {}'.format("".join(f'{c} - ' for c in self.Colors)), 'yellow'))
            else:
                print(colored('Please inform name of color to change...', 'red'))
            
            return True
        elif(command.strip() == '/exit'):
            exit(0)

        return False

    def CreateSocket(self):
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect(self.Address)
            self.nick = input('Nick: ')
            self.client.send(self.nick.encode())
            print(colored(self.client.recv(self.buffer).decode('utf-8'), 'green').center(50))
        except ConnectionRefusedError:
            print(colored('Connection refused...', 'red'))
            exit(1)

    def ListenServer(self):
        while True is not False:
            message = self.client.recv(self.buffer)
            if(not message):
                print(colored('Connection close...', 'red'))
                break
            else:
                print(message.decode('utf-8'))

    def main(self):
        thread = Thread(target=self.ListenServer);thread.daemon=True;thread.start()
        try:
            while True is not False:
                user_message = input(colored(f'[{self.nick}]: ', self.nameColor))
                if(len(user_message.strip()) != 0):
                    if(not self.CheckBultinCommands(user_message)):
                        self.client.send(user_message.encode())
        except KeyboardInterrupt:
            print()
            exit(0)

def main():
    chat = MunityClient('127.0.0.1', 5555)
    chat.Start()
    
if __name__ == '__main__':
    main()