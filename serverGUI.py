from tkinter import *
import socket
import threading

window = Tk()
window.title("Server")
window.geometry("300x400")
window.configure(background = "black")

title = Label(window, fg= "green", bg = "black", text = "SERVER", font = ("TimesNewRoman"))
title.pack(side = TOP)

start = Button(window, fg = "Blue", bg = "black", text = "Connect", font = ("TimesNewRoman", 10), command = lambda : start_server())
start.place(x = 95, y = 45)
stop = Button(window, fg = "Blue", bg = "Black", text = "Stop", font = ("TimesNewRoman", 10), command = lambda : stop_server())
stop.place(x = 165, y = 45)


host = Label(window, text = "Host: X.X.X.X", fg = "white", bg = "black", font = ("TimesNewRoman", 10))
host.place(x = 67, y = 80)
port = Label(window, text = "Port:XXXX", fg = "white", bg = "black", font = ("TimesNewRoman", 10))
port.place(x = 163, y = 80)

clientFrame = Frame(window, bg = "black")
lblLine = Label(clientFrame, text = "<< ====== Client List ====== >>", bg = "black", fg = "red", font = ("TimesNewRoman", 12) )
lblLine.pack(side = TOP)
scrollbar = Scrollbar(clientFrame)
scrollbar.pack(side = RIGHT, fill = Y)
Display = Text(clientFrame, height = 15, width = 30, bg = "black", fg = "white", font= ("TimesNewRoman", 10))
Display.pack(side = LEFT, fill = Y, padx = (5, 0))

scrollbar.config(command = Display.yview)
Display.config(yscrollcommand = scrollbar.set, state = "disabled")

clientFrame.pack(side = BOTTOM, pady = (5, 10))


server = None
HOST_ADDR = "127.0.0.1"
HOST_PORT = 1025
client_name = " "
clients = []
clients_names = []


# Start server function
def start_server():
    global server, HOST_ADDR, HOST_PORT # code is fine without this
    start.config(state = DISABLED)
    stop.config(state = NORMAL)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(socket.AF_INET)
    print(socket.SOCK_STREAM)

    server.bind((HOST_ADDR, HOST_PORT))
    server.listen(5)  # server is listening for client connection

    threading._start_new_thread(accept_clients, (server, " "))

    host["text"] = "Host: " + HOST_ADDR
    port["text"] = "Port: " + str(HOST_PORT)


# Stop server function
def stop_server():
    global server
    start.config(state = NORMAL)
    stop.config(state = DISABLED)

    host["text"] = "Host: X.X.X.X"
    port["text"] = "Port:XXXX"


def accept_clients(the_server, y):
    while True:
        client, addr = the_server.accept()
        clients.append(client)

        # use a thread so as not to clog the gui thread
        threading._start_new_thread(send_receive_client_message, (client, addr))


# Function to receive message from current client AND
# Send that message to other clients
def send_receive_client_message(client_connection, client_ip_addr):
    global server, client_name, clients, clients_addr
    client_msg = " "

    # send welcome message to client
    client_name  = client_connection.recv(4096).decode()
    welcome_msg = "Welcome " + client_name + ". Use 'exit' to quit"
    client_connection.send(welcome_msg.encode())

    clients_names.append(client_name)

    update_client_names_display(clients_names)  # update client names display


    while True:
        data = client_connection.recv(4096).decode()
        if not data: break
        if data == "exit":
            break

        client_msg = data

        idx = get_client_index(clients, client_connection)
        sending_client_name = clients_names[idx]

        for c in clients:
            if c != client_connection:
                server_msg = str(sending_client_name + "->" + client_msg)
                c.send(server_msg.encode())

    # find the client index then remove from both lists(client name list and connection list)
    idx = get_client_index(clients, client_connection)
    del clients_names[idx]
    del clients[idx]
    server_msg = "BYE!"
    client_connection.send(server_msg.encode())
    client_connection.close()

    update_client_names_display(clients_names)  # update client names display


# Return the index of the current client in the list of clients
def get_client_index(client_list, curr_client):
    idx = 0
    for conn in client_list:
        if conn == curr_client:
            break
        idx = idx + 1

    return idx


# Update client name display when a new client connects OR
# When a connected client disconnects
def update_client_names_display(name_list):
    Display.config(state=NORMAL)
    Display.delete('1.0', END)

    for c in name_list:
        Display.insert(END, c+"\n")
    Display.config(state=DISABLED)


window.mainloop()
