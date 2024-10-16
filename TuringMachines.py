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


class TransitionQuadruple:
    input_state: str
    input_symbol: List[str]
    output_state: int
    symbol_or_move: List[str | ShiftMove]

    def __init__(self, input_state, input_symbol, output_state, symbol_or_move):
        if (ShiftMove(input_symbol) == ShiftMove.INPUT and ShiftMove(symbol_or_move) == ShiftMove.NONE
                or ShiftMove(input_symbol) != ShiftMove.INPUT and ShiftMove(symbol_or_move) != ShiftMove.NONE):
            raise Exception("Transição incongruente")

        self.input_state = input_state
        self.input_symbol = input_symbol
        self.output_state = output_state
        self.symbol_or_move = symbol_or_move


class TransitionQuintuple:
    # accept_state: bool
    input_state: str
    input_symbol: List[str]
    output_state: str
    output_symbol: List[str]
    move: List[ShiftMove]

    def __init__(self, input_state, input_symbol, output_state, output_symbol, move: List[ShiftMove]):
        self.input_state = input_state
        self.input_symbol = input_symbol
        self.output_state = output_state
        self.output_symbol = output_symbol
        self.move = move

    def getQuadruple(self, displacement=0) -> [TransitionQuadruple, TransitionQuadruple]:
        q1 = TransitionQuadruple(self.input_state, self.input_symbol, self.input_state + 'm',
                                 self.output_symbol)
        q2 = TransitionQuadruple(q1.input_state, ShiftMove.INPUT.value, self.output_state, self.move)
        return q1, q2


class Tape:
    BLANK_SYMBOL = 'B'
    LIMIT_SYMBOL = '§'
    tape_internal: list = [LIMIT_SYMBOL]
    pointer: int = 1

    def __init__(self, input_tape: str = None):
        super().__init__()
        for c in input_tape:
            self.tape_internal.append(c)

    def _sync_size(self):
        while self.pointer + 1 > len(self.tape_internal):
            self.tape_internal.append(self.BLANK_SYMBOL)

    def right(self):
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

    def __str__(self):
        out: str = '|'
        for index, symbol in enumerate(self.tape_internal):
            if index == self.pointer:
                out += f'\x1b[1;31m{symbol}\x1b[0m|'
            else:
                out += f'{symbol}|'
        return out


class TuringMachine:
    DETAIL_STR = False
    NO_MOVE = True
    current_state: str
    transitions: List[TransitionQuintuple]
    tapes: List[Tape]
    accept_state: str

    def __init__(self, accept_state: str, states: List[str], tape_symbols: List[str], input_symbols: List[str],
                 transitions=None, init_state='q1', tapes: List[Tape] = None):
        if tapes is None:
            tapes = []
        else:
            self.tapes = tapes
        if transitions is None:
            transitions = []
        self.transitions = transitions
        self.current_state = init_state
        self.accept_state = accept_state
        self.states = states
        self.tape_symbols = tape_symbols
        self.input_symbols = input_symbols

    def bind_transition(self, transition: TransitionQuintuple, readed_symbol: List[str]) -> bool:
        return self.current_state == transition.input_state and transition.input_symbol == readed_symbol

    def _execute_transition(self, transition: TransitionQuintuple | TransitionQuadruple):

        def exec_move(tape: Tape, move: ShiftMove):
            if (move == ShiftMove.LEFT):
                tape.left()
            elif move == ShiftMove.RIGHT:
                tape.right()
            elif move == ShiftMove.NO_MOVE and not self.NO_MOVE:
                raise Exception("Maquina de Turing: Esta MT não permite movimentos nulo")
            else:
                raise Exception("Movimento Inválido")

        if isinstance(transition, TransitionQuintuple):
            for fita, symbol, move in zip(self.tapes, transition.output_symbol, transition.move):
                fita.write(symbol)
                exec_move(fita, move)

        elif isinstance(transition, TransitionQuadruple):
            for fita, symbol_or_move in zip(self.tapes, transition.symbol_or_move):
                if isinstance(symbol_or_move, ShiftMove):
                    exec_move(fita, symbol_or_move)
                else:
                    fita.write(symbol_or_move)

        self.current_state = transition.output_state

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

    def step(self):
        if self.current_state == self.accept_state:
            pass

        symbol = [tape.read() for tape in self.tapes]

        list_transitions = [t for t in self.transitions if self.bind_transition(t, symbol)]

        if len(list_transitions) == 0:
            raise Exception(
                f"Máquina de Turing: Nenhuma transição encontrada para estado {self.current_state} e simbolo {symbol}")
        elif len(list_transitions) > 1:
            raise Exception(
                f"Máquina de Turing: Mais de uma transição encontrada para estado {self.current_state} e simbolo "
                f"{symbol}. Máquina Não Deterministica não implementada")
        transistion = list_transitions[0]

        self._execute_transition(transistion)

    def __str__(self):
        if self.DETAIL_STR:
            out = f"""
                    _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-
                    Símbolos de Entrada: {self.input_symbols}
                    Símbolos de Fita: {self.tape_symbols}
                    Estados: {self.states}
                    Estado de Aceitação: {self.accept_state}
                    Estado atual: {self.current_state} \n
                    """
        else:
            out = f"Estado atual: {self.current_state} \n"

        for tape in self.tapes:
            out += tape.__str__() + "\n"
        out += "\t\t_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-"

        return out

    def run(self):
        while self.current_state != self.accept_state:
            self.step()
            print(self)
        print("EXECUTION END")
