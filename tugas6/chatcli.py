import threading
import socket
import json
import sys

TARGET_IP = '127.0.0.1'


class ChatClient:
    def __init__(self, server) -> None:
        self.server = server
        self.portnumber = 8999
        if server == 'A':
            self.portnumber = 8999
        if server == 'B':
            self.portnumber = 9000
        if server == 'C':
            self.portnumber = 9001
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (TARGET_IP, self.portnumber)
        self.sock.connect(self.server_address)
        self.token_id = ""

    def proses(self, cmdline):
        j = cmdline.split(' ')
        try:
            command = j[0].strip()
            if command == 'register':
                username = j[1].strip()
                name = j[2].strip()
                password = j[3].strip()
                return self.register(username, name, password)
            elif command == 'login':
                username = j[1].strip()
                password = j[2].strip()
                return self.login(username, password)
            elif command == 'logout':
                return self.logout()
            elif command == 'inbox':
                return self.get_inbox()
            elif command == 'send':
                address = j[1].strip().split('@')
                username_to = address[0].strip()
                server_to = address[1].strip()
                message = ""
                for w in j[2:]:
                    message = message + w + ' '
                if server_to == self.server:
                    return self.send_message(username_to, message)
                else:
                    return self.send_message_to_server(server_to, username_to, message)
            elif command == 'creategroup':
                group_id = j[1].strip()
                group_members = j[2].strip()
                return self.create_group(group_id, group_members)
            elif command == 'sendgroup':
                group_id = j[1].strip()
                message = ""
                for w in j[2:]:
                    message = message + w + ' '
                return self.sendgroupmessage(group_id, message)
            elif command == 'sendfile':
                address = j[1].strip()
                filename = j[2].strip()
                address_split = address.split('@')
                username_to = address_split[0].strip()
                server_to = address_split[1].strip()
                if self.server == server_to:
                    return self.send_file(address, filename)
                else:
                    return self.send_file_to_server(address, filename)
            elif command == 'sendfilegroup':
                server_id = self.server
                group_id = j[1].strip()
                filename = j[2].strip()
                return self.send_file_group(server_id, group_id, filename)
            elif command == 'sendfilegroupserver':
                group_id = j[1].strip()
                server_id = j[2].strip()
                filename = j[3].strip()
                return self.send_file_group_to_server(group_id, server_id, filename)
        except IndexError:
            return "Command tidak benar"

    def send_string(self, string: str):
        try:
            self.sock.sendall(string.encode())
            receive_msg = ""
            while True:
                data = self.sock.recv(32)
                if data:
                    receive_msg = "{}{}".format(receive_msg, data.decode())
                    print(receive_msg)
                    if receive_msg[-4:] == '\r\n\r\n':
                        return json.loads(receive_msg)
        except:
            self.sock.close()
            return {'status': 'error', 'message': 'gagal'}

    def login(self, username, password):
        if self.token_id != '':
            return "Error: another user already logged in"
        string = "login {} {} \r\n" . format(username, password)
        result = self.send_string(string)
        if result['status'] == 'ok':
            self.token_id = result['token_id']
            return "Username {} logged in, token {} " .format(username, self.token_id)
        else:
            return "Error: {}" . format(result['message'])

    def register(self, username, name, password):
        message = "register {} {} {}\r\n".format(username, name, password)
        result = self.send_string(message)
        if result['status'] == 'ok':
            return 'User {} succesfully registered'.format(username)
        else:
            return 'Error: {}'.format(result['message'])

    def logout(self):
        string = "logout {}\r\n".format(self.token_id)
        result = self.send_string(string)
        if result['status'] == 'ok':
            self.token_id = ''
            return "Logged out"
        else:
            return "Error: {}".format(result['message'])

    def get_inbox(self):
        token_id = self.token_id

        string = "inbox {}\r\n".format(token_id)
        result = self.send_string(string)
        if result['status'] == 'ok':
            return result['inbox']
        else:
            return "Error: {}".format(result['message'])

    def send_message(self, usernameto="xxx", message="xxx"):
        if self.token_id == "":
            return "Error: not authorized"
        string = "send {} {} {}\r\n" . format(
            self.token_id, usernameto, message)
        result = self.send_string(string)
        if result['status'] == 'ok':
            return "Message telah dikirim ke {}" . format(usernameto)
        else:
            return "Error: {}" . format(result['message'])

    def send_message_to_server(self, server_to, username_to, message):
        if self.token_id == "":
            return "Error: not authorized"
        string = 'sendtoserver {} {} {} {}\r\n'.format(
            self.token_id, server_to, username_to, message)
        result = self.send_string(string)
        if result['status'] == 'ok':
            return 'Message telah dikirim ke server {}'.format(server_to)
        else:
            return 'Error: {}'.format(result['message'])

    def send_file(self, address, filename):
        if self.token_id == "":
            return "Error: not authorized"
        string = "sendfile {} {} {}\r\n" .format(
            self.token_id, address, filename)
        result = self.send_string(string)
        if result['status'] == 'ok':
            return 'File {} sent to {}'.format(filename, address)
        else:
            return 'Error: {}'.format(result['message'])

    def send_file_to_server(self, address, filename):
        if self.token_id == '':
            return "Error: not authorized"

        server_from = self.server
        string = 'sendfileserver {} {} {} {}\r\n'.format(
            self.token_id, server_from, address, filename)
        result = self.send_string(string)
        if result['status'] == 'ok':
            return 'File {} sent to {}'.format(filename, address.split(' ')[0])
        else:
            return 'Error: {}'.format(result['message'])

    def send_file_group_to_server(self, group_id, server_id, filename):
        if self.token_id == '':
            return "Error: not authorized"

        server_from = self.server
        string = 'sendfilegroupserver {} {} {} {} {}\r\n'.format(
            self.token_id, server_from, server_id, group_id, filename)
        result = self.send_string(string)
        print(result)
        if result['status'] == 'ok':
            return 'File {} sent to group {}'.format(filename, group_id)
        else:
            return 'Error: {}'.format(result['message'])

    def send_file_group(self, server_id, group_id, filename):
        if self.token_id == '':
            return "Error: not authorized"

        string = 'sendfilegroup {} {} {} {}\r\n'.format(
            self.token_id, server_id, group_id, filename)
        result = self.send_string(string)
        if result['status'] == 'ok':
            return result['message']
        else:
            return 'Error: {}'.format(result['message'])

    def sendgroupmessage(self, group_id, message):
        if self.token_id == "":
            return "Error: not authorized"
        string = "sendgroup {} {} {} {}\r\n" . format(
            self.token_id, group_id, self.server, message)
        result = self.send_string(string)
        if result['status'] == 'ok':
            return "Message sent to {}" . format(group_id)
        else:
            return "Error: {}" . format(result['message'])

    def create_group(self, group_id, members):
        if self.token_id == "":
            return "Error: not authorized"
        string = "creategroup {} {}\r\n".format(group_id, members)
        result = self.send_string(string)
        if result['status'] == 'ok':
            return 'Group {} created with member: {}'.format(group_id, members)
        else:
            return 'Error: {}'.format(result['message'])


if __name__ == '__main__':
    server = 'A'
    try:
        server = sys.argv[1]
    except:
        pass

    if server != 'A' and server != 'B' and server != 'C':
        print('Server tidak ada')
        sys.exit()

    cc = ChatClient(server)
    while True:
        cmdline = input("\nCommand: ")
        print(cc.proses(cmdline))
