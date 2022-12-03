import enum
import socket
import select

class SOCKET_OP(enum.Enum):
	NEW_CONNECTION = 0
	DATA_IN = 1
	HANGUP = 2

class Server_Socket:
	clients = []

	def __init__(self, host, port):
		self.host = host
		self.port = port

	def listen(self):
		serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		serversock.bind((self.host, self.port))
		serversock.listen(10)

		while True:
			print('waiting in select')
			all_socks = self.clients + [serversock]
			readable, writable, exceptional = select.select(all_socks, [], all_socks)
			if len(exceptional) >= 1:
				print('exceptional! %s' % (exceptional,))
				continue
			if len(readable) >= 1:
				client = readable[0]
				if client == serversock:
					client = self.addConnection(serversock)
					data = None
					op = SOCKET_OP.NEW_CONNECTION
				else:
					data = client.recv(1024)
					if len(data) <= 0:
						print('client - hangup')
						self.clients.remove(client)
						op = SOCKET_OP.HANGUP
					else:
						op = SOCKET_OP.DATA_IN
				yield client, data, op

	def addConnection(self, serversock):
		print('serversock in')
		current_connection, client_address = serversock.accept()
		self.clients.append(current_connection)
		print('%s connected' % (client_address,))
		return current_connection

	@classmethod
	def broadcast(cls, client_list, data):
		jsondata = bytes(data, 'utf-8')
		for c in client_list:
			c.send(jsondata)
