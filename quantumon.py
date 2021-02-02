from qiskit import Aer, QuantumCircuit, QuantumRegister, ClassicalRegister, execute
from qiskit.quantum_info import Operator
import numpy as np
import scipy
import random
import sys
import time
import os


os.system('')


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


GAMMA = 0


def u_hat(theta, phi):
    return np.matrix([[np.exp(1j * phi) * np.cos(theta / 2), np.sin(theta / 2)],
                      [-np.sin(theta / 2), np.exp(-1j * phi) * np.cos(theta / 2)]])


d_hat = u_hat(np.pi, 0)

alice_hp = 100
bob_hp = 100


def payoff(alice, bob):
    if alice == 0 and bob == 0:
        return (20, 20)
    elif alice == 0 and bob == 1:
        return (0, 40)
    if alice == 1 and bob == 0:
        return (40, 0)
    elif alice == 1 and bob == 1:
        return (-10, -10)


PLAYER_NAMES = ['Supercon', 'Iontra', 'Dottum', 'Optica']
random.shuffle(PLAYER_NAMES)
alice_name, bob_name = PLAYER_NAMES[0], PLAYER_NAMES[1]

OPERATIONS = ['Z', 'Y', 'X', 'H']


def rand_gate():
    gate = ''
    random.shuffle(OPERATIONS)
    for i in range(random.randint(1, 4)):
        gate += OPERATIONS[i]
    return gate


OPTION_NAMES = ["Growl", "Tackle", "Scratch", "Slash", "Bite", "Charm"]
rand_gates = {g: rand_gate() for g in OPTION_NAMES}


def crawl(s, should_crawl=True):
    for letter in s:
        sys.stdout.write(letter)
        sys.stdout.flush()
        if should_crawl:
            time.sleep(0.02)
    if s[-1] != "\n":
        print("")


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def game_over(should_crawl=True):
    if alice_hp > bob_hp:
        crawl("{} fainted!".format(bob_name), should_crawl)
        crawl("{} won!".format(alice_name), should_crawl)
    elif bob_hp > alice_hp:
        crawl("{} fainted!".format(alice_name), should_crawl)
        crawl("{} won!".format(bob_name), should_crawl)
    else:
        crawl("It's a draw!", should_crawl)
    crawl("Please play again!", should_crawl)


def print_hp():
    print(bcolors.HEADER + bcolors.BOLD + "{0: <10} [".format(alice_name) + int(alice_hp // 5)
          * "=" + (20 - int(alice_hp // 5)) * " " + "] {:.2f}".format(alice_hp))
    print("{0: <10} [".format(bob_name) + int(bob_hp // 5) * "=" +
          (20 - int(bob_hp // 5)) * " " + "] {:.2f}".format(bob_hp) + bcolors.ENDC)


friendliness = 0


def print_header(should_crawl=True):
    print_hp()

    if friendliness < 0.1:
        crawl("It's like an awkward first encounter...",
              should_crawl)
    elif friendliness < 0.3:
        crawl("Have these two met before?", should_crawl)
    elif friendliness < 0.5:
        crawl("Feels like an old reunion.", should_crawl)
    elif friendliness < 0.7:
        crawl("Friendship is in the air!", should_crawl)
    else:
        crawl("You can feel friendship all around you!",
              should_crawl)


def loop():
    global alice_hp
    global bob_hp
    global GAMMA
    global friendliness

    qc = QuantumCircuit(QuantumRegister(1, alice_name.lower()),
                        QuantumRegister(1, bob_name.lower()),QuantumRegister(1, 'ancilla'),ClassicalRegister(3))
    j_hat = np.matrix(scipy.linalg.expm(
        np.kron(-1j * GAMMA * d_hat, d_hat / 2)))
#    qc.unitary(Operator(j_hat), [0, 1], label="Friendship")
    qc.rx(-np.pi/2,2)
    qc.cx(2,0)
    qc.cx(2,1)

    def defect(q):
        qc.x(q)     #Defecting is just a \sigma_x now
#        qc.z(q)

    def quantum(q):
        qc.y(q)
        qc.x(q)

    def exec_gate(q, gate):
        for g in gate:
            if g == 'Z':
                qc.z(q)
            elif g == 'Y':
                qc.y(q)
            elif g == 'X':
                qc.x(q)
            elif g == 'H':
                qc.h(q)
            elif g == 'T':
                qc.t(q)
            elif g == 'S':
                qc.s(q)

    def prompt(q):
        clear_screen()
        print_header(should_crawl=False)
        options = tuple(random.sample(OPTION_NAMES, 3))

        while True:
            print("\nWhat will {} do?".format(
                alice_name if q == 0 else bob_name))

            print("[1] Fight\t[2] Heal\t[3] Befriend")
            print("[4] {}\t[5] {}\t[6] {}".format(*options))

            result = input(bcolors.WARNING + ">>> " + bcolors.ENDC)
            try:
                i = int(result) - 1
                if i == 0:
                    defect(q)
                    return "Fight"
                elif i == 1:
                    return "Heal"
                elif i == 2:
                    quantum(q)
                    return "Befriend"
                else:
                    exec_gate(q, rand_gates[options[i - 3]])
                    return options[i - 3]
            except (ValueError, IndexError):
                print("Please enter an option number.")
                continue

    if random.choice([True, False]):
        alice_move = prompt(0)
        bob_move = prompt(1)
    else:
        bob_move = prompt(1)
        alice_move = prompt(0)
    clear_screen()

#    qc.unitary(Operator(j_hat.H), [0, 1], label="Battle")
    qc.cx(2,1)
    qc.cx(2,0)
    qc.rx(np.pi/2,2)
    
    qc.measure(range(3),range(3))

    msg = ""
    msg += "{} used {}{}!\n".format(alice_name, alice_move,
                                    " to heal 5 HP" if alice_move == "Heal" else "")
    msg += "{} used {}{}!\n".format(bob_name, bob_move,
                                    " to heal 5 HP" if bob_move == "Heal" else "")

    if alice_move == "Heal":
        alice_hp += 5
    if bob_move == "Heal":
        bob_hp += 5
    bob_hp = min(bob_hp, 100)
    alice_hp = min(alice_hp, 100)
    
    shots=1000
    backend = Aer.get_backend('qasm_simulator')
    job = execute(qc, backend,shots=shots)
    result = job.result().get_counts()

    alice_exp = 0
    bob_exp = 0

    for outcome, prob in result.items():
        prob=prob/shots
        alice, bob = int(outcome[2]), int(outcome[1])  #These numbers have been changed to incorporate the extra qubit added
        alice, bob = payoff(alice, bob)
        alice_exp += prob * alice
        bob_exp += prob * bob

    if alice_move == "Befriend" and bob_move not in ("Befriend", "Heal") \
            and alice_exp > bob_exp or bob_move == "Befriend" \
            and alice_move not in ("Befriend", "Heal") and bob_exp > alice_exp:
        msg += bcolors.OKCYAN + bcolors.BOLD + \
            "It's the power of friendship!\n" + bcolors.ENDC

    if alice_exp == bob_exp:
        if alice_exp > 0:
            msg += bcolors.OKGREEN + \
                "It's a draw! Both sides heal {:.2f} HP!{}\n".format(
                    alice_exp, bcolors.ENDC)
        else:
            msg += bcolors.FAIL + \
                "It's a draw! Both sides take {:.2f} HP damage!{}\n".format(
                    abs(alice_exp), bcolors.ENDC)
        bob_hp += bob_exp
        alice_hp += alice_exp

    elif alice_exp > bob_exp:
        msg += bcolors.FAIL + "{} hits {} for {:.2f} HP damage!{}\n".format(
            alice_name, bob_name, alice_exp - bob_exp, bcolors.ENDC)
        bob_hp -= alice_exp - bob_exp
    else:
        msg += bcolors.FAIL + "{} hits {} for {:.2f} HP damage!{}\n".format(
            bob_name, alice_name, bob_exp - alice_exp, bcolors.ENDC)
        alice_hp -= bob_exp - alice_exp

    bob_hp = max(0, min(bob_hp, 100))
    alice_hp = max(0, min(alice_hp, 100))

    print_hp()
    print(qc)
    print("")
    crawl(msg)

    if alice_hp <= 0 or bob_hp <= 0:
        game_over()
        sys.exit(0)

    friendliness = min(max(abs(alice_hp - bob_hp) / 50,
                           1 - max(alice_hp, bob_hp) / 50), 1)
    GAMMA = friendliness * np.pi / 2

    time.sleep(2)
    clear_screen()
    print_header()


try:
    crawl(bcolors.OKGREEN + bcolors.BOLD +
          "A wild quantum state appeared!" + bcolors.ENDC)

    time.sleep(0.5)

    print_hp()
    while True:
        loop()
except (KeyboardInterrupt, EOFError):
    game_over(should_crawl=False)
