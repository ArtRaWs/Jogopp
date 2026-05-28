# ============================================================
#  ELDORIA GAME - BANCO DE PERGUNTAS PYTHON
# ============================================================

import copy
import random


_BANCO: dict[str, list[dict]] = {

    # ── Tema: Sentinela de Sucata ─────────────────────────────
    "dicionarios": [
        {
            "pergunta": "Como acessar o valor da chave 'nome'\nnum dicionário d = {'nome': 'Arthur'}?",
            "opcoes": [
                "d.nome",
                "d['nome']",
                "d.get_nome()",
                "d[0]",
            ],
            "correta": 1,
            "explicacao": "Use d['chave'] ou d.get('chave') para acessar valores.",
        },
        {
            "pergunta": "Qual método retorna todas as chaves\nde um dicionário?",
            "opcoes": [
                "d.values()",
                "d.items()",
                "d.keys()",
                "d.chaves()",
            ],
            "correta": 2,
            "explicacao": "d.keys() retorna todas as chaves; d.values() retorna os valores.",
        },
        {
            "pergunta": "O que faz d.get('hp', 0)\nse 'hp' não existir no dicionário?",
            "opcoes": [
                "Lança KeyError",
                "Retorna None",
                "Retorna 0",
                "Cria a chave 'hp'",
            ],
            "correta": 2,
            "explicacao": "d.get(chave, padrão) retorna o padrão se a chave não existir.",
        },
        {
            "pergunta": "Como adicionar ou atualizar\na chave 'nivel' para 5 num dicionário d?",
            "opcoes": [
                "d.add('nivel', 5)",
                "d['nivel'] = 5",
                "d.update_key('nivel', 5)",
                "d.set('nivel') = 5",
            ],
            "correta": 1,
            "explicacao": "d['chave'] = valor adiciona ou sobrescreve a chave diretamente.",
        },
        {
            "pergunta": "Qual o resultado de len({'a': 1, 'b': 2, 'c': 3})?",
            "opcoes": ["6", "2", "3", "1"],
            "correta": 2,
            "explicacao": "len() em dicionário conta o número de pares chave-valor.",
        },
    ],

    # ── Tema: General Bug ─────────────────────────────────────
    "listas": [
        {
            "pergunta": "Dada a matriz:\nm = [[1,2,3],[4,5,6],[7,8,9]]\nQual é m[1][2]?",
            "opcoes": ["4", "6", "8", "3"],
            "correta": 1,
            "explicacao": "m[1] é a segunda linha [4,5,6]; m[1][2] é o índice 2 = 6.",
        },
        {
            "pergunta": "Como adicionar o valor 10\nno final de uma lista lst?",
            "opcoes": [
                "lst.add(10)",
                "lst.insert(10)",
                "lst.append(10)",
                "lst + 10",
            ],
            "correta": 2,
            "explicacao": "append() adiciona um elemento no final da lista.",
        },
        {
            "pergunta": "O que retorna lst[-1]\npara lst = [10, 20, 30]?",
            "opcoes": ["10", "20", "30", "Erro"],
            "correta": 2,
            "explicacao": "Índices negativos acessam do final: -1 é o último elemento.",
        },
        {
            "pergunta": "Qual método remove\no primeiro elemento de valor 5 da lista?",
            "opcoes": [
                "lst.pop(5)",
                "lst.delete(5)",
                "lst.remove(5)",
                "del lst[5]",
            ],
            "correta": 2,
            "explicacao": "remove(valor) exclui a primeira ocorrência do valor. pop(índice) remove por posição.",
        },
        {
            "pergunta": "Como criar uma lista\ncom os números de 0 a 4?",
            "opcoes": [
                "list(range(5))",
                "list(range(1,5))",
                "[0..4]",
                "range[0:5]",
            ],
            "correta": 0,
            "explicacao": "range(5) gera 0,1,2,3,4 — e list() converte para lista.",
        },
    ],

    # ── Tema: Rei Drakon ──────────────────────────────────────
    "arquivos": [
        {
            "pergunta": "Qual modo abre um arquivo\nsomente para leitura em Python?",
            "opcoes": ["'w'", "'a'", "'r'", "'x'"],
            "correta": 2,
            "explicacao": "'r' = read (leitura), 'w' = write, 'a' = append, 'x' = cria novo.",
        },
        {
            "pergunta": "O que a instrução 'with' garante\nao abrir um arquivo?",
            "opcoes": [
                "Lê o arquivo mais rápido",
                "Fecha o arquivo automaticamente",
                "Converte para binário",
                "Cria backup automático",
            ],
            "correta": 1,
            "explicacao": "O bloco 'with' garante que o arquivo seja fechado mesmo em caso de erro.",
        },
        {
            "pergunta": "Qual método lê\ntodas as linhas de um arquivo como lista?",
            "opcoes": [
                "f.read()",
                "f.readline()",
                "f.readlines()",
                "f.lines()",
            ],
            "correta": 2,
            "explicacao": "readlines() retorna uma lista de strings, uma por linha.",
        },
        {
            "pergunta": "Como escrever 'Olá' em um arquivo\nno modo de adição (sem apagar)?",
            "opcoes": [
                "open('f.txt', 'w')",
                "open('f.txt', 'r')",
                "open('f.txt', 'a')",
                "open('f.txt', 'x')",
            ],
            "correta": 2,
            "explicacao": "'a' (append) adiciona conteúdo sem apagar o que já existe.",
        },
        {
            "pergunta": "O que acontece se abrir um arquivo\ncom modo 'w' que já existe?",
            "opcoes": [
                "Lança FileExistsError",
                "Cria um backup automático",
                "Apaga o conteúdo e recria",
                "Abre em modo leitura",
            ],
            "correta": 2,
            "explicacao": "Modo 'w' trunca (apaga) o arquivo existente e começa do zero.",
        },
    ],
}


def get_perguntas(topico: str) -> list[dict]:
    """
    Retorna uma cópia embaralhada das perguntas do tópico.
    Se o tópico não existir, retorna lista vazia.
    """
    perguntas = copy.deepcopy(_BANCO.get(topico, []))
    random.shuffle(perguntas)
    return perguntas