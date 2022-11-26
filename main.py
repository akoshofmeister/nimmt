import time

import server
from runServer import Server_Socket

HOST = '0.0.0.0'
PORT = 6546

if __name__ == '__main__':
    try:
        serversock=Server_Socket(HOST, PORT)
        serversock.set_process_function(server.process_data)
        serversock.listen()

    except KeyboardInterrupt:
        print('interrupt - exiting')
        # print('n_connections: %d' % (len(all_players),))
        # for client in all_players:
        #     del client
        # time.sleep(1)
        exit(9)