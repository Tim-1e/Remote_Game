import socket

def get_ip():
    Info = socket.gethostbyname_ex(socket.gethostname())
    ip = Info[2][0]
    print(ip)
    

    

get_ip()