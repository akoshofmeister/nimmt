import socket
import json

target_host = '0.0.0.0'
target_port = 6546

def do_cmd(j):
	print('doing cmd')
	print(j.get('cmd'))

def parse_cmd(msg):
	try:
		res = json.loads(msg)
		print(res)
		do_cmd(res)
		return True
	except(json.decoder.JSONDecodeError):
		print('json decode error...')
		return False

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((target_host, target_port))
while True:
	response = client.recv(4096)
	if response == b'q\n':
		print('quitting...')
		break
	if not parse_cmd(response):
		print('Not a json:', response)
