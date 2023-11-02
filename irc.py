import socket
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
            print(f"{sender_name} disse para {destination}: {message}", end="")
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
        print("data = ", data)

def ConnectAndAuthenticate(socket, nick):
    # Envie as informações de login para o servidor
    socket.send(f"USER {nick} 0 * :{nick}\r\n".encode())
    socket.send(f"NICK {nick}\r\n".encode())

    while True:
        data = socket.recv(2048).decode("UTF-8")
        
        if len(data) <= 0:
            continue
        
        if "004" in data:
            # Autenticado com sucesso, pode prosseguir
            break

        if "433" in data:
            print("Nickname já está em uso!!!")
            exit(0)
    
    print("Conectado com sucesso")

def JoinChannel(socket, channelName):
    socket.send(f"JOIN :{channelName}\r\n".encode())

    while True:
        data = socket.recv(2048).decode("UTF-8")

        if len(data) <= 0:
            continue

        print(data)
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

    print(f"Entrou no canal {channelName} com sucesso")

def SendMessage(source, sink, msg):
    # if sink[0] == '#': --> mensagem para um canal
    print(f'{source} disse para {sink}: {msg}')
    irc.send(f"PRIVMSG {sink} :{msg}\r\n".encode())

def ReadUserInputThenSendMessage():
    
    # meu nick, destinatário, mensagem
    # o nick já é 'fixo', correto? entao nao precisaria pedir aqui
    # o destinatário pode ser usuário ou canal. Canal começa com '#'
    # por fim a mensagem, qlq coisa

    while True:
        data = input().split(" ")
        if len(data) < 2:
            print("Mensagem inválida")
            continue
        sink = data[0]
        msg = " ".join(data[1:])
        SendMessage(nickname, sink, msg)

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

inputThread = threading.Thread(target = ReadUserInputThenSendMessage, daemon = True)
inputThread.start()

while True:
    data = irc.recv(2048).decode("UTF-8")
    
    if "PING" in data:
        irc.send("PONG :pingis\r\n".encode()) 
    
    ExtractMessage(data)