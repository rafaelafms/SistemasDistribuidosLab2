#Lado servidor
#Finalizacao do lado do servidor
#Multithreading (usa join para esperar as threads terminarem apos digitar 'fim' no servidor)
import socket
import select
import json
import sys
import threading

#define a localizacao do servidor
HOST = '' # vazio indica que podera receber requisicoes a partir de qq interface de rede da maquina
PORT = 10000 # porta de acesso

#define a lista de I/O de interesse (jah inclui a entrada padrao)
entradas = [sys.stdin]
#cria um lock para o acesso ao dicionario
lock = threading.Lock()

#Cria um socket de servidor e o coloca em modo de espera por conexoes
#Saida: o socket criado
def iniciaServidor():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #cria o socket 
    sock.bind((HOST, PORT)) #vincula a localizacao do servidor
    sock.listen(5) #coloca-se em modo de espera por conexoes
    sock.setblocking(False) #configura o socket para o modo nao-bloqueante
    entradas.append(sock) #inclui o socket principal na lista de entradas de interesse

    return sock

#Aceita o pedido de conexao de um cliente
#Entrada: o socket do servidor
#Saida: o novo socket da conexao e o endereco do cliente
def aceitaConexao(sock):
    clisock, endr = sock.accept() #estabelece conexao com o proximo cliente

    return clisock, endr

def iniciaDicionario():
    dicionario = {}
    with open("entrada.json","r") as openfile:
        dicionario = json.load(openfile)
    return dicionario

def salvaDicionario(dicionario):
    with open("entrada.json", "w") as outfile:
        json.dump(dicionario, outfile)
    return

class ler:
    def __init__(self, dicionario, chave):
        self.dicionario = dicionario
        self.chave = chave
        
    def execucao(self, dicionario, chave):
        if self.chave in self.dicionario:
            valor = self.dicionario[chave]
            return valor
        return '[]'

class escrever:
    def __init__(self, dicionario, chave, valor):
        self.dicionario = dicionario
        self.chave = chave
        self.valor = valor
        
    def execucao(self, dicionario, chave, valor):
        if chave in dicionario:
            self.dicionario[chave].append(self.valor)
            self.dicionario[chave].sort()
        else:
            self.dicionario[chave] = (self.valor).split()

#Recebe mensagens e as envia de volta para o cliente (ate o cliente finalizar)
#Entrada: socket da conexao e endereco do cliente
def atendeRequisicoes(clisock, endr, dicionario):
    while True:
        data = clisock.recv(1024) #recebe dados do cliente
        if not data: #dados vazios: cliente encerrou
            print(str(endr) + '-> encerrou')
            clisock.close() #encerra a conexao com o cliente
            return 
        elif str(data, encoding='utf-8') == 'leitura': 
            chave = clisock.recv(1024)
            saida1 = ler(dicionario, str(chave, encoding='utf-8'))
            lock.acquire()
            saida = saida1.execucao(dicionario, str(chave, encoding='utf-8'))
            lock.release()
            clisock.send((" ".join(saida)).encode('utf-8'))
                    
        elif str(data, encoding='utf-8') == 'escrita': 
            chave = clisock.recv(1024)
            valor = clisock.recv(1024)
            saida1 = escrever(dicionario, str(chave, encoding='utf-8'), str(valor, encoding='utf-8'))
            lock.acquire()
            saida = saida1.execucao(dicionario, str(chave, encoding='utf-8'), str(valor, encoding='utf-8'))
            lock.release()
            print(dicionario)
            clisock.send('Valores inseridos com sucesso'.encode('utf-8'))
        
#Inicializa e implementa o loop principal (infinito) do servidor
def main():
    clientes=[] #armazena as threads criadas para fazer join
    sock = iniciaServidor()
    dicionario = iniciaDicionario()
    print("Pronto para receber conexoes...")
    while True:
        #espera por qualquer entrada de interesse
        leitura, escrita, excecao = select.select(entradas, [], [])
        #tratar todas as entradas prontas
        for pronto in leitura:
            if pronto == sock:  #pedido novo de conexao
                clisock, endr = aceitaConexao(sock)
                print ('Conectado com: ', endr)
                cliente = threading.Thread(target=atendeRequisicoes, args=(clisock,endr,dicionario)) #cria nova thread para atender o cliente
                cliente.start()
                clientes.append(cliente) #armazena a referencia da thread para usar com join()
            elif pronto == sys.stdin: #entrada padrao
                cmd = input()
                if cmd == 'fim': #solicitacao de finalizacao do servidor
                    for c in clientes: #aguarda todas as threads terminarem
                        c.join()
                    salvaDicionario(dicionario)
                    sock.close()
                    sys.exit()
                elif cmd == 'delete': #outro exemplo de comando para o servidor
                    chave = input('Digite a chave a ser excluida: ')
                    lock.acquire()
                    del dicionario[chave]
                    lock.release()
                    print('Chave excluida com sucesso!')
                elif cmd == 'salva': #outro exemplo de comando para o servidor
                    salvaDicionario(dicionario)
                    print('Dicionario salvo!')
main()
