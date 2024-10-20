from typing import List
from enum import Enum
from copy import deepcopy


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
        self.input_state = input_state
        self.input_symbol = input_symbol
        self.output_state = output_state
        self.symbol_or_move = symbol_or_move

    def __str__(self):
        input_symbols_str = ','.join(self.input_symbol)
        symbol_or_move_str = ','.join(map(str, self.symbol_or_move))
        return f"({self.input_state},{input_symbols_str}) = ({self.output_state},{symbol_or_move_str})"


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

    def getQuadruple(self) -> [TransitionQuadruple, TransitionQuadruple]:
        q1 = TransitionQuadruple(f"A({self.input_state})",
                                 input_symbol=[self.input_symbol[0], "/", Tape.BLANK_SYMBOL],
                                 output_state=f"A'({self.input_state})",
                                 symbol_or_move=[self.output_symbol[0], ShiftMove.RIGHT, Tape.BLANK_SYMBOL]
                                 )
        q2 = TransitionQuadruple(q1.output_state,
                                 input_symbol=[ShiftMove.INPUT.value, Tape.BLANK_SYMBOL, ShiftMove.INPUT.value],
                                 output_state=f"A({self.output_state})",
                                 symbol_or_move=[self.move[0], self.input_state, ShiftMove.NO_MOVE]
                                 )

        c1 = TransitionQuadruple(f"C{self.input_state}",
                                 input_symbol=[ShiftMove.INPUT.value, self.input_state, ShiftMove.INPUT.value],
                                 output_state=f"C'({self.output_state})",
                                 symbol_or_move=[ShiftMove.Inverse(self.move), Tape.BLANK_SYMBOL, ShiftMove.NO_MOVE]
                                 )
        c1 = TransitionQuadruple(f"C'{self.input_state}",
                                 input_symbol=[ShiftMove.INPUT.value, self.input_state, ShiftMove.INPUT.value],
                                 output_state=f"C'({int(self.output_state)-1})",
                                 symbol_or_move=[ShiftMove.Inverse(self.move), Tape.BLANK_SYMBOL, ShiftMove.NO_MOVE]
                                 )

        return q1, q2


class Tape:
    BLANK_SYMBOL = 'B'
    LIMIT_SYMBOL = '§'
    tape_internal: list
    pointer: int = 1

    def __init__(self, input_tape: str = None):
        self.tape_internal = [self.LIMIT_SYMBOL]
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

    def read(self) -> str | ShiftMove:
        s = self.tape_internal[self.pointer]
        if ShiftMove(s) == ShiftMove.NONE:
            return s
        else:
            return ShiftMove(s)

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
    init_state: str
    init_tapes: List[Tape]
    transitions: List[TransitionQuintuple]
    tapes: List[Tape]
    accept_state: str

    def __init__(self, accept_state: str, states: List[str], tape_symbols: List[str], input_symbols: List[str],
                 transitions=None, init_state='q1', tapes: List[Tape] = None):
        if tapes is None:
            self.init_tapes = []
        else:
            self.init_tapes = deepcopy(tapes)
        if transitions is None:
            transitions = []
        self.transitions = transitions
        self.init_state = init_state
        self.accept_state = accept_state
        self.states = states
        self.tape_symbols = tape_symbols
        self.input_symbols = input_symbols

        self.reset()

    def reset(self):
        self.tapes = deepcopy(self.init_tapes)
        self.current_state = self.init_state

    def bind_transition(self, transition: TransitionQuintuple, readed_symbol: List[str]) -> bool:
        if self.current_state == transition.input_state:
            for x, y in zip(transition.input_symbol, readed_symbol):
                if x != "/" and x != y:
                    return False
            return True
        return False

    def _execute_transition(self, transition: TransitionQuintuple | TransitionQuadruple):

        def exec_move(tape: Tape, move: ShiftMove):
            if (move == ShiftMove.LEFT):
                tape.left()
            elif move == ShiftMove.RIGHT:
                tape.right()
            elif move == ShiftMove.NO_MOVE and self.NO_MOVE:
                pass
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
            print(
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


def make_reversible_turing_machine(Tm: TuringMachine) -> TuringMachine:
    """
    Deve retornar uma Máquina de Turing Multifita Reversivel
    :param Tm: MT de uma fita
    :return: MT Reversível
    """
    if len(Tm.tapes) > 1:
        raise Exception("Expected one tape Turing Machine")

    transtitions_quintuple: List[TransitionQuintuple] = []
    states_list: List[str] = ["A(i), A(f)"]

    # Adiciona os estados originais. x -> A(x)
    for state in Tm.states:
        states_list.append(f"A({state})")
        states_list.append(f"A'({state})")

    """Aplica o requisito descrito no artigo.
    Special quintuples: The machine includes the following quintuples and T .
    Ai, b -> b, +, A2,
    Af-1, b -> b, 0, Af
     
     A2 é o estado inicial da máquina e Af-1 é o estado final, estes serçai "trocados" por A1 e Af-1
     Espera-se que Tm não possua estados "i" e  "f"
    """
    first_transition = TransitionQuintuple('i', [Tm.tapes[0].BLANK_SYMBOL], Tm.init_state,
                                           [Tape.BLANK_SYMBOL],
                                           [ShiftMove.RIGHT])
    last_transition = TransitionQuintuple(Tm.accept_state, [Tape.BLANK_SYMBOL], "f",
                                          [Tape.BLANK_SYMBOL],
                                          [ShiftMove.NO_MOVE])

    transtitions_quintuple.append(first_transition)
    transtitions_quintuple.append(last_transition)

    transtitions_quintuple += Tm.transitions

    transitions_quad: List[TransitionQuadruple] = []
    for transition in transtitions_quintuple:
        q1, q2 = transition.getQuadruple()
        transitions_quad.append(q1)
        transitions_quad.append(q2)

    # Copy
    tcopy: List[TransitionQuadruple] = [
        TransitionQuadruple(input_state="A(f)",
                            input_symbol=[Tape.BLANK_SYMBOL, f"{Tm.accept_state}", Tape.BLANK_SYMBOL],
                            output_state="B'(1)",
                            symbol_or_move=[Tape.BLANK_SYMBOL, f"{Tm.accept_state}", Tape.BLANK_SYMBOL]),
        TransitionQuadruple(input_state="B'(1)",
                            input_symbol=["/", "/", "/"],
                            output_state="B(1)",
                            symbol_or_move=[ShiftMove.RIGHT, ShiftMove.NO_MOVE, ShiftMove.RIGHT]),
        TransitionQuadruple(input_state="B(1)",
                            input_symbol=[Tape.BLANK_SYMBOL, f"{Tm.accept_state}", Tape.BLANK_SYMBOL],
                            output_state="B'(2)",
                            symbol_or_move=[Tape.BLANK_SYMBOL, f"{Tm.accept_state}", Tape.BLANK_SYMBOL]),
        TransitionQuadruple(input_state="B'(2)",
                            input_symbol=["/", "/", "/"],
                            output_state="B(2)",
                            symbol_or_move=[ShiftMove.LEFT, ShiftMove.NO_MOVE, ShiftMove.LEFT]),
        TransitionQuadruple(input_state="B(2)",
                            input_symbol=[Tape.BLANK_SYMBOL, f"{Tm.accept_state}", Tape.BLANK_SYMBOL],
                            output_state="C(f)",
                            symbol_or_move=[Tape.BLANK_SYMBOL, f"{Tm.accept_state}", Tape.BLANK_SYMBOL]),
    ]

    for symbol in Tm.tape_symbols:
        if symbol == Tape.BLANK_SYMBOL:
            continue
        tb1 = TransitionQuadruple(input_state="B(1)",
                                  input_symbol=[symbol, f"{Tm.accept_state}", Tape.BLANK_SYMBOL],
                                  output_state="B'(1)",
                                  symbol_or_move=[symbol, f"{Tm.accept_state}", symbol])
        tb2 = TransitionQuadruple(input_state="B(2)",
                                  input_symbol=[symbol, f"{Tm.accept_state}", symbol],
                                  output_state="B'(2)",
                                  symbol_or_move=[symbol, f"{Tm.accept_state}", symbol])

        tcopy.append(tb1)
        tcopy.append(tb2)

    transitions_quad.extend(tcopy)

    transitions_quad.sort(key=lambda a: a.input_state.replace("'", ""))

    tmp_tape = deepcopy(Tm.init_tapes)
    tmp_tape.extend([Tape(f"{Tape.BLANK_SYMBOL}"), Tape(f"{Tape.BLANK_SYMBOL}")])
    tmp_tape[0].tape_internal.insert(1, Tape.BLANK_SYMBOL)

    for t in transitions_quad:
        print(t)

    return TuringMachine(init_state="A(i)", accept_state="d",
                         states=states_list, tape_symbols=Tm.tape_symbols,
                         transitions=transitions_quad, tapes=tmp_tape,
                         input_symbols=Tm.input_symbols)
