# -- coding: utf-8 --
"""
Created on Sat Apr 15 13:12:32 2023

@author: User
"""

import socket
HEADER = 64
PORT = 5059
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)


def send(msg):
    try:
        #source--(1) is used to implement this part
        # msg is the name inputed
        message = msg.encode(FORMAT)
        # compute its lenght and change it to bytes and send it so that the server can know how much the size of the name he would be receiving is
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        Player.send(send_length)
        Player.send(message)
        # this loop is incase the name was already used to input another one until she/he choose something different
        name = True
        while name:
            #start receiving data from server
            data = Player.recv(2048).decode(FORMAT)
            if data:
                print(data)
                if (data == "The name is already taken pick another one"):
                    msg = input("Please Enter your name:")
                    message = msg.encode(FORMAT)
                    msg_length = len(message)
                    send_length = str(msg_length).encode(FORMAT)
                    send_length += b' ' * (HEADER - len(send_length))
                    Player.send(send_length)
                    Player.send(message)
                else:
                    # means we received is connected
                    name = False
                    break

        booll = True
        roundd = 1
        while booll:
            data = Player.recv(2048).decode(FORMAT)

            if data:
                # recall that we added split to avoid no matter what concatenation because of the threads
                messages = data.split("split")
                for message in messages:
                    print(message)

                    try:
                        # if the message received is not a number than it is the end either the game stopped or finished
                        num = int(message)
                        resp = input("Enter the same number:")
                        Player.send(resp.encode(FORMAT))
                        roundd = roundd + 1

#everything above is done by Sarah Rouphael

                    #everything below is done by Lynn Edde and Rami Khalaf

                    except:
                        # add a return statment for each of the cases
                        try:
                            if (message.startswith("You are the winner of this game!!") or message.startswith("You lost this game!!") or message.startswith("Draw!!")):
                                booll = False
                                return
                            if message.startswith("the connection was closed"):
                                booll=False
                                return
                            if (message.startswith( "We have not received anything, the game has ended, you can try reconnecting")):
                                booll = False
                                return

                            if (message.startswith("the second player disconnected, the game will stop!")):
                                booll = False
                                return

                        except:
                            # these are useless
                            if (message == "We have not received anything, the game has ended, you can try reconnecting"):
                                booll = False
                                return

                            if (message == "the second player disconnected, the game will stop!"):
                                booll = False
                                return
        return

    except:
        print("An error occured from the server side, the game stopped")
        return


# try to connect to the server
try:

    Player = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Player.connect(ADDR)
    Playerr = input("Please Enter your name:")
    send(Playerr)
except:
    print("the server have not opened yet")

#Sources: written on the server code
