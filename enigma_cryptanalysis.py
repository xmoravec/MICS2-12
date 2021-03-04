
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def char_to_index(char):
    return ord(char[0]) - 65

class Rotor:

    def __init__(self, wiring, starting_rotation):
        self.wiring = wiring
        self.rotation = starting_rotation

    def rotate(self):
        self.rotation += 1
        self.rotation %= 26
        #This is commented out, because the other rotors should not move
        #position = [N, M, L, R].index(self)
        #if position in range(3) and self.rotation == char_to_index(KEY[position]):
            #print(position)
            #[N, M, L, R][position + 1].rotate()

    def set_rotation(self, val):
        self.rotation = val

    def get(self, x):
        x = char_to_index(x)
        return self.wiring[x]

    ## This is for the inverse rotor function
    def get_reverse(self, x):
        x = self.wiring.find(x)
        return ALPHABET[x]

N = Rotor("BDFHJLCPRTXVZNYEIWGAKMUSQO", 0)
M = Rotor("AJDKSIRUXBLHWTMCQGZNPYFVOE", 0)
L = Rotor("EKMFLGDQVZNTOWYHXUSPAIBRCJ", 0)
R = Rotor("YRUHQSLDPXNGOKMIEBFZCWVJAT", 0)

## These are the encryption functions

## This function simply applies the cyclis shift, where N.rotation is used as the I value
def applyP(char):
    return chr(((char_to_index(char) + N.rotation) % 26) + 65)

## By PI i simply mean P^-I
def applyPI(char):
    return chr(((char_to_index(char) - N.rotation) % 26) + 65)

def applyPINP(char):
    n = N.get(applyP(char))
    return applyPI(n)

def applyZ(char):
    e = R.get(L.get(M.get(char)))
    return M.get_reverse(L.get_reverse(e))

def applyZPINP(char):
    return applyZ(applyPINP(char))

## A generic encrypt function, applies either ZPINP on the plaintext, or PINP on ciphertext
def encrypt(word, func):
    result = ""
    for c in word:
        ## We first rotate, then encrypt
        N.rotate()
        result += func(c)
    return result

## Here i check for the validity of the encryption, e.g. find the contradictions
def check_contradictions(a, b):
    print(f"checked: {a} over {b}")
    for i, c in enumerate(a):
        for j, d in enumerate(a):
            if c == d and b[i] != b[j]:
                print(f"contradiction: in letter {c} at positions {i} goes to {b[i]} and at {j} goes to {b[j]}")
                return False
    return True

## This functions is the main loop of the program, where all the initial settings are generated and tried
def bathons_attack(plaintext, ciphertext):
    for i in range(26):
        N.set_rotation(i)
        p = encrypt(plaintext, applyZPINP)
        ## This set the rotation to the initial setting so the second encryption begins from the same point
        N.set_rotation(i)
        c = encrypt(ciphertext, applyPINP)
        ## this comparison must be done by checking the non contradiction property
        if check_contradictions(p, c):
            return f"HURRAY. Initial setting of N is {chr(65 + i)}"
    return "The initial rotor setting was not found"


print(bathons_attack("FORAREASONEVERYTHINGHAPPENS", "HMUVNBLLMHDSTTKIWOKRECSHDLP"))