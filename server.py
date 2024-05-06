import socket
import ssl

SMTP_SERVER = "localhost"
SMTP_PORT = 25

#! Send warning email if BCC is detected
def sendWarningEmail(header):
    #! From Practical 6
    sender_email = "u22534599@tuks.co.za"
    recipient_email = "u22534599@tuks.co.za"
    subject = f"[BCC Warning] {header}"
    
    message = f"From: {sender_email}\r\nTo: {recipient_email}\r\nSubject: {subject}\r\n\r\n"
    message += "\r\n.\r\n"
    # message += "You have received a BCC email.\r\n.\r\n"
    
    try:
        smtp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        smtp_socket.connect((SMTP_SERVER, SMTP_PORT))
        smtp_socket.settimeout(10)

        response = smtp_socket.recv(1024).decode()
        print("Server Response:", response)

        smtp_socket.send(b"HELO localhost\r\n")
        response = smtp_socket.recv(1024).decode()
        print("HELO Response:", response)
        
        smtp_socket.send(f"MAIL FROM:<{sender_email}>\r\n".encode())
        response = smtp_socket.recv(1024).decode()
        print("MAIL FROM Response:", response)
        
        smtp_socket.send(f"RCPT TO:<{recipient_email}>\r\n".encode())
        response = smtp_socket.recv(1024).decode()
        print("RCPT TO Response:", response)
        
        smtp_socket.send(b"DATA\r\n")
        response = smtp_socket.recv(1024).decode()
        print("DATA Response:", response)
        
        smtp_socket.send(message.encode())
        response = smtp_socket.recv(1024).decode()
        print("Message Response:", response)
        
        smtp_socket.send(b"QUIT\r\n")
        response = smtp_socket.recv(1024).decode()
        print("QUIT Response:", response)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        smtp_socket.close()

#! Class for POP3 client
class clientPOP3:
    def __init__(self, server, port=995):
        self.server = server
        self.port = port
        self.sock = None

    def connect(self):
        context = ssl.create_default_context()
        with socket.create_connection((self.server, self.port)) as sock:
            self.sock = context.wrap_socket(sock, server_hostname=self.server)
            response = self.sock.recv(1024).decode()
            if(debugFlag):
                print(response)
    
    #* Helper function
    def sendToServer(self, command):
        self.sock.send(f"{command}\r\n".encode())
        return self.sock.recv(1024).decode()
    
    def login(self, username, password):
        self.sendToServer(f"USER {username}")
        self.sendToServer(f"PASS {password}")

    def getEmail(self, index):
        response = self.sendToServer(f"RETR {index}")
        if(debugFlag):
            print(response)
        return response
        
    def getIndex(self):
        return int(self.sendToServer("STAT").split(" ")[1])

    def quit(self):
        if(debugFlag):
            print(self.sendToServer("QUIT"))
        else:    
            self.sendToServer("QUIT")
        self.sock.close()

#! If you want to see the server responses, set debugFlag to True
debugFlag = False

#! Ensures constant monitoring of the email server
while True:
    #* Connect to the email server
    client = clientPOP3("pop.gmail.com", 995)
    client.connect()
    #! Change during demo session
    client.login("u22534599@tuks.co.za", "tempPassword1234")
    #* Get index of latest email
    numMessages = client.getIndex()
    email = client.getEmail(numMessages)
    client.quit()

    #* Check if the email contains BCC
    if("Bcc: Donatello Carboni <u22534599@tuks.co.za>" in email):
        #* Extract the subject
        subject = email.split("\r\n")[5].split(":")[1]
        #* Send warning email
        sendWarningEmail(subject)