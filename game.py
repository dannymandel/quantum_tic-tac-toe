import numpy as np
import streamlit as st

def quantum_superposition():
    # Import Qiskit only when simulating so Streamlit can load the game logic
    # without initializing the simulator in its script thread.
    from qiskit import QuantumCircuit
    from qiskit.providers.basic_provider import BasicSimulator

    circuit = QuantumCircuit(1, 1)

    circuit.h(0)

    circuit.measure(0, 0)

    simulator = BasicSimulator()

    result = simulator.run(circuit, shots=1).result().get_counts()

    return result


def validate(arr):
    """Return 0 when the game is won or drawn, otherwise return 1."""
    arr = np.asarray(arr)
    if arr.shape != (3, 3):
        raise ValueError("The board must be a 3x3 NumPy array.")

    flag = True
    zero_ket = "|0>"
    one_ket = "|1>"

    # Check both diagonals first, for the user and the computer.
    if arr[0, 0] == one_ket and arr[1, 1] == one_ket and arr[2, 2] == one_ket:
        st.success("User has won!")
        flag = False
    elif arr[0, 0] == zero_ket and arr[1, 1] == zero_ket and arr[2, 2] == zero_ket:
        st.success("Computer wins!")
        flag = False
    elif arr[0, 2] == one_ket and arr[1, 1] == one_ket and arr[2, 0] == one_ket:
        st.success("User has won!")
        flag = False
    elif arr[0, 2] == zero_ket and arr[1, 1] == zero_ket and arr[2, 0] == zero_ket:
        st.success("Computer wins!")
        flag = False

    if not flag:
        return 0

    # Check each row for a user or computer win.
    for index in range(3):
        if list(arr[index, :]) == [one_ket, one_ket, one_ket]:
            st.success("User has won!")
            return 0
        if list(arr[index, :]) == [zero_ket, zero_ket, zero_ket]:
            st.success("Computer wins!")
            return 0

    # Check each column for a user or computer win.
    for index in range(3):
        if list(arr[:, index]) == [one_ket, one_ket, one_ket]:
            st.success("User has won!")
            return 0
        if list(arr[:, index]) == [zero_ket, zero_ket, zero_ket]:
            st.success("Computer wins!")
            return 0

    # The board is a draw once no superposition cells remain.
    if not any(value in ("|ψ>", "|ψ⟩") for value in arr.flat):
        st.write("It's a draw!")
        return 0

    return 1


def get_random_value():
    results = quantum_superposition()
    if not results:
        raise RuntimeError("The simulator returned no measurement results.")
    measured_state = next(iter(results))
    return f"|{measured_state}>"


if __name__ == "__main__":
    print(get_random_value())

