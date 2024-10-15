"""Entrada-Quintupla.txt
# Linha 1: número de estados, número de símbolos no alfabeto de entrada, número de símbolos no alfabeto da fita e
número de transições, respectivamente.
# Linha 2: Estados. O último estado representa o estado de aceitação.
# Linha 3: alfabeto de entrada
# Linha 4: alfabeto da fita.
# Linhas ~: funcão de transição (como explicada no artigo).
# Última linha: Entrada

"""
import re
from re import match
from sys import stdin
from typing import IO
from TuringMachines import TransactionQuintuple, ShiftMove


def make_trasnaction_quintuple(input: str) -> TransactionQuintuple:
    # Expressão regular para capturar os números e símbolos
    padrao = r"\((\d+),([A-Z])\)=\((\d+),([A-Z]),([A-Z])\)"

    # Usar re.match para extrair os valores
    match = re.match(padrao, input)

    if match:
        # Extrair os grupos correspondentes
        input_state = match.group(1)
        input_symbol = match.group(2)
        output_state = match.group(3)
        output_symbol = match.group(4)
        move = ShiftMove(match.group(5))
    # 
    return TransactionQuintuple(input_state, input_symbol, output_state, output_symbol, move)

# TODO: Faria mais sentido matemático, usar set() ao invés de list()
def turing_from_file(file: IO):

    # Linha 1: Informações de Controle
    n_states, n_input_symbols, n_tape_symbols, n_trans = file.readline().split(sep=' ')
    print(n_states, n_input_symbols, n_tape_symbols, n_trans)

    # Linha 2: Estados
    states = file.readline().split(sep=' ')
    print(states)
    if len(states) != n_states:
        raise Exception("Linha 2: Número de estados informado não corresponde ao fornecido")
    accept_state = states[-1]

    # Linha 3:
    input_symbols = file.readline().split(sep=' ')
    if len(input_symbols) != n_input_symbols:
        raise Exception("Linha 3: Número de simbolos de entrada informado não corresponde ao fornecido")

    # Linha 4
    input_tape = file.readline().split(sep=' ')
    if len(input_tape) != n_tape_symbols:
        raise Exception("Linha 4: Número de simbolos de fita informado não corresponde ao fornecido")
    # TODO: Poderia verificar que o conjunto de simbolos de entrada é subset do conjunto de simbolos da fita

    # Transições
    remain_lines = file.readlines()

    transactions = []
    for line in remain_lines[0:-1]:
        transactions.append(make_trasnaction_quintuple(line))
    if len(transactions) != n_trans:
        raise Exception("Número de transições não corresponde ao fornecido")



turing_from_file(stdin)