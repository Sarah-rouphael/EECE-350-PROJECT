# -- coding: utf-8 --
"""
Created on Sat Apr 15 13:05:41 2023

@author: User
"""
#source: everything on moodle and https://www.youtube.com/watch?v=McoDjOCb2Zo
import socket
import threading
import random
import time

# initialiazing the size of the messages to be sent, server ip, port
HEADER = 64
PORT = 5059
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
Players = True

# this list is for storing the RTT to check which is the winner
listt = []

# this list is used for storing the name to check wether the players inputed the same name to not allow it
list_name = []

# to check how many are still connected
nbrofthread = 0

# creating a socket and binding the ip and port number
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#create TCP welcoming socket
server.bind(ADDR)#server begins listening for
#incoming TCP requests

# incremented each time one player win
Score_player1 = 0
Score_player2 = 0

#source: 1 and 2
def handle_client(conn, addr):
    global nbrofthread
    global Score_player1
    global Score_player2
    global list_name
    global listt
    global Players
    print(f"[NEW CONNECTION] {addr} connected.")

    # the try is to catch errors when a client closes the window unexpectadly and will be handled in except
    try:

        connected = True

        # the timeout is set in case the player kept the window opened but left so that we do not wait forever
        conn.settimeout(15)
        while connected:

            try:
                # from the client side we will be calculating and sending first the size of the name inputed to choose the size we have to receive
                msg_length = conn.recv(HEADER).decode(FORMAT)
                if msg_length:
                    msg_length = int(msg_length)

                    # after receiving the size we receive the name with message length needed
                    msg = conn.recv(msg_length).decode(FORMAT)

                    # we take the time to choose the one who inputed the same name but later to change it
                    tm = time.time()
                    tup = (msg, tm)
                    list_name.append(tup)

                    namee = True
                    while namee:
                        # if we have 2 players now
                        if (len(list_name) > 1):
                            # check if the names are the same
                            if ((list_name[0][0] == list_name[1][0])):
                                # check who inputed last and ask her/him to input again
                                if (list_name[0][1] < list_name[1][1]):
                                    if (tup == list_name[1]):
                                        del list_name[1]
                                        conn.send(("The name is already taken pick another one").encode(FORMAT))
                                        msg_length = conn.recv(HEADER).decode(FORMAT)
                                        if msg_length:
                                            msg_length = int(msg_length)
                                            msg = conn.recv(msg_length).decode(FORMAT)
                                            tm = time.time()
                                            tup = (msg, tm)
                                            list_name.append(tup)
                                else:
                                    if (list_name[0][1] > list_name[1][1]):
                                        if (tup == list_name[0]):
                                            del list_name[0]
                                            conn.send(("The name is already taken pick another one").encode(FORMAT))
                                            msg_length = conn.recv(HEADER).decode(FORMAT)
                                            if msg_length:
                                                msg_length = int(msg_length)
                                                msg = conn.recv(msg_length).decode(FORMAT)
                                                tm = time.time()
                                                tup = (msg, tm)
                                                list_name.append(tup)
                            else:
                                # if the name are not equal
                                namee = False

                    # inform that they are both now connected
                    name = msg + " is connected"
                    conn.send((name).encode(FORMAT))
                    connected = False
                    nbrofthread = nbrofthread + 1

            # incase the person did not input in 15 seconds inform him that he was disconnected
            except socket.timeout:

                Score_player1 = 0
                Score_player2 = 0
                conn.send("We have not received anything, the game has ended, you can try reconnecting".encode(FORMAT))
                conn.close()
                connected = False
                return
            #Everything above is Done By Sarah Rouphael


        #From here till the end of the function handle_client is done by Jade El Masri
        # initialiazing the round
        count = 1
        boolean = True
        # if one client disconnected boolean will be set to false and the game finishes
        while boolean:

            if (nbrofthread) == 2:
                # after we have 2 players wait few seconds to synchronize the threads(make the threads run in parallel and avoiding errors)
                Players = False
                list_name = []
                time.sleep(2)
                # note that the split at the end was added in case the wait was not enough and the messages were concatenated
                #concatination is an error that happens when there lack of synchronization between the threads
                #synchronization: the threads are running in parallel and not one leading or lagging the other
                conn.send(("Welcome!The game will start" + "split").encode(FORMAT))
                #once 2 clients connect, a welcome message is sent to both clients informing them that the game will start
                # count start 1,2,3
                while (count < 4):

                    # nbrofthreads will be decremented if a player disconnects during the game
                    
                    if ((nbrofthread) == 2):

                        print("round " + str(count))
                        time.sleep(2)
                        # send which round we are at
                        conn.send(("Round " + str(count) + "split").encode(FORMAT))
                        x = game(conn, msg)
                        # after one game increment
                        count = count + 1
                    else:
                        # game will return false in case nbrofthreads was less than 2, so that we can inform the other client that the game has stopped
                        #and we close the connection(server does not send anything anymore)
                        if (x == False):
                            inform_lost_connection(conn)
                            Players = True

                            nbrofthread = 0
                            Score_player1 = 0
                            Score_player2 = 0
                            listt = []
                            conn.close()
                            boolean = False
                            return

                if (nbrofthread != 2):
                    inform_lost_connection(conn)
                    Players = True
                    Score_player1 = 0
                    Score_player2 = 0
                    nbrofthread = 0
                    listt = []
                    conn.close()

                # this is to display the end, scores
                if (boolean == True and nbrofthread == 2):
                    Termination(conn, msg)
                    time.sleep(4)
                    Players = True
                    Score_player1 = 0
                    Score_player2 = 0
                    nbrofthread = 0
                    listt = []
                    conn.close()
                    boolean = False
                    return


    except:
        # if client disconnected unexpectedly, the seerver closes the connection and sends to the other client
        #that the connection was closed
        try: conn.send(("the connection was closed").encode(FORMAT))
        except: do = False
        print("Clients closed")
        Score_player1 = 0
        Score_player2 = 0
        nbrofthread = 0
        list_name = []
        listt = []
        conn.close()
        time.sleep(2)
        Players = True
        


def game(conn, msg):
    global nbrofthread
    global Score_player1
    global Score_player2
    global listt
    global Players
    try:
        # generate a random number and send it
        rand = random.randint(0, 9)
        r = str(rand)
        time.sleep(5)
        conn.send((r).encode(FORMAT))
        #start calculating the start_time()
        start_time = time.time()

        connected = True
        # set timeout in case player left without closing the window
        conn.settimeout(15)
        while connected:
            try:
                #waiting for the client to send his response(number sent to him/her)
                response = conn.recv(2048).decode('utf-8')

                if response:

                    # conn.settimeout(None)
                    # after receiving calculate the finish time
                    finish_time = time.time()
                    try:
                        # if the response was an int and it was equal to the rand number store in the tupple name rtt and 1 otherwise name 0 0
                        # append the tuple to the list
                        response = int(response)
                        if (response == rand):
                            RTT = finish_time - start_time
                            listt.append((msg, RTT, 1))
                        else:
                            # when tuple at index 2 is 0->wrong input
                            listt.append((msg, 0, 0))


                    except:
                        # in case  the client sent a letter or something else, his/her response is considered as wrong input
                        #when tuple at index 2 is 0->wrong input
                        listt.append((msg, 0, 0))

            except socket.timeout:
                # handling errors:if a client took too much to respond to the server, the server closes the connection
                # and sends the following:
                conn.send(("We have not received anything, the game has ended, you can try reconnecting").encode(FORMAT))
                conn.close()
                connected = False
                nbrofthread = 0
                Score_player1 = 0
                Score_player2 = 0
                listt = []
                return True
        #everything above is done by Jade El Masri

            wait = True
            n = 0
            connected = False
        #everything below till the end of the function is done by Lynn Edde
        while wait:
            # nbrofthread will be decremented if a player disconnects
            if (nbrofthread == 2):
                # if the length of the list is 2, we are at the first round check the first 2 objects in the list 0,1
                #note: list at index 0 and index 1 contain the tuples having the names of two clients and their RTTS
                if (len(listt) == 2):
                    win_loose(n, msg, conn)
                    wait = False

                # if the length is 4 check listt[2] and list[3] we are at round 2
                if (len(listt) == 4):
                    n = 2
                    win_loose(n, msg, conn)
                    wait = False

                # if it is 6 check listt[4] and list[5] we are at round 3
                if (len(listt) == 6):
                    n = 4
                    win_loose(n, msg, conn)
                    wait = False

            else:
                # if one closed return false to inform that connection was lost(handle error), nbofthreads is less than 2
                wait = False
                return False

        return None
    except:
        try:
            conn.send(("the connection was closed").encode(FORMAT))
        except: do = False
        print("Clients closed")
        Score_player1 = 0
        Score_player2 = 0
        nbrofthread = 0
        listt = []
        conn.close()
        time.sleep(2)
        Players = True
        


# this function will check the value of RTT in the list and compare to choose the winner
# at round 1 n=0 compare listt[0] and listt[1] the value of RTT is in the tuple index 1,
# first we need to check if the input was correct -> tuple at index 2 if it is 1 than input was correct
def win_loose(n, msg, conn):
    global Score_player1
    global Score_player2
    global nbrofthread
    global listt
    try:
        #both clients have correct input
        if (listt[n][2] == 1 and listt[n + 1][2] == 1):
            #compare RTT which is at index 1 of the tuple
            if (listt[n][1] < listt[n + 1][1]):

                if (msg == listt[n][0]):
                    winner = "You are the winner, your RTT is " + str(listt[n][1]) + "  " + listt[n + 1][0] + " lost, his/her RTT is " + str(listt[n + 1][1]) + " split"
                    conn.send(winner.encode(FORMAT))
                    # here listt[n][0] which is the name of the player is the winner
                    # we chose Score_player1 to be assigned to the name in listt[0][0] and player2 for the next
                    # if this is the thread of the person msg=listt[n][0]=listt[0][0] we increment player 1
                    # but if the winner correspond to the second name not listt[0][0] increment player2
                    if listt[n][0] == listt[0][0]:
                        Score_player1 = Score_player1 + 1
                        

                    else:
                        Score_player2 = Score_player2 + 1
                        

                else:
                    #if msg!=listt[n][0] then we are in the thread in the client that lost
                    #list[n][1] was less than list [n+1][1]
                    winner = "You lost your RTT is " + str(listt[n + 1][1]) + "  " + listt[n][0] + " is the winner,his/her RTT is " + str(listt[n][1]) + " split"
                    conn.send((winner).encode(FORMAT))
                #we added time.sleep() to synchronize the threading functions when incrementing the score
                time.sleep(2)
                if Score_player1>Score_player2:
                    #results displayed in descending order
                    #which is done throughout this whole function
                    conn.send((listt[0][0]+" score = "+str(Score_player1)).encode(FORMAT))
                    conn.send((listt[1][0] +" score = "+ str(Score_player2)).encode(FORMAT))
                else:
                    conn.send((listt[1][0] +" score = "+ str(Score_player2)).encode(FORMAT))
                    conn.send((listt[0][0] +" score = "+ str(Score_player1)).encode(FORMAT))
            # same idea as before but we have to handle all cases if bigger or equal
            elif (listt[n][1] > listt[n + 1][1]):

                if (msg == listt[n][0]):
                    winner = "You lost your RTT is " + str(listt[n][1]) + "  " + listt[n + 1][0] + " is the winner,his/her RTT is " + str(listt[n + 1][1]) + " split"
                    conn.send((winner).encode(FORMAT))

                    if (listt[n][0] == listt[0][0]):
                        Score_player2 = Score_player2 + 1
                        

                    else:
                        Score_player1 = Score_player1 + 1
                        
                else:
                    winner = "You are the winner, your RTT is " + str(listt[n + 1][1]) + "  " + listt[n][0] + ",his/her RTT is " + str(listt[n][1]) + " split"
                    conn.send((winner).encode(FORMAT))
                time.sleep(2)
                if Score_player1>Score_player2:
                    conn.send((listt[0][0]+" score = "+str(Score_player1)).encode(FORMAT))
                    conn.send((listt[1][0] +" score = "+ str(Score_player2)).encode(FORMAT))
                else:
                    conn.send((listt[1][0]+" score = " + str(Score_player2)).encode(FORMAT))
                    conn.send((listt[0][0] +" score = "+ str(Score_player1)).encode(FORMAT))
            else:
                winner = "Draw. No winner" + " split"
                conn.send((winner).encode(FORMAT))
                time.sleep(2)
                if Score_player1>Score_player2:
                    conn.send((listt[0][0]+" score = "+str(Score_player1)).encode(FORMAT))
                    conn.send((listt[1][0] +" score = "+ str(Score_player2)).encode(FORMAT))
                else:
                    conn.send((listt[1][0] +" score = "+ str(Score_player2)).encode(FORMAT))
                    conn.send((listt[0][0] +" score = "+ str(Score_player1)).encode(FORMAT))
        #Everything above is written by Sarah Rouphael

        #Everything below till end of the function is written by Rami Khalaf

        # we have to handle if the input was wrong
        #resembles the ideas discussed before
        else:
            if (listt[n][2] == 0 and listt[n + 1][2] == 0):
                winner = "Draw" + " split"
                conn.send((winner).encode(FORMAT))
                time.sleep(2)
                if Score_player1>Score_player2:
                    conn.send((listt[0][0]+" score = "+str(Score_player1)).encode(FORMAT))
                    conn.send((listt[1][0] +" score = "+ str(Score_player2)).encode(FORMAT))
                else:
                    conn.send((listt[1][0] +" score = "+ str(Score_player2)).encode(FORMAT))
                    conn.send((listt[0][0] +" score = "+ str(Score_player1)).encode(FORMAT))


            #players pressing the wrong number are disqualified from a certain round is handled below
            #notice that RTT is not significant when a player presses the wrong number
            elif (listt[n][2] == 0 and listt[n + 1][2] == 1):

                if (msg == listt[n][0]):
                    winner = "You lost your input was wrong " + "  " + listt[n + 1][0] + " is the winner, his/her RTT is " + str(listt[n + 1][1]) + " split"
                    conn.send((winner).encode(FORMAT))
                    if (listt[n][0] == listt[0][0]):
                        Score_player2 = Score_player2 + 1
                    else:
                        Score_player1 = Score_player1 + 1

                else:
                    winner = "You are the winner, your RTT is " + str(listt[n + 1][1]) + "  " + listt[n][0] + " lost since his/her input was wrong" + " split"
                    conn.send((winner).encode(FORMAT))
                time.sleep(2)
                if Score_player1>Score_player2:
                    conn.send((listt[0][0]+" score = "+str(Score_player1)).encode(FORMAT))
                    conn.send((listt[1][0] +" score = "+ str(Score_player2)).encode(FORMAT))
                else:
                    conn.send((listt[1][0] +" score = "+ str(Score_player2)).encode(FORMAT))
                    conn.send((listt[0][0] +" score = "+ str(Score_player1)).encode(FORMAT))
            else:

                if (msg == listt[n + 1][0]):
                    winner = "You lost your input was wrong " + listt[n][0] + " is the winner, his/her RTT is " + str( listt[n][1]) + " split"
                    conn.send((winner).encode(FORMAT))
                    if (listt[n][0] == listt[0][0]):
                        Score_player1 = Score_player1 + 1
                    else:
                        Score_player2 = Score_player2 + 1
                        
                else:
                    winner = "You are the winner, your RTT is " + str(listt[n][1]) + listt[n + 1][0] + " lost since his/her input was wrong " + " split"
                    conn.send((winner).encode(FORMAT))
                time.sleep(2)
                if Score_player1>Score_player2:
                    conn.send((listt[0][0]+" score = "+str(Score_player1)).encode(FORMAT))
                    conn.send((listt[1][0] +" score = "+ str(Score_player2)).encode(FORMAT))
                else:
                    conn.send((listt[1][0] +" score = "+ str(Score_player2)).encode(FORMAT))
                    conn.send((listt[0][0] +" score = "+ str(Score_player1)).encode(FORMAT))

    except:
        try: conn.send(("the connection was closed").encode(FORMAT))
        except: do = False
        print("Clients closed")
        Score_player1 = 0
        Score_player2 = 0
        nbrofthread = 0
        listt = []
        conn.close()
        time.sleep(2)
        Players = True
#the function below handles an error whereby if a
#client disconnects unexpectedly, the server should inform the other client
#that the game has ended
def inform_lost_connection(conn):
    conn.send(("the second player disconnected, the game will stop!").encode(FORMAT))


# this is used to send who is the winner
#termination function is written by Lynn Edde and Rami Khalaf
def Termination(conn, msg):
    global Score_player1
    global Score_player2
    global listt
    global nbrofthread
    # this is used to allow the scores to be incremented in the threads in case of delays between the 2
    time.sleep(3)
    try:

        if (Score_player1 == Score_player2):
            conn.send("Draw!! No winner".encode(FORMAT))
            return
        # as we said listt[0][0] correspond to score player 1
        if (msg == listt[0][0]):
            if (Score_player1 > Score_player2):
                conn.send(("You are the winner of this game!! score = " + str(Score_player1)).encode(FORMAT))
            else:
                conn.send(("You lost this game!! score = " + str(Score_player1)).encode(FORMAT))
        else:
            if (Score_player2 > Score_player1):
                conn.send(("You are the winner of this game!! score = " + str(Score_player2)).encode(FORMAT))
            else:
                conn.send(("You lost this game!! score = " + str(Score_player2)).encode(FORMAT))
        conn.close()
    except:
        try: conn.send(("the connection was closed").encode(FORMAT))
        except: do = False
        print("Clients closed")
        Score_player1 = 0
        Score_player2 = 0
        nbrofthread = 0
        listt = []
        conn.close()
        time.sleep(2)
        Players = True

#sources used: 1,2 and 4
#def start() done by Jade El Masri
def start():
    # global nbrofthread
    global Players
    server.listen()#server begins listening for
        #incoming TCP requests
    print(f"[LISTENING] Server is listening on {SERVER}")
    Players = True
    while True:
        #condition used to limit the number of clients to 2
        if (threading.active_count() - 1 < 2 and Players == True):
            conn, addr = server.accept()#server waits on accept() for incoming
            #requests, new socket created on return
            #threading.Thread() allows the handle_client function to run in parallel for the two clients
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
            # nbrofthread = threading.active_count() - 1


print("[STARTING] server is starting...")
start()
#sources:
#https://www.youtube.com/watch?v=McoDjOCb2Zo---(source 1)
#https://www.geeksforgeeks.org/socket-programming-multi-threading-python/---(source 2)
#https://www.youtube.com/results?search_query=python+multiplayer+game ---(source 3)
#Everything on Moodle---(source 4)
#https://www.youtube.com/watch?v=xceTFWy_eag---(source 5)

