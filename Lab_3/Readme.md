# Laboratório III - Chamada de Procedimento Remoto
O laboratório consiste em aprender mais sobre a troca de mensagens entre processos com o chamado gRPC. 
O grupo é composto por Beatriz Maia, Iago Cerqueira e Sophie Dilhon. Para ver a análise em vídeo, acesse este link.

## Configuração
O programa foi desenvolvido com a linguagem Python 3.10, utilizando pacotes da biblioteca padrão de python e pacotes referentes a implementação do grpc. 
Para configurar sua máquina, é necessário instalar as dependências utilizadas. Aconselha se a criação de um ambiente {ambiente} da seguinte forma:

```sh
python -m venv {ambiente}
```

em que {ambiente} pode ser qualquer nome de sua escolha. Após a criação do ambiente, é necessário ativá-lo. Para ativar no linux ou mac, execute o seguinte comando:

```sh
source /{ambiente}/bin/activate
```

para ativar no windows, execute o seguinte comando:

```sh
.\{ambiente}\Scripts\activate
```

Após isso, instale as dependências utilizando

```sh
pip install -r requirements.txt
```

## Execução
Para executar o sistema, primeiro deve-se rodar o comando abaixo no terminal
```sh
python -m grpc_tools.protoc --proto_path=. ./mine_grpc.proto --python_out=. --grpc_python_out=.
```
Após isso, dois arquivos serão criados: 'mine_grpc_pb2.py' e 'mine_grpc_pb2_grpc.py', que são utilizados pelo servidor e cliente.

Por fim, execute o servidor e o cliente em terminais separados, e nessa ordem
```sh
python mine_server.py
python mine_client.py
```

## Implementação
A implementação consiste em clientes com o objetivo de mineirar blocos de uma blockchain, para isso, os clientes utilizam o gRPC para
se conectar ao servidor e obter os dados necessários para resolver o desafio criado.

Para a passagem de dados de um sistema ao outro, o gRPC utiliza um mecanismo de serialização chamado protobuf. 
O Arquivo de extensão _.proto_ representa a estruturação dos dados, e foi fornecido pelo professor.

Em seguida, foi implementado o servidor [mine_server.py](mine_server.py), este roda na porta _8080_ e é responsável por criar e armazenar os desafios. 
Ao receber uma tentativa de solução, o servidor verifica esta aplicando-a a hash SHA-1 e convertendo-a em binários, para então conferir se os primeiros x bits (x = dificuldade)
são iguais à zero. Caso o cliente tenha sucesso, os dados desse desafio são editados, e um novo desafio é criado.

Além disso, foi implementado o cliente [mine_client.py](mine_client.py), que se conecta ao servidor. O cliente possui algumas opções de ações, que recebem dados do servidor.
Ao selecionar a opção _mine_, o cliente inicia de fato a mineração do bloco (resolução do desafio). Para isso, ele se comunica com o servidor para obter os dados referentes ao desafio pendente,
e abre 6 Threads que irão procurar soluções em paralelo. Cada thread cria uma solução aleatória (um valor de 0 a 10000000) e valida a solução da mesma forma que o servidor valida 
(descrito no paragrafo a cima), a cada 5 tentativas a thread se comunica com o servidor para verificar se o desafio ainda está pendente. Caso não esteja mais, a Thread termina sua execução.
Threads podem buscar e testar mesmas soluções, uma vez que não foi implementada comunicação entre elas, podendo inclusive submeter soluções vencedoras ao servidor ao mesmo tempo, neste caso,
apenas a primeira recebida pelo servidor será registrada como a solução do desafio.
