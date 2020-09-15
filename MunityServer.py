#!/usr/bin/python3
# coding: utf-8

__author__ = 'Nairy'
__version__ = '2.0'
__contact__ = '__Nairy__#7181 or https://www.github.com/znairy'

import socket
import time
from datetime import datetime
from threading import Thread
from termcolor import colored
from sys import exit

class MunityServer(object):
    ''' client side '''
    def __init__(self, host, port):
        date = datetime.today()
        self.Address = (host, port)
        self.server = None
        self.Allusers = []
        self.privateNameUsers = []
        self.privateUsers = []
        self.waitRoom = []
        self.buffer = 1024
        self.log = open(f'{date.year}-{date.month}-{date.day}.log', 'w')
        self.commands = [
            ('/commands', '\n  /version\n  /contact\n  /clear\n  /namecolor\n  /listusers\n  /private\n  /accept\n  /decline\n  /leave'),
            ('/version', '2.0'),
            ('/contact', '  Discord: __Nairy__#7181 or https://www.github.com/zNairy'),
            ('/clear', None),
            ('/namecolor', None),
            ('/listusers', None),
            ('/private', None),
            ('/accept', None),
            ('/decline', None),
            ('/leave', None),
            ('/invites', None)
        ]

    def Start(self):
        self.CreateSocket()
        self.main()

    def CreateSocket(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind(self.Address)
            self.server.listen(10)
        except Exception as err:
            print(colored(err, 'red'))
            exit(1)

    def NumOfInvites(self, conn):
        conn.send(str(len(self.OnWaitRoom(conn))).encode())

    def LeavePrivateRoom(self, conn):
        user = self.OnPrivateRoom(conn)
        if(user):
            user = user[0]
            for _user in user:
                _user.send(f'\n  [*] {self.CheckNickName(_user)}, seu parceiro acabou de te deixar...\n  Voltando ao chat geral...'.encode())
                self.privateNameUsers.remove(self.CheckNickName(_user))
            
            for _user in self.privateUsers:
                if(user == _user):
                    self.privateUsers.remove(user)
        else:
            conn.send('\n Vocẽ não está em uma sala privada...'.encode())
    
    def AddUser(self, conn, nick):
        self.Allusers.append((conn, nick))

    def OnPrivateRoom(self, conn):
        return [user for user in self.privateUsers if conn in user]

    def OnWaitRoom(self, conn):
        return [user for user in self.waitRoom if conn in user]

    def SendNotificationPrivate(self, users, conn):
        for _user in users:
            if(_user is not conn):
                _user.send(f'\n  [*] Você está no privado com {self.CheckNickName(conn)} agora!'.encode())
                conn.send(f'\n  [*] Você está no privado com {self.CheckNickName(_user)} agora!'.encode())

    def CheckInvite(self, conn, nickname, users):
        for invite in users:
            for _user in invite:
                if(_user is not conn and self.CheckNickName(_user) == nickname):
                    return invite

    def AddPrivateNameUsers(self, users):
        for _user in users:
            self.privateNameUsers.append(self.CheckNickName(_user))

    def Accept(self, conn, nickname):
        user = self.OnPrivateRoom(conn)
        if(not user):
            user = self.OnWaitRoom(conn)
            if(user):
                _user = self.CheckInvite(conn, nickname, user)
                if(_user):
                    self.AddPrivateNameUsers(_user)
                    self.SendNotificationPrivate(_user, conn)
                    self.privateUsers.append(_user)
                    self.waitRoom.remove(_user)
                else:
                    conn.send(f'\n  Você não tem invites de {nickname}'.encode())
            else:
                conn.send(f'\n  Você não tem pedidos para sala privada...'.encode())
        else:
            conn.send(f'\n  Você já está em uma conversa privada, use /leave para sair...'.encode())

    def Decline(self, conn, nickname):
        user = self.OnWaitRoom(conn)
        if(user):
            _user = self.CheckInvite(conn, nickname, user)
            if(_user):
                self.waitRoom.remove(_user)
            else:
                conn.send(f'\n  Você não tem invites de {nickname}'.encode())
        else:
            conn.send(f'\n Você não tem pedidos para sala privada...'.encode())

    def AddOnPrivate(self, nick, conn):
        user = self.OnPrivateRoom(conn)
        if(not user):
            user = self.CheckUser(nick)
            if(user):
                user = user[0]
                if(self.CheckNickName(conn) != user[1]):
                    user[0].send(f'\n Olá {nick}, o usuário {self.CheckNickName(conn)} quer se conectar com você!'.encode())
                    self.waitRoom.append((conn, user[0]))
                else:
                    conn.send(f' Você não pode mandar convite a sí mesmo...'.encode())
            else:
                conn.send(f' Usuario {nick} não está online...'.encode())
        else:
            conn.send(f'\n  Você já está em uma conversa privada, use /leave para sair...'.encode())

    def CheckNickName(self, connection):
        return [conn[1] for conn in self.Allusers if conn[0] == connection][0]
    
    def CheckUser(self, nick):
        return [user for user in self.Allusers if user[1] == nick]

    def SendCommand(self, cmd, conn):
        command = self.CommandAvailable(cmd.split(' ')[0])
        if(command):
            command = command[0]
            if(command[0] == '/listusers'):
                listofusers = '\n' + ''.join(f'{user[1]}\n' for user in self.Allusers)
                conn.send(listofusers.encode())
            elif(command[0] == '/private'):
                if(cmd[9:].strip() != ""):
                    self.AddOnPrivate(cmd[9:].strip(), conn)
                else:
                    conn.send('\n  Passe o nome do usuário como argumento:  /private nome_do_usuario'.encode())
            elif(command[0] == '/accept'):
                if(cmd[8:].strip() != ""):
                    self.Accept(conn, cmd[8:].strip())
                else:
                    conn.send(f'\n  Passe o nome do usuário como argumento:  /accept nome_do_usuario'.encode())
            elif(command[0] == '/decline'):
                if(cmd[9:].strip() != ""):
                    self.Decline(conn, cmd[9:].strip())
                else:
                    conn.send('\n  Passe o nome do usuário como argumento: /decline nome_do_usuario'.encode())
            elif(command[0] == '/leave'):
                self.LeavePrivateRoom(conn)
            elif(command[0] == '/invites'):
                self.NumOfInvites(conn)
            else:
                conn.send(f'  {command[1]}'.encode())
        else:
            conn.send(f'  Erro: comando {cmd} inválido ou inexistente...'.encode())

    def CommandAvailable(self, cmd):
        return [command for command in self.commands if cmd == command[0]]

    def RemoveConnection(self, apl):
        self.Allusers.remove([user for user in self.Allusers if user[1] == apl][0])
    
    def ListenUsers(self, conn, apl):
        while True is not False:
            user_message = conn.recv(self.buffer).decode('utf-8')
            if(not user_message):
                print(colored(f'  {apl} has left...', 'red'))
                if(self.OnPrivateRoom(conn)):
                    self.LeavePrivateRoom(conn)
                self.RemoveConnection(apl)
                break
            elif(user_message[0] == '/'):
                self.SendCommand(user_message, conn)    
            else:
                onprivate = self.OnPrivateRoom(conn)
                if(onprivate):
                    if(onprivate[0][0] != conn):
                        onprivate[0][0].send(user_message.encode())
                    else:
                        onprivate[0][1].send(user_message.encode())
                else:
                    self.WriteLog(user_message, apl)
                    for user in self.Allusers:
                        if(user[0] is not conn and user[1] not in self.privateNameUsers):
                            user[0].send(f'\n[{apl}]: {user_message}'.encode())

    def WriteLog(self, message, apl):
        hour = datetime.now()
        hour = hour.strftime('%H-%M-%S ')
        self.log.write(f'{hour} - [{apl}]: {message}\n')
    
    def main(self):
        print(colored(f'  Server open in: {self.Address[0]}:{self.Address[1]}', 'yellow'))
        try:
            while True:
                connection, adress = self.server.accept()
                apl = connection.recv(self.buffer);apl = apl.decode('utf-8')
                connection.send(f'  Welcome to Munity {apl}\n  Você está no canal geral!'.encode())
                self.AddUser(connection, apl)
                print(colored(f'  {apl} - has joinned...', 'green'))
                thread = Thread(target=self.ListenUsers, args=(connection, apl));thread.daemon=True;thread.start()
        except KeyboardInterrupt:
            print()
            exit(0)

def main():
    chat = MunityServer('127.0.0.1', 5555)
    chat.Start()

if __name__ == '__main__':
    main()