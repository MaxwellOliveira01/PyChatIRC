import socket
import tkinter as tk
import threading

def ExtractMessage(data):

    if len(data) <= 0:
        return

    if "NOTICE" in data: 
        return
    
    if "JOIN" in data:
        return

    if "MOTD" in data:
        return

    if "PRIVMSG" in data:
        parts = data.split(" ", 3)
        if len(parts) >= 4:
            sender_info, message_type, destination, message = parts[0], parts[1], parts[2], parts[3]
            sender_parts = sender_info.split("!")
            sender_name = sender_parts[0][1:]  # remove o ':' no início do nome do remetente
            message = message[1:]  # remova o ':' no início da mensagem
            #print(f"{sender_name} disse para {destination}: {message}", end="")
            AddMsgToViewArea(f"{sender_name} disse para {destination}: {message}")
    else:
        '''
        tratar os seguintes erros:
        401 - ERR_NOSUCHNICK: O apelido especificado não foi encontrado no servidor.
        403 - ERR_NOSUCHCHANNEL: O canal especificado não foi encontrado no servidor.
        404 - ERR_CANNOTSENDTOCHAN: Não é possível enviar mensagens para o canal especificado (geralmente devido a restrições ou configurações específicas do canal).
        405 - ERR_TOOMANYCHANNELS: O usuário já está em muitos canais e não pode entrar em mais um.
        406 - ERR_WASNOSUCHNICK: O apelido ao qual se está respondendo não foi encontrado no servidor.
        407 - ERR_TOOMANYTARGETS: Muitos destinos foram especificados na mesma mensagem.
        471 - ERR_CHANNELISFULL: O canal está cheio e não é possível entrar.
        473 - ERR_INVITEONLYCHAN: O canal é somente para convidados e o usuário não tem permissão para entrar sem um convite.
        474 - ERR_BANNEDFROMCHAN: O usuário está banido do canal e não pode entrar.
        475 - ERR_BADCHANNELKEY: A senha do canal especificada está incorreta.
        481 - ERR_NOPRIVILEGES: O usuário não tem privilégios suficientes para executar a ação desejada.
        482 - ERR_CHANOPRIVSNEEDED: São necessários privilégios de operador do canal (channel operator) para executar a ação desejada.
        483 - ERR_CANTKILLSERVER: Não é permitido desconectar o servidor ou matar a conexão do servidor.
        501 - ERR_UMODEUNKNOWNFLAG: O modo de usuário especificado não é reconhecido.
        502 - ERR_USERSDONTMATCH: Os modos de usuário não coincidem.
        '''
        AddMsgToViewArea(data)

def ConnectAndAuthenticate(irc, nick):
    # Envie as informações de login para o servidor
    irc.send(f"USER {nick} 0 * :{nick}\r\n".encode())
    irc.send(f"NICK {nick}\r\n".encode())

    while True:
        data = irc.recv(2048).decode("UTF-8")
        
        if len(data) <= 0:
            continue
        
        if "004" in data:
            # Autenticado com sucesso, pode prosseguir
            break

        if "433" in data:
            AddMsgToViewArea("Nickname já está em uso!!!")
            exit(0)
    print("Conectado com sucesso")

def JoinChannel(irc, channelName):
    irc.send(f"JOIN :{channelName}\r\n".encode())

    while True:
        data = irc.recv(2048).decode("UTF-8")

        if len(data) <= 0:
            continue

        #print(data)
        AddMsgToViewArea(data)
        
        '''
        if f"JOIN :{channelName}" in data:
            # entrou com sucesso!!
            break
        '''

        # O servidor retorna o seguinte:
        # o join do if acima
        # a lista de usuários online
        # e dps o END dessa lista, que é o if abaixo

        if "End" in data and "/NAMES" in data:
            break

    #print(f"Entrou no canal {channelName} com sucesso")
    AddMsgToViewArea(f"Entrou no canal {channelName} com sucesso")

def SendMessage(irc, source, sink, msg):
    if not msg:
        return
    # if sink[0] == '#': --> mensagem para um canal
    irc.send(f"PRIVMSG {sink} :{msg}\r\n".encode())
    AddMsgToViewArea(f'{source} disse para {sink}: {msg}')
    inputArea.delete(0, tk.END)

def SendMessageAux(event = None):
    return SendMessage(irc, nickname, "#MeuCanal", inputArea.get())

def AddMsgToViewArea(msg):
    if msg[-1] != '\n':
        msg = msg + '\n'
    messages.append(msg)
    messagesArea.config(state = tk.NORMAL)
    messagesArea.insert(tk.END, msg)
    messagesArea.config(state = tk.DISABLED)
    messagesArea.see(tk.END)
    
def IRCLoop():
    while True:
        data = irc.recv(2048).decode("UTF-8")
        
        if "PING" in data:
            irc.send("PONG :pingis\r\n".encode()) 
        
        ExtractMessage(data)

messages = []
onlineUsers = []

mainWindow = tk.Tk()
mainWindow.title("PyChatIRC")
mainWindow.geometry("1130x500")
mainWindow.resizable(width = False, height = False)

messagesArea = tk.Text(mainWindow, state = tk.DISABLED, height = 29, width = 115)
messagesArea.grid(row = 0, column = 0, columnspan = 3, sticky = 'ew')

inputArea = tk.Entry(mainWindow, width = 160)
inputArea.grid(row = 2, column = 0, stick = 'ew')
inputArea.bind("<Return>", SendMessageAux)

#sendMessageButton = tk.Button(mainWindow, text = "Submit", command = SendMessageAux)
#sendMessageButton.grid(row = 2, column = 1)

onlineUsersArea = tk.Text(mainWindow, state = tk.DISABLED, height = 29, width = 20)
onlineUsersArea.grid(row = 0, column = 4, columnspan = 1, sticky = 'ew')

mainScroolBar = tk.Scrollbar(mainWindow, command = onlineUsersArea.yview)
mainScroolBar.grid(row = 0, column = 5, stick = 'ns')
onlineUsersArea.config(yscrollcommand = mainScroolBar.set)

# Informações básicas a serem usadas
server = "localhost"
port = 6667
channel = "#MeuCanal"
nickname = "PythonUser4"

# Crie um socket e conecta ao servidor IRC local
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.connect((server, port))

ConnectAndAuthenticate(irc, nickname)
JoinChannel(irc, channel)

ircThread = threading.Thread(target = IRCLoop, daemon = True)
ircThread.start()

mainWindow.mainloop()