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

entradas = [sys.stdin] #define a lista de I/O de interesse (jah inclui a entrada padrao)
lock = threading.Lock() #cria um lock para o acesso ao dicionario

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

class dic:
    def __init__ (self):
        dicionarioInicial = {}
    
    def iniciaDicionario(self):
        with open("entrada.json","r") as openfile:
            self.dicionarioInicial = json.load(openfile)
        return self.dicionarioInicial
    
    def salvaDicionario(self, dicionario):
        with open("entrada.json", "w") as outfile:
            json.dump(dicionario, outfile)

class ler:
    def __init__(self, dicionario, chave):
        self.dicionario = dicionario
        self.chave = chave
        
    def execucaoLer(self):
        if self.chave in self.dicionario:
            valor = self.dicionario[self.chave]
            return valor
        return '[]'

class escrever:
    def __init__(self, dicionario, chave, valor):
        self.dicionario = dicionario
        self.chave = chave
        self.valor = valor
        
    def execucaoEscrever(self):
        if self.chave in self.dicionario:
            self.dicionario[self.chave].append(self.valor)
            self.dicionario[self.chave].sort()
        else:
            self.dicionario[self.chave] = (self.valor).split()

#Recebe mensagens e as envia de volta para o cliente (ate o cliente finalizar)
#Entrada: socket da conexao e endereco do cliente
def atendeRequisicoes(clisock, endr, dicionario):
    while True:
        data = clisock.recv(1024) #recebe dados do cliente
        if not data: #dados vazios: cliente encerrou
            print(str(endr) + '-> encerrou')
            clisock.close() #encerra a conexao com o cliente
            return 

        elif str(data, encoding='utf-8') == 'leitura': #cliente solicitou a leitura
            chave = clisock.recv(1024) #chave enviada pelo cliente
            criaLeitura = ler(dicionario, str(chave, encoding='utf-8')) #cria a classe para leitura
            saida = criaLeitura.execucaoLer() 
            clisock.send(str(saida).encode('utf-8'))#(" ".join(saida)).encode('utf-8')) #envia ao cliente o valor obtido
                    
        elif str(data, encoding='utf-8') == 'escrita': 
            chave = clisock.recv(1024) #chave enviada pelo cliente
            valor = clisock.recv(1024) #valor enviado pelo cliente
            criaEscrita = escrever(dicionario, str(chave, encoding='utf-8'), str(valor, encoding='utf-8')) #cria a classe para escrita
            lock.acquire() #lock para que ninguem leia enquanto escreve
            saida = criaEscrita.execucaoEscrever()
            lock.release()
            clisock.send('Valores inseridos com sucesso!'.encode('utf-8')) #confirma insercao
        
#Inicializa e implementa o loop principal (infinito) do servidor
def main():
    clientes=[] #armazena as threads criadas para fazer join
    sock = iniciaServidor()
    dicSalvo = dic()
    dicionario = dicSalvo.iniciaDicionario()
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
                    dicSalvo.salvaDicionario(dicionario)
                    sock.close()
                    sys.exit()
                elif cmd == 'delete': #outro exemplo de comando para o servidor
                    chave = input('Digite a chave a ser excluida ou "reset" para excluir todo dicionario: ')
                    if chave == 'reset':
                        lock.acquire()
                        dicionario.clear()
                        lock.release()
                        print('Dicionario excluido com sucesso!')
                    else:
                        lock.acquire()
                        del dicionario[chave]
                        lock.release()
                        print('Chave excluida com sucesso!')
                elif cmd == 'salva': #outro exemplo de comando para o servidor
                    dicSalvo.salvaDicionario(dicionario)
                    print('Dicionario salvo!')
                else:
                    print('Comando invalido! Comandos validos: "fim", "delete" e "salva"')
main()
