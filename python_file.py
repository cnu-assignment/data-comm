import socket
import threading
import time
import subprocess
import os
FLAGS = None
class ServerSocket():

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', FLAGS.port))
        self.student_list = list()
        self.game_list = list()
        self.winning_student = list()
        self.student_correct_list = ["201402329","201950218", '201550320']
        self.winning_student = list()
        #self.ip_list = list()


    def wait_queue(self):
        #TODO LOCK을 걸것
        while True:
            data, addr = self.socket.recvfrom(2000)
            if data.decode("utf-8").split()[0] == "game":
                self.game_list.append((data.decode(), addr))
            else:
                data_set = (data.decode(), addr)
                ip = addr[0]
                port = addr[1]
                #if ip not in self.ip_list:
                #self.ip_list.append(ip)
                if data.decode() in self.student_correct_list :
                    self.student_list.append(data_set)
                    print(" ["+data.decode()+"] 님이 입장하셨습니다.")
                    self.socket.sendto("correct".encode(), addr)

                else:
                    self.socket.sendto("not correct studentID send again".encode(),addr)


    def start_ARQ(self,player,file_name):
        print(player, "start File transmit")
        p = subprocess.Popen(["python3", "stopAndWait_receiver.py",'-f', file_name])

        while True:
            end = p.poll()
            if end is not None:
                print("transmit end")
                break
            continue


    def start_game(self, student_list):
        print("게임을 기다리는 중입니다...")
        while len(student_list) >= 0:
            if len(student_list) <= 1:
                pass
            else:
                player_1 = student_list[0]
                del student_list[0]
                player_2 = student_list[0]
                del student_list[0]

                while True:
                    self.socket.sendto("send pythonfile : recv_1.py".encode(), player_1[1])
                    self.start_ARQ(player_1[0], "recv_1.py")
                    if os.path.exists("recv_1.py"):
                        self.socket.sendto("correct".encode(), player_1[1])
                        break
                    else:
                        self.socket.sendto("1-not correct file name send again : recv_1.py".encode(), player_1[1])


                while True:
                    self.socket.sendto("send pythonfile : recv_2.py".encode(), player_2[1])
                    self.start_ARQ(player_2[0], "recv_2.py")
                    if os.path.exists("recv_2.py"):
                        self.socket.sendto("correct".encode(), player_2[1])
                        break
                    else:
                        self.socket.sendto("1-not correct file name send again : recv_2.py".encode(), player_2[1])

                self.socket.sendto("send pythonfile : ".encode(), player_2[1])




                p_2 = subprocess.check_output(["python3", "recv_1.py"]).decode("utf-8").split("\n")[0]
                p_3 = subprocess.check_output(["python3", "recv_2.py"]).decode("utf-8").split("\n")[0]
                print(p_2)
                print(p_3)

                p_2 = p_2.split(',')
                p_3 = p_3.split(',')

                scores = [0,0]
                for i in range(len(p_2)):
                    print(str(i)+" Round Start ")
                    print(player_1[0] + " vs "+ player_2[0])
                    scores[self.game_rock_scissor_paper(p_2[i], p_3[i])] += 1
                if scores[0] > scores[1]:
                    print(player_1[0]+"winning")
                    self.winning_student.append(player_1)
                elif  scores[0] < scores[1]:
                    print(player_2[0]+"winning")
                    self.winning_student.append(player_2)
                else:
                    print("same score")


    def game_start(self):
        gamers = list()
        score = [0,0]
        addr_1 = None
        addr_2 = None
        print("게임을 기다리는 중입니다..")

        while True:
            try:
                if len(self.student_list) <= 1:
                    pass
                else:
                    gamer_1 = self.student_list[0]
                    del self.student_list[0]
                    self.socket.sendto("게임을 시작합니다.".encode(), gamer_1[1])

                    gamer_2 = self.student_list[0]
                    del self.student_list[0]
                    self.socket.sendto("게임을 시작합니다.".encode(), gamer_2[1])

                    print("["+gamer_1[0]+" vs "+gamer_2[0]+"]")

                    for i in range(3):
                        print("게임 입력중 ..")
                        while len(self.game_list) < 2:
                            time.sleep(5)
                        data_1, addr_1 = self.game_list[0]
                        self.socket.sendto("게임을 시작합니다.".encode(), addr_1)

                        del self.game_list[0]


                        data_2, addr_2 = self.game_list[0]
                        self.socket.sendto("게임을 시작합니다.".encode(), addr_1)

                        del self.game_list[0]


                        gamers = [data_1.split(), data_2.split()]

                        result = self.game_rock_scissor_paper(gamers[0][2], gamers[1][2])
                        if result == -1:
                            score[0] += 1
                            score[1] += 1
                            print("{}: {}\n{}: {}".format(gamers[0][1], gamers[0][2], gamers[1][1], gamers[1][2]))
                            print("{}차전 : 무승부".format(i+1))
                        else:
                            score[result] += 1
                            print("{}: {}\n{}: {}".format(gamers[0][1], gamers[0][2], gamers[1][1], gamers[1][2]))
                            print("{}차전 : {}승".format(i+1, gamers[result][1]))

                        if i < 2:
                            self.socket.sendto("게임을 시작합니다.".encode(), addr_1)
                            self.socket.sendto("게임을 시작합니다.".encode(), addr_2)

                    if score[0] == score[1]:
                        print('무승부! 퇴근하세요')
                        self.socket.sendto("수고하셨습니다.".encode(), addr_1)
                        self.socket.sendto("수고하셨습니다.".encode(), addr_2)




                    else:
                        win_result = score[0] > score[1] and (gamers[0][1], addr_1) or (gamers[1][1], addr_2)
                        lose_result = score[0] > score[1] and (gamers[0][1], addr_1) or (gamers[1][1], addr_2)

                        print(win_result[0]+" 승리! 퇴근하세요")
                        #self.ip_list.remove(win_result[1])

                        self.socket.sendto("수고하셨습니다.".encode(), win_result[1])
                        self.socket.sendto("수고하셨습니다.".encode(), lose_result[1])




                        self.student_list.insert(0, lose_result)
            except Exception as e:
                print("error:",e)





    def game_rock_scissor_paper(self, input_1, input_2):
        input_1 = int(input_1)
        input_2 = int(input_2)
        if input_1 == input_2:
            return -1
        else:
            if input_1 == 0:
                if input_2 == 1:
                    return 1
                elif input_2 == 2:
                    return 0
            if input_1 == 1:
                if input_2 == 0:
                    return 0
                elif input_2 == 2:
                    return 1
            if input_1 == 2:
                if input_2 == 0:
                    return 1
                elif input_2 == 1:
                     return 0





    def main(self):
        threading.Thread(target=self.wait_queue).start()


        threading.Thread(target=self.start_game,args=(self.student_list,)).start()
        while len(self.student_list) > 6:
            threading.Thread(target=self.start_game,args=(self.student_list,)).start()
            self.student_list = self.winning_student
        #self.start_game()



if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ip', type=str,
                         default='localhost')
    parser.add_argument('-p', '--port', type=int,
                         default=1234)

    FLAGS, _ = parser.parse_known_args()

    server_socket = ServerSocket()
    server_socket.main()
