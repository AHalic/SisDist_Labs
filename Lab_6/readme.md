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

Em relação a mineração, percebe-se uma diferença muito grande entre os desafios. Foram feitos alguns testes considerando diferentes faixas de níveis para os desafios, sendo elas:
- 1 - 10
- 10 - 20
- 20 - 30
- 30 - 40

Com desafios de 1 a 10, todos os clientes eram capazes de encontrar soluções. Cada cliente utiliza 6 threads para encontra solução. Indepente do nível do desafio, todas as threads eram capazes de encontrar uma solução. Isso fazia com que multiplas mensagens eram enviadas para o tópico de *sd/result*, mas apenas a primeira era escolhida e enviada para *sd/solution*.

Quando a faixa mudava para 10-20, o comportamento era similar para os níveis inicias. Porém, com o aumento dos desafios, nem todas as threads foram capazes de encontrarem soluções. O que se percebeu foi que alguns clientes conseguiam encontrar algumas soluções em algumas threads. Isso fazia com que a thread enviasse a mensagem para o tópico *sd/result*. Tanto as outras threads do próprio cliente quanto a de outros eram capazes de receberem mensagens desse tópico, por ter dado *subscribe*, e devido a isso conseguem perceber que uma solução foi enviada. Logo, nao há necessidade de procurar outras soluções e a busca é interrompida.

Quando a faixa mudava para 20-30, o desafio já começava a ficar muito mais difícil. Nos dois casos anteriores, o tempo era de milisegundos, enquanto nesses desafios já começava a demorar na escala de segundos. Geralmente um cliente conseguia encontra a solução localmente em uma única thread, sendo as outras sempre interrompidas. Teve casos também que demoravam muito, e devido a isso interrompemos manualmente (ctrl+c). Era difícil vários clientes encontrarem soluçoes simultaneamente. 

Com a faixa de nível 30-40, o tempo para resolver um desafio aumentava consideravelmente, ao ponto em que todos os testes foram forçadamente interrompidos após 10 minutos por não terem encontrado soluçoes. 

Em relação a implementação, uma análise a ser feita é como é feita a inicialização. Quando um cliente é inicializado, ele manda uma mensagem para a fila do tópico *sd/init*. Uma vez que clientes vão entrando, eles não tem acesso a essa mensagem. Para contornar isso, foi feito que cada cliente fica constantemente mandando uma mensagem. Dessa forma, se um cliente entrar depois, os clientes que entraram antes continuam mandando mensagens e ele é capaz de recebé-las, conhecendo então os clientes existentes. O cliente fica mandando mensagem a cada 5s. Isso talvez não seja a implementação mais ideal, visto que pode lotar de mensagens idênticas. Quando o intervalo era maior, também ocorria casos em que o último cliente mandava mensagem para init, os outros capitavam e paravam de mandar mensagems. Se o último cliente não tinha recebido mensagens de todos os clientes devido ao intervalo de tempo, ocorria uma situação de deadlock, em que o último esperava mensagens de outros clientes (achando que não chegou no limite), enquanto os outros que já tinham recebido a última mensagem para iniciar estavam esperando todos votarem. O último por não ter recebido todas as mensagens, não era capaz de votar. Ele ficava eternamente mandando mensagem. Idealmente, seria legal trabalhar nisso para que situaçoes de deadlock não ocorressem. 
