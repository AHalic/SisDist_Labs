# Laboratório VI - Eleição e Coordenação Distribuída
O laboratório consiste em aprender mais sobre sistemas distribuídos não centralizados e o funcionamento de eleição nestes. 
O grupo é composto por Beatriz Maia, Iago Cerqueira e Sophie Dilhon. Para ver a análise em vídeo, acesse este [link]().

## Configuração
O programa foi desenvolvido com a linguagem Python 3.10, utilizando pacotes da biblioteca padrão de python.
Para configurar sua máquina, é necessário instalar as dependências utilizadas. Aconselha-se a criação de um ambiente {ambiente} da seguinte forma:

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
Para executar o sistema, basta rodar o comando abaixo para ativar um cliente. 

```sh
python client.py --port {p}  --host {h}
```
Neste caso 10 clientes são necessários para que a eleição inicie, então é necessário rodar esse comando paralelamente em 10 terminais.

## Implementação
A implementação consiste em clientes com o objetivo de mineirar blocos de uma blockchain, para isso, no entanto, é preciso eleger um cliente para funcionar como servidor (criar desafios e escolher vencedores). Após feita a eleição, os clientes podem se conectar ao servidor e obter os dados necessários para resolver o desafio criado.

A comunicação é feita usando o modelo Publisher/Subscriber, assim os clientes enviam mensagens ao broker, e todos os outros clientes já conectados a recebem. A eleição é iniciada assim que os 10 clientes se conectarem ao canal e enviarem uma mensagem de apresentação. Como os clientes não possuem acesso às mensagens enviadas anteriormente à sua conexão ao canal, após 10 segundos os clientes reenviam suas mensagens.

Uma vez que todos os clientes conheçam todos os outros clientes, a eleição se inicia, e esta consiste em gerar um número aleatório e enviá-lo ao canal de votos. Aquele cliente que sortear o maior número é o ganhador da eleição.

Finalmente, a mineração inicia-se. O controlador (cliente ganhador da eleição) cria um desafio e envia o Id e dificuldade dele na fila `sd/challenge`. Os clientes podem então iniciar a mineração, criando 6 Threads que buscam a solução paralelamente, ao encontrá-la a solução é enviada a fila `sd/solution`, que é lida pelo controlador. Caso a solução esteja correta, o vencedor e a solução são enviados na fila `sd/result` e um novo desafio é gerado.

## Análise
