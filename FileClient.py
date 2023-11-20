# MP Client by S13 Group 9
# Names: Sayo, Trisha Alissandra
#        Wong, Krizchelle Danielle
#        Yung Cheng, Adrian

import socket
import threading
import json
import time

# Message Buffer Size
BUFFER_SIZE = 1024
# Connection Status
isConnected = False
# Server Address Variable
server_address = None

# Command Processing
def toServer(entry):
    global isConnected
    global server_address
    
    # Invalid Command (does not start with "/")
    if not entry.startswith('/'):
        print("Error: That is not a command! Type /? for help.")
        return
    
    input_line = entry.split()
    command = input_line[0]
    params = input_line[1:]
    
    # Join Command
    if command == "/join":
        if len(params) != 2:
            print("Invalid command syntax!!")
            print("Usage: /join <server_ip_add> <port>")
        else:
            try:
                server_address = (params[0], int(params[1]))
                
                # Send "Join" Command to Server
                client_socket.sendto(json.dumps({"command": "join"}).encode(), server_address)
                time.sleep(0.1)
                client_socket.settimeout(3)
                client_socket.recvfrom(BUFFER_SIZE)
                print("Connection to the Server is successful!")
                client_socket.settimeout(None)
                isConnected = True
                
            except Exception as e:
                print("Error: Connection to the Server has failed! Please check IP Address and Port Number.")
                print(f"More details: {str(e)}")
                server_address = None
                return
    # Leave Command
    elif command == "/leave":
        # Check if connected
        if isConnected:
            # No other parameters for command
            if len(params) > 0:
                print("Error: There should be no parameters for leave.")
                print("Usage: /leave")
            # Send "Leave" Command to Server
            else:
                client_socket.sendto(json.dumps({"command": "leave"}).encode(), server_address)
                print("Connection closed. Thank you!")
                isConnected = False
                server_address = None
        # No Connection Established yet
        else:
            print("Error: Disconnection failed. Please connect to the server first.")
    # Register Command
    elif command == "/register":
        # Check if Client is Connected to the Server
        if isConnected:
            # Incorrect syntax/parameters
            if len(params) != 1:
                print("Error: Command parameters do not match or is not allowed.")
                print("Usage: /register <handle>")
            # Send "Register" Command to Server
            else:
                client_socket.sendto(json.dumps({"command": "register", "handle": params[0]}).encode(), server_address)
        # No Connection Established yet
        else:
            print("Error: Please connect to the server first.")
    # Store Command
    elif command == "/store":
        if len(params) < 1:
            print("Usage: /store <filename>")
        else:
            filename = params[0]
            try:
                # Open the specified file in binary mode for reading
                with open(filename, 'rb') as file:
                    file_data = file.read()
                    # Send file data to the server with the command and filename
                    client_socket.sendto(json.dumps({"command": "store", "filename": filename, "data": file_data.decode('ISO-8859-1')}).encode(), server_address)
                    print(f"File {filename} sent to server.")
            except FileNotFoundError:
                # Handle the case where the file does not exist
                print(f"Error: File not found.")
            except Exception as e:
                # General exception handling
                print(f"Error: {str(e)}")
        pass
    # DIR Command
    elif command == "/dir":
        # TODO: Request File List from server
        pass
    # Get Command
    elif command == "/get":
        # TODO: Retrieve File from server
        pass
    # Help Command
    elif command == "/?":
        print("Connect to the server application:               /join <server_ip_add> <port>")
        print("Disconnect to the server application:            /leave")
        print("Register a unique handle or alias:               /register <handle>")
        print("Send file to server:                             /store <filename>")
        print("Request directory file list from server:         /dir")
        print("Fetch a file from a server:                      /get <filename>")
        print("Request command help:                            /?")
    # Invalid Command (starts with / but not a command)
    else:
        print("Command not found. Type /? for help.")

# Server Message Response
def fromServer(data):
    command = data['command']
    message = data['message']
    
    if command == "ping":
        ping_ack = {'command': 'ping'}
        client_socket.sendto(json.dumps(ping_ack).encode(), server_address)
        return

    # Print Response command from Server
    print(f"> {command}") # FOR DEBUGGING, REMOVE LATER
    # Print Response message from Server
    print(f"> {message}\n> ", end = "")

# Receive Response from Server  
def receive():
    global isConnected
    
    while True:
        if isConnected:
            try:
                message = client_socket.recvfrom(BUFFER_SIZE)
                data = json.loads(message[0].decode())
                fromServer(data)
            except ConnectionResetError:
                print("Error: Connection to the Server has been lost!")
                isConnected = False
            except Exception as e:
                print(f"Error: {str(e)}")
                
   
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

thread = threading.Thread(target = receive)
thread.start()

print("File Exchange Client")
print("Enter a command. Type /? for help")
 
while True:
    entry = input("> ")
    toServer(entry)