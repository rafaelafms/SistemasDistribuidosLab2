#Lado servidor
#Finalizacao do lado do servidor
#Multithreading (usa join para esperar as threads terminarem apos digitar 'fim' no servidor)
import socket
import select
import sys
import threading

#define a localizacao do servidor
HOST = '' # vazio indica que podera receber requisicoes a partir de qq interface de rede da maquina
PORT = 10000 # porta de acesso

#define a lista de I/O de interesse (jah inclui a entrada padrao)
entradas = [sys.stdin]
#armazena o dicionario
dicionario = {}
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

#Recebe mensagens e as envia de volta para o cliente (ate o cliente finalizar)
#Entrada: socket da conexao e endereco do cliente
def atendeRequisicoes(clisock, endr):
	while True:
		data = clisock.recv(1024) #recebe dados do cliente
		if not data: #dados vazios: cliente encerrou
			print(str(endr) + '-> encerrou')
			clisock.close() #encerra a conexao com o cliente
			return 
		elif str(data, encoding='utf-8') == 'leitura': 
			chave = clisock.recv(1024)
			lock.acquire()
			if str(chave, encoding='utf-8') in dicionario:
				valor = dicionario[str(chave, encoding='utf-8')]
				clisock.send((", ".join(valor)).encode('utf-8')) 
			else:
				clisock.send('[]'.encode('utf-8'))
			lock.release()
    				
		elif str(data, encoding='utf-8') == 'escrita': 
			chave = clisock.recv(1024)
			valor = clisock.recv(1024)

			lock.acquire()
			if str(chave, encoding='utf-8') in dicionario:
				dicionario[str(chave, encoding='utf-8')].append(str(valor, encoding='utf-8'))
				dicionario[str(chave, encoding='utf-8')].sort()
			else:
				dicionario[str(chave, encoding='utf-8')] = [str(valor, encoding='utf-8')]
			lock.release()
			print(dicionario)
			clisock.send('Valores inseridos com sucesso'.encode('utf-8'))
		
#Inicializa e implementa o loop principal (infinito) do servidor
def main():
	clientes=[] #armazena as threads criadas para fazer join
	sock = iniciaServidor()
	print("Pronto para receber conexoes...")
	while True:
		#espera por qualquer entrada de interesse
		leitura, escrita, excecao = select.select(entradas, [], [])
		#tratar todas as entradas prontas
		for pronto in leitura:
			if pronto == sock:  #pedido novo de conexao
				clisock, endr = aceitaConexao(sock)
				print ('Conectado com: ', endr)
				cliente = threading.Thread(target=atendeRequisicoes, args=(clisock,endr)) #cria nova thread para atender o cliente
				cliente.start()
				clientes.append(cliente) #armazena a referencia da thread para usar com join()
			elif pronto == sys.stdin: #entrada padrao
				cmd = input()
				if cmd == 'fim': #solicitacao de finalizacao do servidor
					for c in clientes: #aguarda todas as threads terminarem
						c.join()
					sock.close()
					sys.exit()
				elif cmd == 'delete': #outro exemplo de comando para o servidor
					chave = input('Digite a chave a ser excluida: ')
					lock.acquire()
					del dicionario[chave]
					lock.release()
					print(dicionario)
					print('Chave excluida com sucesso')

main()
