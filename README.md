# Projeto Final — Escalonamento em Máquinas Paralelas Idênticas

Este projeto implementa uma meta-heurística VND (*Variable Neighbourhood Descent*) para o Problema de Escalonamento em Máquinas Paralelas Idênticas, representado por:

```txt
P || Cmax
```

O objetivo é distribuir um conjunto de tarefas entre máquinas idênticas de modo a minimizar o `Cmax`, também chamado de *makespan*. O `Cmax` corresponde à carga da máquina que termina por último.

---

## Requisitos

O projeto foi implementado em Python e utiliza apenas bibliotecas padrão da linguagem.

### Requisitos necessários

* Python 3 instalado.

Não é necessário instalar bibliotecas externas.

---

## Execução do programa

Para executar o código principal no Windows PowerShell:

```powershell
py .\scheduling_vnd.py
```

ou:

```powershell
python .\scheduling_vnd.py
```

Em Linux/macOS:

```bash
python3 scheduling_vnd.py
```

Durante a execução, o programa:

1. gera automaticamente as instâncias de teste;
2. salva essas instâncias em arquivos `.txt`;
3. executa a heurística construtiva LPT;
4. aplica o VND com duas vizinhanças;
5. apresenta uma tabela com os resultados computacionais;
6. exibe um resumo final com os principais itens exigidos na Atividade A2.

As instâncias são geradas automaticamente. Portanto, não é necessário fornecer arquivos de entrada manualmente.

Ao executar o script, será criada a pasta:

```txt
instancias_geradas/
```

Essa pasta contém os arquivos das instâncias utilizadas nos experimentos.

Para salvar a saída completa da execução em um arquivo de texto:

```powershell
py .\scheduling_vnd.py > resultados_execucao.txt
```

ou, em Linux/macOS:

```bash
python3 scheduling_vnd.py > resultados_execucao.txt
```

---

## Organização geral da implementação

A implementação contém os principais elementos pedidos na Atividade A2:

* representação da solução por vetor de alocação, cargas das máquinas e valor de `Cmax`;
* função objetivo `f(s) = Cmax`;
* heurística construtiva LPT (*Longest Processing Time First*);
* vizinhança `N1_realocacao`, baseada na realocação de uma tarefa para outra máquina;
* vizinhança `N2_swap`, baseada na troca de duas tarefas entre máquinas diferentes;
* meta-heurística VND (*Variable Neighbourhood Descent*);
* geração automática de instâncias aleatórias;
* cálculo de limite inferior teórico;
* execução dos experimentos computacionais;
* apresentação do melhor resultado e da média do tempo computacional.

---

## Representação da solução

Cada solução é representada por três informações principais:

```python
s['alocacao']
s['cargas']
s['cmax']
```

O campo `alocacao` indica em qual máquina cada tarefa foi colocada.

O campo `cargas` armazena a soma dos tempos das tarefas em cada máquina.

O campo `cmax` guarda o valor da função objetivo, isto é, a maior carga entre todas as máquinas.

---

## Heurística construtiva LPT

A solução inicial é construída com a heurística LPT.

A ideia é simples:

1. ordenar as tarefas da maior para a menor;
2. alocar cada tarefa na máquina que estiver com menor carga no momento.

Essa estratégia costuma produzir uma solução inicial bem equilibrada para o problema `P || Cmax`.

---

## Vizinhanças usadas no VND

O VND utiliza duas vizinhanças.

### N1 — Realocação

Move uma tarefa da máquina atual para outra máquina.

Exemplo:

```txt
tarefa i sai da máquina A e vai para a máquina B
```

### N2 — Troca

Troca duas tarefas que estão em máquinas diferentes.

Exemplo:

```txt
tarefa i da máquina A troca de lugar com tarefa j da máquina B
```

O VND começa pela vizinhança `N1`. Quando encontra uma melhora, volta para `N1`. Quando não encontra melhora, passa para a próxima vizinhança. O processo termina quando nenhuma das vizinhanças consegue melhorar a solução atual.

---

## Geração das instâncias

As instâncias são geradas de forma aleatória, seguindo o padrão usado nos experimentos do projeto:

```txt
p[i] ~ U[1, 100]
```

Ou seja, cada tarefa recebe um tempo de processamento inteiro entre 1 e 100.

As configurações testadas combinam diferentes valores de `n` e `m`, onde:

* `n` é o número de tarefas;
* `m` é o número de máquinas.

Para cada configuração, são usadas 5 sementes fixas, permitindo repetir os mesmos testes em execuções futuras.

---

## Formato dos arquivos gerados

Cada instância gerada é salva em um arquivo `.txt` dentro da pasta:

```txt
instancias_geradas/
```

O formato usado é simples:

```txt
Instancia P_Cmax n m
p1 p2 p3 ... pn
```

Exemplo:

```txt
Instancia P_Cmax 20 4
82 15 4 95 36 ...
```

A primeira linha identifica o problema e informa os valores de `n` e `m`.

A segunda linha contém os tempos de processamento das tarefas.

---

## Significado das principais métricas

A tabela gerada pelo programa apresenta as seguintes colunas:

| Coluna       | Significado                                                    |
| ------------ | -------------------------------------------------------------- |
| `n`          | Número de tarefas da configuração testada.                     |
| `m`          | Número de máquinas disponíveis.                                |
| `LB_m`       | Limite inferior médio teórico para o `Cmax`.                   |
| `LPT_m`      | `Cmax` médio obtido pela heurística construtiva LPT.           |
| `VND_m`      | `Cmax` médio obtido após aplicar o VND.                        |
| `Melhor_VND` | Menor `Cmax` obtido pelo VND nas 5 instâncias da configuração. |
| `Gap_LPT%`   | Distância percentual média entre o LPT e o limite inferior.    |
| `Gap_VND%`   | Distância percentual média entre o VND e o limite inferior.    |
| `Tempo_m(s)` | Média do tempo computacional do VND, em segundos.              |

O cálculo do gap é feito por:

```txt
Gap(%) = (Cmax médio - LB médio) / LB médio × 100
```

O `LB` é um limite inferior teórico. Ele não é necessariamente o ótimo, mas serve como referência para avaliar a qualidade das soluções obtidas.

---

## Resultados computacionais

Nos experimentos, o programa compara a solução inicial obtida pela LPT com a solução final obtida pelo VND.

Um exemplo de linha da saída é:

```txt
n     m      LB_m    LPT_m    VND_m  Melhor_VND    Gap_LPT%   Gap_VND%   Tempo_m(s)
20    4     227.6    232.0    228.4         175       1.93%      0.35%     0.000186
```

Nesse exemplo, o VND reduziu o `Cmax` médio em relação à solução inicial LPT, aproximando o resultado do limite inferior teórico.

A coluna `Melhor_VND` mostra o menor `Cmax` encontrado entre as 5 instâncias daquela configuração.

---

## Resumo final da execução

Ao final da execução, o programa apresenta um resumo com:

* problema tratado;
* representação da solução;
* função objetivo;
* heurística construtiva;
* vizinhanças utilizadas;
* meta-heurística implementada;
* número de configurações testadas;
* número de instâncias avaliadas;
* melhor resultado obtido pelo VND;
* tempo médio geral;
* gap médio geral.

Esse resumo foi incluído para facilitar a conferência dos itens exigidos na Atividade A2.

---

## Conclusão

A implementação resolve o problema `P || Cmax` por meio de uma meta-heurística VND adaptada ao problema.

A solução contempla:

* representação da solução;
* heurística construtiva;
* movimentos de vizinhança;
* implementação do VND;
* geração automática de instâncias;
* resultados computacionais;
* melhor resultado obtido;
* média do tempo computacional.

Assim, o código atende aos requisitos da Atividade A2 do projeto final.
