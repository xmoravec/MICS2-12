from random import randint
from fractions import Fraction

class LFSR(object):
    def __init__(self, n, taps):
        self.n = n

        self.taps = tuple(taps)
        assert self.taps[0] == 0
        assert 0 <= min(self.taps) <= max(self.taps) <= n - 1

        self.state = (0,) * n

    def init(self, state):
        assert len(state) == self.n
        self.state = tuple(state)

    def init_random(self):
        self.state = tuple(randint(0, 1) for _ in range(self.n))

    def clock(self):
        output = self.state[0]
        new_val = 0
        for t in self.taps:
            new_val ^= self.state[t]
        self.state = self.state[1:] + (new_val,)
        return output

    def filter(self, eq):
        """Example:
        eq = [(0, 2), (4, 20), (3,), (7,)]
        corresponds to filter
        s0*s2 + s4*s20 + s3 + s7
        """
        output = 0
        for monomial in eq:
            monomial_value = 1
            for varindex in monomial:
                monomial_value &= self.state[varindex]
            output ^= monomial_value
        return output

    def __str__(self):
        output = ""
        for i in reversed(range(0, self.n)):
            # reversed because we print S_0 to the right
            output += str(self.state[i])
        return output


class Geffe(object):
    def __init__(self, n, all_taps, F):
        assert len(all_taps) == 3
        assert len(F) == 8
        self.L = [LFSR(n, taps) for taps in all_taps]
        self.n = n
        self.F = F

    def set_state(self, k):
        states = [[], [], []]
        for i in range(self.n):
            for s in range(3):
                states[s].append(k[s] % 2)
                k[s] = k[s] // 2

        for s in range(3):
            self.L[s].init(states[s])

    def clock(self):
        f_input = 0
        for s in range(3):
            f_input = (f_input << 1) | (self.L[s].clock())
        return self.F[f_input]

    def __str__(self):
        output = ""
        for s in range(3):
            output += str(self.L[s]) + " "
        return output[:-1]



class FilteredLFSR(object):
    """
    example: F = [(0, 2), (4, 20), (3,), (7,)]
    """
    def __init__(self, n, taps, F):
        self.L = LFSR(n, taps)
        self.L.init_random() # random initial state
        self.eq = tuple(F)

    def clock(self):
        output = self.L.filter(self.eq)
        self.L.clock()
        return output


class ModifiedRC5(object):
    def __init__(self, k0, k1):
        assert 0 <= k0 < 2**32
        assert 0 <= k1 < 2**32
        self.k = k0, k1

    def rotate_left(self, w, n):
        w &= 0xffffffff
        w = (w << n) | (w >> (32-n))
        w &= 0xffffffff
        return w

    def encrypt(self, xl, xr):
        assert 0 <= xl < 2**32
        assert 0 <= xr < 2**32
        for roundno in range(12):
            xl ^= xr
            xl = self.rotate_left(xl, 7)
            xl ^= self.k[0]

            # swap
            xl, xr = xr, xl

            xl ^= xr
            xl = self.rotate_left(xl, 7)
            xl ^= self.k[1]

            # swap
            xl, xr = xr, xl
        return xl, xr

output = "11000101000110101001001101000010111100100010110101100110001101100100101001101011111110001011110111101101010110000010011110101101000010010011011000110001101101001111101100101000001100110011110011111100"
bits = [int(bit, 2) for bit in output]

def get_correlation(stream):
    same = 0
    for i in range(len(stream)):
        if bits[i] == stream[i]:
            same += 1
    return Fraction(same, len(stream))

def find_key_L1():
    gef = Geffe(16, [(0, 1, 4, 7), (0, 1, 7, 11), (0, 2, 3, 5)], [1,0,1,0,0,0,1,1])
    for i in range(2**16):
        gef.set_state([0, i, 0])
        stream = []
        for i in range(len(bits)):
            stream.append(gef.clock())
        if get_correlation(stream) == Fraction(3, 4):
            print(i)
    return None

print(find_key_L1())