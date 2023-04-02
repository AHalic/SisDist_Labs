# Laboratório I – Paralelismo de Processos e Threads

O laboratório consiste em realizar um merge sort utilizando threads. 

## Configuração
O programa foi desenvolvido com a linguagem Python 3.10, utilizando pacotes da biblioteca padrão de python, pandas e matplotlib. Para configurar sua máquina, é necessário instalar as dependências utilizadas. Aconselha se a criação de um ambiente {ambiente} da seguinte forma:

```sh
python -m venv {ambiente}
```

no qual {ambiente} pode ser qualquer nome. Após a criação do ambiente, é necessário ativá-lo. Para ativar no linux ou mac, execute o seguinte comando:

```sh
source /{ambiente}/bin/activate
```

para ativar no windows, execute o seguinte comando:

```sh
.\{ambiente}\Scripts\activate
```

no qual {ambiente} deve ser substituído pelo nome do ambiente criado anteriormente. Após isso, instale as dependências utilizando

```sh
pip install -r requirements.txt
```

## Execução
O programa recebe dois argumentos como entrada, sendo eles uma quantidade **k** de threads que serão geradas inicialmente e um tamanho **n** do array.
Para executar o programa basta rodar o seguinte comando no terminal:

```sh
python main.py k n
```

## Desenvolvimento

A implementação pode ser dividida em três partes:

- Geração dos arrays
- Ordenação dos arrays iniciais
- *Merge* de arrays de forma ordenada

Para ambas etapas, foi utilizada uma classe customizada de threads. Esta classe herda da classe Thread do pacote threading. O seu propósito é para armazenamento do resultado de cada função executada nas threads.

### Geração dos arrays

Esta etapa consiste na criação dos arrays de quantidade **n** e na divisão deles em **k** arrays. Como essa parte é o input para o algoritmo de *mergesort*, ela não é considerada na contabilização da duração do programa.

### Ordenação dos arrays iniciais

Essa etapa consiste na criação de **k** threads. As threads são primeiro criadas, para depois serem iniciadas. Após todas as threads terminarem, os vetores ordenados são obtidos.

### *Merge* de arrays de forma ordenada

Essa etapa consiste na junção dos arrays de forma ordenada. A junção dos vetores são feitas em pares, em que cada junção é feito por uma thread. Se há uma quantidade impar de vetores, o último vetor não é considerado para junção de threads até a última junção. 

Essa etapa é dividida da seguinte forma:
```python
# Merge arrays
while len(sorted_arrays) > 1:
    sorted_arrays = merge_arrays_threads(sorted_arrays)
```
Desta forma, é feito a primeira junção e atribuido um nome aos novos vetores. Caso há mais que 1 vetor, significa que ainda tem como fazer junção e o processo continua. 

## Análise

## Referencias

https://docs.python.org/3/library/threading.html
https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.ThreadPool +  https://stackoverflow.com/questions/69005467/how-to-get-return-values-of-multi-threads-once-one-of-them-is-finished
https://superfastpython.com/thread-return-values/#Need_to_Return_Values_From_a_Thread