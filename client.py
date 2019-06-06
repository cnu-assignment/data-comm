import socket
import subprocess
FLAGS = None
class ClientSocket():

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def socket_send(self):
        while True:
            ID = input("학번을 입력하세요 : ")

            self.socket.sendto(ID.encode(), (FLAGS.ip,FLAGS.port))
            print("send complete")
            data, addr = self.socket.recvfrom(2000)
            print(data)
            if data.decode() == 'correct':
                break
            else:
                print(data.decode())



        while True:
            data, addr = self.socket.recvfrom(2000)
            print(data.decode())

            p = subprocess.Popen(["python3","stopAndWait_send.py"])
            while True:
                end = p.poll()
                if end is not None:
                    print("transmit end")
                    data, addr = self.socket.recvfrom(2000)
                    if data.decode() == "correct":
                        break
                continue






    def main(self):
        self.socket_send()
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ip', type=str,
                         default='localhost')
    parser.add_argument('-p', '--port', type=int,
                         default=1234)

    FLAGS, _ = parser.parse_known_args()

    client_socket = ClientSocket()
    client_socket.main()
