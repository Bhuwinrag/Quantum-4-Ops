
import numpy as np
from math import gcd, ceil, log2, isqrt
from fractions import Fraction
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import UnitaryGate, QFTGate
from qiskit_aer import AerSimulator

simulator = AerSimulator()

def modular_gate(a, N, n):
    U = np.zeros((2**n, 2**n), dtype=complex)
    for x in range(2**n):
        U[(a*x) % N if x < N else x, x] = 1
    return UnitaryGate(U)

def shor(N, a, shots):
    n = ceil(log2(N))
    m = 2*n

    qc = QuantumCircuit(m+n, m)
    qc.x(m)
    qc.h(range(m))

    for j in range(m):
        U = modular_gate(pow(a, 2**j, N), N, n)
        qc.append(U.control(), [j] + list(range(m, m+n)))

    qc.append(QFTGate(m).inverse(), range(m))
    qc.measure(range(m), range(m))

    counts = simulator.run(
        transpile(qc, simulator), shots=shots
    ).result().get_counts()

    for bits, _ in sorted(counts.items(),
                          key=lambda x: x[1], reverse=True):
        value = int(bits.replace(" ", ""), 2)

        if value:
            r = Fraction(value, 2**m).limit_denominator(N).denominator

            for k in range(1, N//r + 1):
                period = r*k

                if period % 2 == 0 and pow(a, period, N) == 1:
                    x = pow(a, period//2, N)
                    p = gcd(x-1, N)
                    q = gcd(x+1, N)

                    if p > 1 and q > 1 and p*q == N:
                        return p, q

    return None

def is_prime(N):
    if N < 2:
        return False
    for i in range(2, isqrt(N)+1):
        if N % i == 0:
            return False
    return True

def trial_factor(N):
    if N % 2 == 0:
        return 2, N//2

    for i in range(3, isqrt(N)+1, 2):
        if N % i == 0:
            return i, N//i

    return None

def factorize(N, a, shots):
    if N == 1:
        return []

    if is_prime(N):
        return [N]

    if N % 2 == 0:
        return factorize(N//2, a, shots) + [2]

    g = gcd(a, N)

    if 1 < g < N:
        p, q = g, N//g

    elif N <= 63:
        result = shor(N, a % N, shots)
        p, q = result if result else trial_factor(N)

    else:
        p, q = trial_factor(N)

    return factorize(p, a, shots) + factorize(q, a, shots)


N = int(input("Enter number: "))
a = int(input("Enter base: "))
shots = int(input("Enter shots: "))

factors = sorted(factorize(N, a, shots))

print("\nSHOR'S ALGORITHM")
print("Input:", N)
print("Factors:", tuple(factors))
print("Prime Factorization:", " × ".join(map(str, factors)))
