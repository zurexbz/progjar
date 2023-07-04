import logging
import threading
import uuid
import os
from datetime import datetime
import socket
from queue import Queue
from datetime import datetime


class ToOtherServerThread(threading.Thread):
    def __init__(self, server, port):
        self.target_server_address = server
        self.target_server_port = port
        self.queue = Queue()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        threading.Thread.__init__(self)

    def run(self):
        self.sock.connect(
            (self.target_server_address, self.target_server_port))
        while True:
            while not self.queue.empty():
                msg = self.queue.get()
                msg = msg.rstrip() + '\r\n'
                self.sock.sendall(msg.encode())

    def put(self, msg):
        self.queue.put(msg)


class Chat:
    def __init__(self):
        self.sessions = {}
        self.users = {
            'fayyadh': {
                'name': 'Fayyadh Hafizh',
                'password': 'keren',
                'incoming': {},
                'outgoing': {}
            },
            'amanda': {
                'name': 'Amanda Salwa Salsabila',
                'password': 'keren',
                'incoming': {},
                'outgoing': {}
            },
            'firman': {
                'name': 'Firman Utina',
                'password': 'keren',
                'incoming': {},
                'outgoing': {}
            }
        }
        self.servers = {
            'A': ToOtherServerThread('127.0.0.1', 8999),
            'B': ToOtherServerThread('127.0.0.1', 9000),
            'C': ToOtherServerThread('127.0.0.1', 9001),
        }
        self.servers['A'].start()
        self.servers['B'].start()
        self.servers['C'].start()
        self.groups = {
            'groupA': ['amanda@A', 'fayyadh@B'],
            'groupB': ['amanda@B', 'fayyadh@A']
        }

    def proses(self, data):
        j = data.split(' ')
        try:
            command = j[0].strip()
            if command == 'login':
                username = j[1].strip()
                password = j[2].strip()
                return self.login(username, password)
            elif command == 'register':
                username = j[1].strip()
                name = j[2].strip()
                password = j[3].strip()
                return self.register(username, name, password)
            elif command == 'logout':
                token_id = j[1].strip()
                return self.logout(token_id)
            elif command == 'inbox':
                token_id = j[1].strip()
                return self.get_inbox(token_id)
            elif command == 'send':
                session_id = j[1].strip()
                username_to = j[2].strip()
                message = ""
                for w in j[3:]:
                    message = message + w + ' '
                username_from = self.sessions[session_id]['username']
                logging.warning('Send: session {} send message from {} to {}'.format(
                    session_id, username_from, username_to))
                return self.send_message(session_id, username_from, username_to, message)
            elif command == 'sendtoserver':
                session_id = j[1].strip()
                server_id = j[2].strip()
                username_to = j[3].strip()
                message = ""
                for w in j[4:]:
                    message = message + w + ' '

                username_from = self.sessions[session_id]['username']
                logging.warning('Send to server {}: session {} sent message from {} to {}'.format(
                    server_id, session_id, username_from, username_to))
                return self.send_to_server(session_id, server_id, username_to, message)
            elif command == 'sendgroup':
                session_id = j[1].strip()
                group_id = j[2].strip()
                server_from = j[3].strip()
                message = ""
                for w in j[4:]:
                    message = message + w + ' '
                usernamefrom = self.sessions[session_id]['username']
                logging.warning("Send: session {} sent message from {} to {}".format(
                    session_id, usernamefrom, group_id))
                return self.send_group_message(session_id, usernamefrom, group_id, server_from, message)
            elif command == 'creategroup':
                group_id = j[1].strip()
                group_members = j[2].strip()
                return self.create_group(group_id, group_members)
            elif command == 'serverfile':
                username_to = j[1].strip()
                filename = j[2].strip()
                content = ' '.join(j[3:])
                return self.server_file(username_to, filename, content)
            elif command == 'servergroupfile':
                session_id = j[1].strip()
                server_from = j[2].strip()
                group_id = j[3].strip()
                filename = j[4].strip()
                content = ' '.join(j[5:])
                return self.server_group_file(session_id, server_from, group_id, filename, content)
            elif command == 'serverinbox':
                username_from = j[1].strip()
                username_to = j[2].strip()
                message = ""
                for w in j[3:]:
                    message = message + w + ' '
                return self.server_inbox(username_from, username_to, message)
            elif command == 'sendfile':
                session_id = j[1].strip()
                address = j[2].strip()
                filename = j[3].strip()
                address_split = address.split('@')
                username_to = address_split[0].strip()
                server_id = address_split[1].strip()
                return self.send_file(session_id, server_id, username_to, filename)
            elif command == 'sendfileserver':
                session_id = j[1].strip()
                server_from = j[2].strip()
                address = j[3].strip()
                filename = j[4].strip()
                address_split = address.split('@')
                username_to = address_split[0].strip()
                server_id = address_split[1].strip()
                return self.send_file_to_server(session_id, server_id, username_to, filename)
            elif command == 'sendfilegroup':
                session_id = j[1].strip()
                server_from = j[2].strip()
                group_id = j[3].strip()
                filename = j[4].strip()
                return self.send_file_group(session_id, server_from, group_id, filename)
            elif command == 'sendfilegroupserver':
                session_id = j[1].strip()
                server_from = j[2].strip()
                server_id = j[3].strip()
                group_id = j[4].strip()
                filename = j[5].strip()
                return self.send_file_group_to_server(session_id, server_from, server_id, group_id, filename)
        except KeyError:
            return {'status': 'error', 'message': 'Information tidak ditemukan'}
        except IndexError:
            return {'status': 'error', 'message': 'Protokol tidak benar'}

    def login(self, username, password):
        if username not in self.users:
            return {'status': 'error', 'message': 'User tidak ada'}
        if self.users[username]['password'] != password:
            return {'status': 'error', 'message': 'Username atau password salah'}
        token_id = str(uuid.uuid4())
        self.sessions[token_id] = {
            'username': username, 'user_detail': self.users[username]}
        return {'status': 'ok', 'token_id': token_id}

    def register(self, username, name, password):
        if username in self.users:
            return {'status': 'error', 'message': 'User sudah ada'}
        self.users[username] = {'name': name, 'password': password, 'incoming': {},
                                'outgoing': {}}
        if not os.path.exists('files/'):
            os.mkdir('files')
        os.chdir('files/')
        if not os.path.exists(username):
            os.mkdir(username)
        os.chdir('../')
        return {'status': 'ok', 'message': 'User telah terdaftar'}

    def logout(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]
            return {'status': 'ok', 'message': "User telah keluar"}
        else:
            return {'status': 'error', 'message': "Session tidak ditemukan"}

    def get_inbox(self, session_id):
        if session_id not in self.sessions:
            return {'status': 'error', 'message': 'Session tidak ditemukan'}

        username = self.sessions[session_id]['username']

        if username not in self.users:
            return {'status': 'error', 'message': 'User tidak ditemukan'}

        inbox = self.users[username]['incoming']

        return {'status': 'ok', 'inbox': inbox}

    def server_file(self, username_to, filename, content):
        path_to = 'files/' + username_to + '/'
        print(os.path.abspath(path_to))
        os.chdir(path_to)
        print('lewat brooo')

        if not os.path.exists(filename):
            fp_new = open(filename, 'wb+')
            fp_new.write(bytes(content, 'utf-8'))
            fp_new.close()
            os.chdir('../../')
            return {'status': 'ok', 'message': 'File terkirim'}
        else:
            os.chdir('../../')
            return {'status': 'error', 'message': 'File sudah ada'}

    def server_group_file(self, session_id, server_from, group_id, filename, content):
        username_from = self.sessions[session_id]['username']

        for member in self.groups[group_id]:
            address = member.split('@')
            username_to = address[0].strip()
            server_to = address[1].strip()
            if username_to == username_from:
                continue

            if server_to == server_from:
                self.server_file(username_to, filename, content)
            else:
                self.send_file_to_server(
                    session_id, server_to, username_to, filename)

        return {'status': 'ok', 'message': 'File terkirim ke group {}'.format(group_id)}

    def server_inbox(self, username_from, username_to, message):
        s_fr = self.get_user(username_from)
        s_to = self.get_user(username_to)

        if s_fr == False and s_to == False:
            return {'status': 'ok', 'message': 'User tidak ditemukan'}

        curr_time = datetime.now()
        msg = {'msg_from': s_fr['name'], 'msg_to': s_to['name'],
               'msg': message, 'sent_time': curr_time.strftime("%Y-%m-%d %H:%M:%S")}

        outqueue_sender = s_fr['outgoing']
        inqueue_receiver = s_to['incoming']
        try:
            outqueue_sender[username_from].append(msg)
        except KeyError:
            outqueue_sender[username_from] = []
            outqueue_sender[username_from].append(msg)
        try:
            inqueue_receiver[username_from].append(msg)
        except KeyError:
            inqueue_receiver[username_from] = []
            inqueue_receiver[username_from].append(msg)
        return {'status': 'ok', 'message': 'Message ke server telah dikirim'}

    def get_user(self, username):
        if username not in self.users:
            return False
        return self.users[username]

    def send_message(self, session_id, username_from, username_to, message):
        if session_id not in self.sessions:
            return {'status': 'error', 'message': 'Session tidak ditemukan'}
        s_fr = self.get_user(username_from)
        s_to = self.get_user(username_to)

        if s_fr is False or s_to is False:
            return {'status': 'error', 'message': 'User tidak ditemukan'}

        curr_time = datetime.now()
        message = {'msg_from': s_fr['name'], 'msg_to': s_to['name'],
                   'msg': message, 'sent_time': curr_time.strftime("%Y-%m-%d %H:%M:%S")}
        outqueue_sender = s_fr['outgoing']
        inqueue_receiver = s_to['incoming']
        try:
            outqueue_sender[username_from].append(message)
        except KeyError:
            outqueue_sender[username_from] = []
            outqueue_sender[username_from].append(message)
        try:
            inqueue_receiver[username_from].append(message)
        except KeyError:
            inqueue_receiver[username_from] = []
            inqueue_receiver[username_from].append(message)
        return {'status': 'ok', 'message': 'Message sent'}

    def send_to_server(self, session_id, server_id, username_to, message):
        if session_id not in self.sessions:
            return {'status': 'error', 'message': 'Session tidak ditemukan'}
        if server_id not in self.servers:
            return {'status': 'error', 'message': 'Server {} tidak ditemukan'.format(server_id)}

        username_from = self.sessions[session_id]['username']
        self.servers[server_id].put('serverinbox {} {} {}'.format(
            username_from, username_to, message))
        return {'status': 'ok', 'message': 'Message sent to server {}'.format(server_id)}

    def send_group_message(self, session_id, username_from, group_id, server_from, message):
        if session_id not in self.sessions:
            return {'status': 'error', 'message': 'Session tidak ditemukan'}
        if group_id not in self.groups:
            return {'status': 'error', 'message': 'Group tidak ditemukan'}

        s_fr = self.get_user(username_from)

        if s_fr is False:
            return {'status': 'error', 'message': 'User tidak ditemukan'}
        if username_from + '@' + server_from not in self.groups[group_id]:
            return {'status': 'error', 'message': 'User tidak ada dalam {}'.format(group_id)}
        sent_id = []

        for member in self.groups[group_id]:
            address = member.split("@")
            username_to = address[0].strip()
            server_to = address[1].strip()
            s_to = self.get_user(username_to)
            if s_to is False or server_to not in self.servers or s_to is s_fr:
                continue
            if server_to == server_from:
                self.send_message(session_id, username_from,
                                  username_to, message)
            else:
                self.send_to_server(session_id, server_to,
                                    username_to, message)

            sent_id.append(username_to)

        return {'status': 'ok', 'message': 'Message Sent to {} in {}'.format(', '.join(sent_id), group_id)}

    def create_group(self, group_id, members):
        if group_id in self.groups:
            return {'status': 'error', 'message': 'Group {} sudah ada'.format(group_id)}
        self.groups[group_id] = []
        user_member = members.split(',')
        for user in user_member:
            if user not in self.groups[group_id]:
                self.groups[group_id].append(user)

        return {'status': 'ok', 'message': 'Group {} telah dibuat'.format(group_id)}

    def send_file(self, session_id, server_id, username_to, filename):
        username_from = self.sessions[session_id]['username']

        if username_to == username_from:
            return {'status': 'error', 'message': 'Tidak bisa mengirim ke diri sendiri'}
        if session_id not in self.sessions:
            return {'status': 'error', 'message': 'Session tidak ditemukan'}
        if username_to not in self.users:
            return {'status': 'error', 'message': 'User tujuan tidak ditemukan'}
        if server_id not in self.servers:
            return {'status': 'ERROR', 'message': 'Server Tidak Ada'}
        path_from = './files/' + username_from + '/'
        path_to = '../' + username_to + '/'
        print(os.path.abspath(path_from))
        os.chdir(path_from)

        if os.path.exists(filename):
            fp = open(f"{filename}", 'rb')
            content = fp.read()
            fp.close()
            os.chdir(path_to)
            if os.path.exists(f"{filename}"):
                os.chdir('../../')
                return {'status': 'error', 'message': 'File sudah ada di user {}'.format(username_to)}
            fp_new = open(filename, 'wb+')
            fp_new.write(content)
            fp_new.close()
            os.chdir('../../')
            return {'status': 'ok', 'message': 'File terkirim'}
        else:
            os.chdir('../../')
            return {'status': 'error', 'message': 'File tidak ada'}

    def send_file_to_server(self, session_id, server_to, username_to, filename):
        username_from = self.sessions[session_id]['username']

        if session_id not in self.sessions:
            return {'status': 'error', 'message': 'Session tidak ditemukan'}
        if username_to == username_from:
            return {'status': 'error', 'message': 'Tidak bisa mengirim ke diri sendiri'}
        if username_to not in self.users:
            return {'status': 'error', 'message': 'User tujuan tidak ditemukan'}
        if server_to not in self.servers:
            return {'status': 'ERROR', 'message': 'Server Tidak Ada'}

        path_from = './files/' + username_from + '/'
        print(username_from)
        print(os.path.abspath(path_from))
        os.chdir(path_from)

        if os.path.exists(filename):
            print('masuk filename')
            fp = open(f"{filename}", 'rb')
            content = fp.read()
            fp.close()
            os.chdir('../../')
            self.servers[server_to].put('serverfile {} {} {}'.format(
                username_to, filename, content.decode()))
            return {'status': 'ok', 'message': 'File terkirim'}
        else:
            print('gamasuk')
            os.chdir('../../')
            return {'status': 'error', 'message': 'File tidak ada'}

    def send_file_group(self, session_id, server_from, group_id, filename):
        if session_id not in self.sessions:
            return {'status': 'error', 'message': 'Session tidak ditemukan'}
        if group_id not in self.groups:
            return {'status': 'error', 'message': 'Group {} tidak ditemukan'.format(group_id)}

        username_from = self.sessions[session_id]['username']
        path_from = 'files/' + username_from + '/'

        os.chdir(path_from)
        if not os.path.exists(filename):
            os.chdir('../../')
            return {'status': 'error', 'message': 'File tidak ada'}

        os.chdir('../../')
        for member in self.groups[group_id]:
            address = member.split('@')
            username_to = address[0].strip()
            server_to = address[1].strip()
            if username_to == username_from:
                continue

            if server_to == server_from:
                self.send_file(session_id, server_from, username_to, filename)
            else:
                self.send_file_to_server(
                    session_id, server_to, username_to, filename)

        os.chdir('../../')

        return {'status': 'ok', 'message': 'File terkirim ke group {}'.format(group_id)}

    def send_file_group_to_server(self, session_id, server_from, server_id, group_id, filename):
        if session_id not in self.sessions:
            return {'status': 'error', 'message': 'Session tidak ditemukan'}
        if group_id not in self.groups:
            return {'status': 'error', 'message': 'Group tidak ditemukan'}

        username_from = self.sessions[session_id]['username']
        path_from = 'files/' + username_from + "/"

        os.chdir(path_from)

        if not os.path.exists(filename):
            os.chdir('../../')
            return {'status': 'error', 'message': 'File tidak ada'}

        fp = open(f"{filename}", 'rb')
        content = fp.read()
        fp.close()
        os.chdir('../../')
        self.servers[server_id].put('servergroupfile {} {} {} {} {}'.format(
            session_id, server_from, group_id, filename, content))

        return {'status': 'ok', 'message': 'File terkirim ke group {} melalui server {}'.format(group_id, server_id)}
