#servidor de echo: lado cliente
import socket

HOST = 'localhost' # maquina onde esta o servidor
PORT = 10000       # porta que o servidor esta escutando

#Cria um socket de cliente e conecta-se ao servidor.
#Saida: socket criado
def iniciaCliente():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #cria socket
	sock.connect((HOST, PORT)) #conecta-se com o servidor

	return sock

"""Recebe a acao que o usuario deseja realizar e envia ao servidor as informacoes necessarias para realiza-la 
Caso leitura: envia a chave solicitada pelo usuario 
Caso escrita: envia a chave e o valor a ser escrito
Saida: resposta do servidor
Caso leitura: o valor da chave enviada
Caso escrita: valores inseridos com sucesso
Entrada: socket conectado ao servidor"""
def fazRequisicoes(sock):
	#le as mensagens do usuario ate ele digitar 'fim'
	while True: 
		acao = input("Digite a acao que deseja realizar 'leitura', 'escrita' ou 'fim' para terminar: ")
		if acao == 'fim': break

		sock.send(acao.encode('utf-8')) #envia a mensagem do usuario para o servidor
		if acao == 'leitura': 
			chave = input('Digite a chave a ser lida: ')
			sock.send(chave.encode('utf-8'))
	
		elif acao == 'escrita': 
			chave = input('Digite a chave: ')
			sock.send(chave.encode('utf-8'))
			valor = input('Digite o valor a ser inserido: ')
			sock.send(valor.encode('utf-8'))
	
		resultado = sock.recv(1024) #espera a resposta do servidor

		print(str(resultado, encoding='utf-8')) #imprime a mensagem recebida

	sock.close() #encerra a conexao

#Funcao principal do cliente
def main():
	#inicia o cliente
	sock = iniciaCliente()
	#interage com o servidor ate encerrar
	fazRequisicoes(sock)

main()