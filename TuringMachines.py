from typing import List
from enum import Enum


class ShiftMove(Enum):
    NO_MOVE = "0"
    LEFT = "-"
    RIGHT = "+"
    INPUT = "/"
    NONE = None

    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if member.value == value:
                return member
        if value == 'R':
            return cls.RIGHT
        elif value == 'L':
            return cls.LEFT

        return cls.NONE


class TransactionQuadruple:
    input_state: int
    input_symbol: str
    output_state: int
    symbol_or_move: str | ShiftMove

    def __init__(self, input_state, input_symbol, output_state, symbol_or_move):
        if (ShiftMove(input_symbol) == ShiftMove.INPUT and ShiftMove(symbol_or_move) == ShiftMove.NONE
                or ShiftMove(input_symbol) != ShiftMove.INPUT and ShiftMove(symbol_or_move) != ShiftMove.NONE):
            raise Exception("Transição incongruente")

        self.input_state = input_state
        self.input_symbol = input_symbol
        self.output_state = output_state
        self.symbol_or_move = symbol_or_move


class TransactionQuintuple:
    # accept_state: bool
    input_state: int
    input_symbol: str
    output_state: int
    output_symbol: int
    move: ShiftMove

    def __init__(self, input_state, input_symbol, output_state, output_symbol, move: ShiftMove):
        self.input_state = input_state
        self.input_symbol = input_symbol
        self.output_state = output_state
        self.output_symbol = output_symbol
        self.move = move

    def getQuadruple(self, displacement=0) -> [TransactionQuadruple, TransactionQuadruple]:
        q1 = TransactionQuadruple(self.input_state, self.input_symbol, self.input_state + displacement,
                                  self.output_symbol)
        q2 = TransactionQuadruple(q1.input_state, ShiftMove.INPUT.value, self.output_state, self.move)
        return q1, q2


class StandarTuringMachine:
    current_state: int = 0
    tape_index: int = 0
    transactions: List[TransactionQuintuple]

    def __init__(self, transactions=None):
        if transactions is None:
            transactions = []
        self.transactions = transactions

    def valide(self) -> bool:
        """ 3 ) Special quintuples: The machine includes the following quintuples
            A1, b -> A2, b, RIGHT
            Af-1, b -> Af, b, NO_MOVE

            These two are thus thefirst and last executed respectively
            in any terminating computation on a standard input. The
            letter b represents a blank.

            - buscar o primeiro estado e ver que ele só aparece uma vez
            - buscar o ultimo estado e ver que ele só aparece uma vez
            """

        return True


class Tape:
    BLANK_SYMBOL = ''
    LIMIT_SYMBOL = '§'
    tape_internal: list = ['$', BLANK_SYMBOL]
    pointer: int = 1

    def __init__(self, input: str):
        super().__init__()
        self.tape_internal.append(self.LIMIT_SYMBOL)
        for c in input:
            self.tape_internal.append(c)

    def _sync_size(self):
        while self.pointer + 1 > len(self.tape_internal):
            self.tape_internal.append(self.BLANK_SYMBOL)

    def righ(self):
        self.pointer += 1
        self._sync_size()

    def left(self):
        self.pointer -= 1
        if self.pointer < 0:
            raise Exception("Tape: Movimento para além do limite esquerdo")
        self._sync_size()

    def write(self, value: str):
        if self.pointer == 0:
            raise Exception(f"Tape: Tentativa de sobrescrever o símbolo limitador de fita {self.LIMIT_SYMBOL}")
        self.tape_internal[self.pointer] = value

    def read(self) -> str:
        return self.tape_internal[self.pointer]
