"""
Universidade Federal da Paraíba — Centro de Informática (UFPB / CI)

Problema de Escalonamento em Máquinas Paralelas Idênticas (P || Cmax)

Disciplina : Estrutura de Dados e Complexidade de Algoritmos

Aluno      : Everton Batista da Silva
Professor  : Prof. Gilberto Farias

Ideia do problema:
    Temos n tarefas, cada uma com um tempo de processamento p[i], e m máquinas
    idênticas. O objetivo é distribuir as tarefas entre as máquinas para minimizar
    o makespan, isto é, a maior carga entre as máquinas.

    Cmax = max carga(Mk), para k = 1, ..., m

O código abaixo implementa uma solução heurística usando:
    - representação da solução;
    - função objetivo;
    - heurística construtiva LPT;
    - duas vizinhanças: realocação e troca;
    - VND;
    - experimentos com instâncias aleatórias.
"""

import os
import random
import time


# =============================================================================
# SEÇÃO 1 — REPRESENTAÇÃO DA SOLUÇÃO
# =============================================================================

# A solução é guardada em um dicionário simples:
#   alocacao[i] = máquina em que a tarefa i foi colocada
#   cargas[k]   = soma dos tempos das tarefas da máquina k
#   cmax        = maior carga entre todas as máquinas
#
# Guardar as cargas evita recalcular tudo a cada movimento.


def cria_solucao_vazia(n, m):
    """Cria uma solução ainda sem tarefas alocadas."""
    return {
        'alocacao': [-1] * n,
        'cargas': [0] * m,
        'cmax': 0
    }


def copia_solucao(s):
    """Faz uma cópia da solução para testar movimentos sem alterar a original."""
    return {
        'alocacao': s['alocacao'][:],
        'cargas': s['cargas'][:],
        'cmax': s['cmax']
    }


# =============================================================================
# SEÇÃO 2 — FUNÇÃO OBJETIVO
# =============================================================================

# No P || Cmax, a função objetivo é o makespan:
# o maior tempo de conclusão entre as máquinas.


def f(s):
    """Retorna o Cmax da solução."""
    return max(s['cargas'])


def recalcula_cmax(s):
    """Atualiza o Cmax depois de alguma mudança nas cargas."""
    s['cmax'] = max(s['cargas'])


# =============================================================================
# SEÇÃO 3 — HEURÍSTICA CONSTRUTIVA LPT
# =============================================================================

# LPT = Longest Processing Time First.
# A ideia é começar pelas tarefas maiores e sempre colocá-las na máquina
# que está menos carregada naquele momento.


def lpt(p, m):
    """Constrói a solução inicial usando a heurística LPT."""
    n = len(p)
    s = cria_solucao_vazia(n, m)

    # Ordena as tarefas da maior para a menor.
    ordem = sorted(range(n), key=lambda i: p[i], reverse=True)

    for i in ordem:
        # Escolhe a máquina com menor carga atual.
        k = s['cargas'].index(min(s['cargas']))
        s['alocacao'][i] = k
        s['cargas'][k] += p[i]

    recalcula_cmax(s)
    return s


# =============================================================================
# SEÇÃO 4 — VIZINHANÇA N1: REALOCAÇÃO
# =============================================================================

# Um movimento de realocação tira uma tarefa da máquina atual e a coloca em outra.
# A vizinhança é explorada procurando o melhor movimento que reduza o Cmax.


def N1_realocacao(s, p, m):
    """Procura o melhor vizinho obtido por realocação de uma tarefa."""
    n = len(p)
    melhor_cmax = s['cmax']
    melhor_tarefa = -1
    melhor_dest = -1

    for i in range(n):
        orig = s['alocacao'][i]
        carga_orig_nova = s['cargas'][orig] - p[i]

        for dest in range(m):
            if dest == orig:
                continue

            carga_dest_nova = s['cargas'][dest] + p[i]

            # Recalcula o Cmax olhando para as cargas que mudariam.
            novo_cmax = 0
            for k in range(m):
                if k == orig:
                    novo_cmax = max(novo_cmax, carga_orig_nova)
                elif k == dest:
                    novo_cmax = max(novo_cmax, carga_dest_nova)
                else:
                    novo_cmax = max(novo_cmax, s['cargas'][k])

            if novo_cmax < melhor_cmax:
                melhor_cmax = novo_cmax
                melhor_tarefa = i
                melhor_dest = dest

    if melhor_tarefa == -1:
        return None

    # Aplica a melhor realocação encontrada.
    s_linha = copia_solucao(s)
    orig = s_linha['alocacao'][melhor_tarefa]

    s_linha['cargas'][orig] -= p[melhor_tarefa]
    s_linha['cargas'][melhor_dest] += p[melhor_tarefa]
    s_linha['alocacao'][melhor_tarefa] = melhor_dest
    s_linha['cmax'] = melhor_cmax

    return s_linha


# =============================================================================
# SEÇÃO 5 — VIZINHANÇA N2: TROCA
# =============================================================================

# A troca pega duas tarefas que estão em máquinas diferentes e inverte suas
# posições. Esse movimento ajuda quando apenas realocar uma tarefa não melhora.


def N2_swap(s, p, m):
    """Procura o melhor vizinho obtido pela troca de duas tarefas."""
    n = len(p)
    melhor_cmax = s['cmax']
    melhor_i = -1
    melhor_j = -1

    for i in range(n - 1):
        maq_i = s['alocacao'][i]

        for j in range(i + 1, n):
            maq_j = s['alocacao'][j]

            if maq_i == maq_j:
                continue

            carga_i_nova = s['cargas'][maq_i] - p[i] + p[j]
            carga_j_nova = s['cargas'][maq_j] - p[j] + p[i]

            novo_cmax = 0
            for k in range(m):
                if k == maq_i:
                    novo_cmax = max(novo_cmax, carga_i_nova)
                elif k == maq_j:
                    novo_cmax = max(novo_cmax, carga_j_nova)
                else:
                    novo_cmax = max(novo_cmax, s['cargas'][k])

            if novo_cmax < melhor_cmax:
                melhor_cmax = novo_cmax
                melhor_i = i
                melhor_j = j

    if melhor_i == -1:
        return None

    # Aplica a melhor troca encontrada.
    s_linha = copia_solucao(s)
    mi = s_linha['alocacao'][melhor_i]
    mj = s_linha['alocacao'][melhor_j]

    s_linha['cargas'][mi] += -p[melhor_i] + p[melhor_j]
    s_linha['cargas'][mj] += -p[melhor_j] + p[melhor_i]
    s_linha['alocacao'][melhor_i] = mj
    s_linha['alocacao'][melhor_j] = mi
    s_linha['cmax'] = melhor_cmax

    return s_linha


# =============================================================================
# SEÇÃO 6 — VND
# =============================================================================

# O VND começa com uma solução inicial e tenta melhorar usando vizinhanças
# diferentes. Quando uma vizinhança melhora a solução, o algoritmo volta para
# a primeira vizinhança. Se não melhorar, passa para a próxima.


def vnd(p, m, verbose=False):
    """Executa o VND usando LPT como solução inicial."""
    inicio = time.time()

    s = lpt(p, m)
    cmax_lpt = s['cmax']

    if verbose:
        print(f"    Solução inicial LPT: Cmax = {cmax_lpt}")

    vizinhancas = [N1_realocacao, N2_swap]
    nomes = ['N1-Realocacao', 'N2-Swap']
    r = len(vizinhancas)

    k = 0
    iteracoes = 0

    while k < r:
        iteracoes += 1
        s_linha = vizinhancas[k](s, p, m)

        if s_linha is not None:
            if verbose:
                print(f"    [{nomes[k]}] melhora: {s['cmax']} -> {s_linha['cmax']}")
            s = s_linha
            k = 0
        else:
            if verbose:
                print(f"    [{nomes[k]}] sem melhora (Cmax = {s['cmax']})")
            k += 1

    tempo_total = time.time() - inicio

    if verbose:
        print(f"    VND finalizado: Cmax = {s['cmax']} | "
              f"iterações = {iteracoes} | tempo = {tempo_total:.4f}s")

    return {
        'solucao': s,
        'cmax': s['cmax'],
        'cmax_lpt': cmax_lpt,
        'tempo': tempo_total,
        'iteracoes': iteracoes
    }


# =============================================================================
# SEÇÃO 7 — INSTÂNCIAS E LIMITE INFERIOR
# =============================================================================

# As instâncias seguem o padrão descrito no relatório da A1: 
# tempos inteiros aleatórios no intervalo [1, 100].


def gera_instancia(n, m, semente=None):
    """Gera uma lista de tempos de processamento."""
    if semente is not None:
        random.seed(semente)
    return [random.randint(1, 100) for _ in range(n)]


def salva_instancia(p, m, caminho):
    """Salva uma instância em arquivo texto para facilitar a conferência."""
    n = len(p)

    with open(caminho, 'w', encoding='utf-8') as f_out:
        f_out.write(f"Instancia P_Cmax {n} {m}\n")
        f_out.write(" ".join(str(t) for t in p) + "\n")


def gera_arquivos_instancias(pasta, configuracoes, sementes):
    """Gera os arquivos das instâncias usadas nos experimentos."""
    os.makedirs(pasta, exist_ok=True)
    caminhos = []

    for n, m in configuracoes:
        for semente in sementes:
            p = gera_instancia(n, m, semente)
            nome_arquivo = f"p_cmax-n{n}-m{m}-s{semente}.txt"
            caminho = os.path.join(pasta, nome_arquivo)
            salva_instancia(p, m, caminho)
            caminhos.append(caminho)

    return caminhos


def limite_inferior(p, m):
    """
    Calcula um limite inferior simples para o Cmax.

    Ele considera duas coisas:
    - nenhuma solução pode ter Cmax menor que a maior tarefa;
    - a carga média por máquina também precisa ser respeitada.
    """
    soma = sum(p)
    maior = max(p)
    lb = max(maior, -(-soma // m))  # ceil(soma / m)

    return lb


# =============================================================================
# SEÇÃO 8 — EXPERIMENTOS
# =============================================================================

# Configurações usadas nos testes da A2. As sementes deixam os resultados
# reproduzíveis: rodando de novo, as mesmas instâncias são geradas.


CONFIGURACOES_EXPERIMENTOS = [
    (20, 2), (20, 4),
    (50, 2), (50, 4), (50, 8),
    (100, 2), (100, 4), (100, 8), (100, 16),
    (200, 4), (200, 8), (200, 16),
]

SEMENTES_EXPERIMENTOS = [42, 17, 99, 7, 123]


def experimentos():
    """
    Executa os testes computacionais.

    Para cada configuração, o script roda 5 instâncias, compara LPT e VND,
    registra o menor Cmax observado pelo VND e calcula o tempo médio.
    """
    configuracoes = CONFIGURACOES_EXPERIMENTOS
    sementes = SEMENTES_EXPERIMENTOS
    n_instancias = len(sementes)

    resultados = []

    sep = "=" * 104
    print(sep)
    print("EXPERIMENTOS COMPUTACIONAIS — P || Cmax  |  VND com N1=Realocação e N2=Swap")
    print("Instâncias: p[i] ~ U[1, 100]  |  5 instâncias por configuração")
    print(sep)
    print(f"{'n':>6} {'m':>4}  {'LB_m':>8} {'LPT_m':>8} {'VND_m':>8} "
          f"{'Melhor_VND':>11}  {'Gap_LPT%':>10} {'Gap_VND%':>10}  {'Tempo_m(s)':>11}")
    print("-" * 104)

    for n, m in configuracoes:
        lbs, lpts, vnds, tempos = [], [], [], []

        for semente in sementes:
            p = gera_instancia(n, m, semente)
            lb = limite_inferior(p, m)
            r = vnd(p, m, verbose=False)

            lbs.append(lb)
            lpts.append(r['cmax_lpt'])
            vnds.append(r['cmax'])
            tempos.append(r['tempo'])

        lb_m = sum(lbs) / n_instancias
        lpt_m = sum(lpts) / n_instancias
        vnd_m = sum(vnds) / n_instancias
        tempo_m = sum(tempos) / n_instancias
        melhor_vnd = min(vnds)

        gap_lpt = (lpt_m - lb_m) / lb_m * 100 if lb_m > 0 else 0.0
        gap_vnd = (vnd_m - lb_m) / lb_m * 100 if lb_m > 0 else 0.0

        print(f"{n:>6} {m:>4}  {lb_m:>8.1f} {lpt_m:>8.1f} {vnd_m:>8.1f} "
              f"{melhor_vnd:>11}  {gap_lpt:>9.2f}% {gap_vnd:>9.2f}%  {tempo_m:>11.6f}")

        resultados.append({
            'n': n,
            'm': m,
            'lb_medio': lb_m,
            'cmax_lpt_medio': lpt_m,
            'cmax_vnd_medio': vnd_m,
            'melhor_vnd': melhor_vnd,
            'gap_lpt_medio': gap_lpt,
            'gap_vnd_medio': gap_vnd,
            'tempo_medio': tempo_m,
        })

    print(sep)
    print("LB_m       = limite inferior médio")
    print("LPT_m      = Cmax médio da solução inicial LPT")
    print("VND_m      = Cmax médio depois do VND")
    print("Melhor_VND = menor Cmax obtido pelo VND nas 5 instâncias")
    print("Tempo_m(s) = tempo médio de execução do VND")
    print("Gap(%)     = diferença percentual em relação ao limite inferior médio")
    print(sep)

    return resultados


def exibe_resumo_final(resultados):
    """Mostra, no fim da execução, os itens pedidos na A2."""
    if not resultados:
        print("Nenhum resultado experimental foi gerado.")
        return

    total_configuracoes = len(resultados)
    total_instancias = total_configuracoes * len(SEMENTES_EXPERIMENTOS)

    melhor_global = min(resultados, key=lambda r: r['melhor_vnd'])
    tempo_medio_geral = sum(r['tempo_medio'] for r in resultados) / total_configuracoes
    gap_vnd_medio_geral = sum(r['gap_vnd_medio'] for r in resultados) / total_configuracoes
    gap_lpt_medio_geral = sum(r['gap_lpt_medio'] for r in resultados) / total_configuracoes

    qtd_vnd_melhor_ou_igual_lpt = sum(
        1 for r in resultados
        if r['cmax_vnd_medio'] <= r['cmax_lpt_medio']
    )

    sep = "=" * 104
    print("\n" + sep)
    print("A2. Heurísticas para o POC")
    print(sep)

    print("• Representação da solução")
    print("  A solução usa três campos: alocacao, cargas e cmax.")
    print("  - alocacao[i] indica a máquina escolhida para a tarefa i;")
    print("  - cargas[k] guarda a carga acumulada da máquina k;")
    print("  - cmax guarda a maior carga, que é o valor da função objetivo.")
    print()

    print("• Heurística de construção")
    print("  Foi usada a heurística LPT (Longest Processing Time First).")
    print("  Ela ordena as tarefas da maior para a menor e aloca cada uma na máquina menos carregada.")
    print()

    print("• Movimentos de vizinhança")
    print("  Foram usados dois movimentos:")
    print("  - N1_realocacao: move uma tarefa para outra máquina;")
    print("  - N2_swap: troca duas tarefas que estão em máquinas diferentes.")
    print()

    print("• Implementar o VND")
    print("  O VND foi implementado na função vnd(p, m).")
    print("  Ele começa com a solução LPT e tenta melhorar a solução usando N1 e N2.")
    print()

    print("• Resultados computacionais:")
    print(f"  Configurações testadas : {total_configuracoes}")
    print(f"  Instâncias avaliadas   : {total_instancias} "
          f"({len(SEMENTES_EXPERIMENTOS)} sementes por configuração)")
    print(f"  Gap médio LPT          : {gap_lpt_medio_geral:.3f}% em relação ao LB médio")
    print(f"  Gap médio VND          : {gap_vnd_medio_geral:.3f}% em relação ao LB médio")
    print(f"  VND <= LPT             : {qtd_vnd_melhor_ou_igual_lpt}/{total_configuracoes} "
          "configurações, comparando o Cmax médio")
    print()

    print("- Melhor resultado")
    print(f"  Cmax = {melhor_global['melhor_vnd']} "
          f"na configuração n={melhor_global['n']}, m={melhor_global['m']}.")
    print()

    print("- Média do tempo computacional")
    print(f"  {tempo_medio_geral:.6f} segundos, considerando a média dos tempos médios do VND.")

    print(sep)


# =============================================================================
# SEÇÃO 9 — PROGRAMA PRINCIPAL
# =============================================================================

if __name__ == "__main__":

    pasta_instancias = "instancias_geradas"
    caminhos = gera_arquivos_instancias(
        pasta_instancias,
        CONFIGURACOES_EXPERIMENTOS,
        SEMENTES_EXPERIMENTOS
    )

    print(f"Geradas {len(caminhos)} instâncias em '{pasta_instancias}/'\n")

    resultados = experimentos()
    exibe_resumo_final(resultados)
