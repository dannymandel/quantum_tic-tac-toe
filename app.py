import numpy as np
import streamlit as st
import pandas as pd
import runpy
from pathlib import Path
import subprocess
import sys


game = runpy.run_path(str(Path(__file__).with_name("game.py")))


def reset_game():
    st.session_state.quantum_board = np.full((3, 3), "|ψ⟩", dtype=object)
    st.session_state.game_over = False
    st.session_state.needs_validation = False
    st.session_state.current_player = "You"
    st.session_state.move_history = []
    st.session_state.qubit_message = "Welcome to the quantum kitty lab! Pick any open square to begin."
    st.session_state.celebration_shown = False


WINNING_LINES = (
    ((0, 0), (0, 1), (0, 2)),
    ((1, 0), (1, 1), (1, 2)),
    ((2, 0), (2, 1), (2, 2)),
    ((0, 0), (1, 0), (2, 0)),
    ((0, 1), (1, 1), (2, 1)),
    ((0, 2), (1, 2), (2, 2)),
    ((0, 0), (1, 1), (2, 2)),
    ((0, 2), (1, 1), (2, 0)),
)


def run_measurement():
    script_path = str(Path(__file__).with_name("game.py"))
    result = subprocess.run(
        [sys.executable, script_path],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    measured_state = result.stdout.strip().splitlines()[-1]
    if measured_state not in ("|0>", "|1>"):
        raise RuntimeError(f"Unexpected measurement result: {measured_state}")
    return measured_state


def would_make_line(board, row, col, mark):
    possible_board = board.copy()
    possible_board[row, col] = mark
    return any(
        all(possible_board[r, c] == mark for r, c in line)
        for line in WINNING_LINES
    )


def winner_for_board(board):
    for line in WINNING_LINES:
        states = [board[row, col] for row, col in line]
        if states == ["|1>", "|1>", "|1>"]:
            return "You"
        if states == ["|0>", "|0>", "|0>"]:
            return "Computer"
    if not any(value in ("|ψ>", "|ψ⟩") for value in board.flat):
        return "Draw"
    return None


def choose_computer_cell(board):
    empty_cells = [
        (row, col)
        for row in range(3)
        for col in range(3)
        if board[row, col] in ("|ψ>", "|ψ⟩")
    ]
    if not empty_cells:
        return None

    # Aim for a computer win, then try to block a user win.
    for row, col in empty_cells:
        if would_make_line(board, row, col, "|0>"):
            return row, col
    for row, col in empty_cells:
        if would_make_line(board, row, col, "|1>"):
            return row, col

    # Otherwise prefer the center, then a corner, then any open square.
    for preferred in ((1, 1), (0, 0), (0, 2), (2, 0), (2, 2)):
        if preferred in empty_cells:
            return preferred
    return empty_cells[0]


def measure_cell(row, col):
    board = st.session_state.quantum_board
    if board[row, col] in ("|ψ>", "|ψ⟩") and not st.session_state.game_over:
        measured_state = run_measurement()
        board[row, col] = measured_state
        st.session_state.needs_validation = True
        st.session_state.current_player = "Computer"
        st.session_state.move_history.append(
            f"You measured square {row * 3 + col + 1}: {measured_state}"
        )
        st.session_state.qubit_message = (
            "Purrfect collapse! Your square became |1>!"
            if measured_state == "|1>"
            else "A surprise quantum wiggle! Your square became |0>."
        )

def main():
    st.markdown(
        """
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400;700&display=swap');
          .stApp,
          [data-testid="stAppViewContainer"] {
            background: #fffaf2;
            color: #453852;
          }
          [data-testid="stHeader"] {
            background: transparent;
          }
          [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f1eaff 0%, #fffaf2 100%);
            border-right: 3px dotted #9b7bbb;
          }
          [data-testid="stSidebar"] * {
            color: #59466b;
          }
          h1, h2, h3 {
            color: #785a91;
          }
          p, label, [data-testid="stCaptionContainer"] {
            color: #51475a;
          }
          [data-testid="stMainBlockContainer"] {
            border-top: 3px dotted #9b7bbb;
            border-bottom: 3px dotted #9b7bbb;
            padding: 2.25rem 1.5rem 1.25rem;
          }
          [data-testid="stSidebar"] [data-testid="stImage"] {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
          }
          [data-testid="stSidebar"] [data-testid="stImage"] img {
            display: block;
            margin: 0 auto !important;
            align-self: center;
          }
          [data-testid="stButton"] > button {
            background: #eee5fa;
            color: #59466b;
            border: 1px solid #cbb8df;
            border-radius: 12px;
          }
          [data-testid="stButton"] > button:hover {
            background: #dcefeb;
            color: #315f60;
            border-color: #78aaa5;
          }
          [data-testid="stSelectbox"] [role="combobox"] {
            background: #fffdf9;
            border-color: #b99dcc;
            border-radius: 10px;
          }
          [data-testid="stAlert"] {
            background: #edf6f2;
            border-left-color: #78aaa5;
            color: #315f60;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )
    menu = ["Play", "Instructions", "About Quantum Concepts", "About My Game"]
    st.sidebar.image(str(Path(__file__).with_name("qubit.svg")), width="stretch")
    st.sidebar.markdown(
        "<div style='text-align:center; margin-top:-0.5rem; margin-bottom:0.8rem;'>"
        "<span style='background:#eee5fa; color:#644b7b; padding:0.3rem 0.85rem; "
        "border-radius:999px; font-weight:600;'>♡ Qubit the cat ♡</span></div>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        """
        <div style="text-align:center; padding: 0.25rem 0 0.75rem;">
          <div style="font-family:'Dancing Script', cursive; font-size:1.65rem; font-weight:700; line-height:1.25; color:#785a91;">
            ✨ Qubit the Cat's ✨<br>Quantum Tic-Tac-Toe
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    option = st.sidebar.selectbox("Menu", menu)

    if "quantum_board" not in st.session_state:
        reset_game()
    else:
        # Preserve games already open while adding defaults for newly added features.
        st.session_state.setdefault(
            "qubit_message",
            "Welcome to the quantum kitty lab! Pick any open square to begin.",
        )
        st.session_state.setdefault("celebration_shown", False)

    if option == "Play":
        title_col, mascot_col = st.columns([5, 1])
        title_col.title("Qubit'sQuantum Tic-Tac-Toe")
        mascot_col.image(str(Path(__file__).with_name("qubit.svg")), width=72)
        st.write("Welcome to Qubit's quantum kitty lab! Pick an open |ψ⟩ square and watch it collapse.")
        st.caption("After your turn, Qubit picks a square too. Match three states in a row, column, or diagonal to win.")

        st.markdown("#### ✨ Quantum state guide ✨")
        guide_cols = st.columns(3)
        guide_cols[0].markdown("**|ψ⟩**  \nStill in superposition")
        guide_cols[1].markdown("**|1⟩**  \nYour winning state")
        guide_cols[2].markdown("**|0⟩**  \nQubit's winning state")

        if st.session_state.needs_validation:
            st.session_state.needs_validation = False
            st.session_state.game_over = game["validate"](st.session_state.quantum_board) == 0

        if st.session_state.current_player == "Computer" and not st.session_state.game_over:
            computer_cell = choose_computer_cell(st.session_state.quantum_board)
            if computer_cell is not None:
                row, col = computer_cell
                measured_state = run_measurement()
                st.session_state.quantum_board[row, col] = measured_state
                st.session_state.move_history.append(
                    f"Computer measured square {row * 3 + col + 1}: {measured_state}"
                )
                st.session_state.qubit_message += (
                    f" Qubit measured square {row * 3 + col + 1}; it became {measured_state}. Meow!"
                )
                st.session_state.game_over = game["validate"](st.session_state.quantum_board) == 0
                st.session_state.current_player = "You"

        st.info(f"🐱 Qubit says: {st.session_state.qubit_message}")
        st.button("🔄 Clean the Litterbox", on_click=reset_game)
        board = st.session_state.quantum_board
        for row in range(3):
            columns = st.columns(3)
            for col in range(3):
                value = board[row, col]
                cell_number = row * 3 + col + 1
                columns[col].button(
                    f"{cell_number}: {value}",
                    key=f"play_cell_{cell_number}",
                    on_click=measure_cell,
                    args=(row, col),
                    disabled=(
                        value not in ("|ψ>", "|ψ⟩")
                        or st.session_state.game_over
                        or st.session_state.current_player != "You"
                    ),
                )

        if not st.session_state.game_over:
            st.markdown("### 🌟 Your turn! Pick a sparkly square 🌟")
        else:
            winner = winner_for_board(board)
            if winner == "You":
                st.success("You win! Qubit is doing a happy tail wiggle! 🎉🐱")
                if not st.session_state.celebration_shown:
                    st.balloons()
                    st.session_state.celebration_shown = True
            elif winner == "Computer":
                st.info("Qubit wins this round! Those tiny quantum paws were quick! 🐾")
                if not st.session_state.celebration_shown:
                    st.snow()
                    st.session_state.celebration_shown = True
            else:
                st.info("It's a draw! The quantum kitties are equally clever. 🤝")
                if not st.session_state.celebration_shown:
                    st.toast("A purrfectly balanced board! ✨")
                    st.session_state.celebration_shown = True
        if st.session_state.move_history:
            st.markdown("#### 🐾 Move-by-move story")
            for move in st.session_state.move_history:
                st.write(f"- {move}")

    elif option == "Instructions":
        psi = "|ψ⟩"
        board = np.array ([[psi,psi,psi],[psi,psi,psi],[psi,psi,psi]])
        st.dataframe(board)
        instruction_1 = "Each cell in the board represents a quantum state in superposition. The symbol |ψ⟩ indicates that the state is in superposition until measured."
        st.write(instruction_1)
        instruction_2 = "When a measurement is made(User making move), the superposition collapses to a definite state, either |0⟩ or |1⟩."
        st.write(instruction_2)
        instruction_3 = "Players will interact with these quantum states, making decisions based on the outcomes of measurements."
        st.write(instruction_3)
        instruction_4 = "The game will simulate measurements and the collapse of quantum states, allowing players to experience quantum phenomena interactively."
        st.write(instruction_4)
        board_numbering = pd.DataFrame([[1,2,3],[4,5,6],[7,8,9]])
        st.dataframe(board_numbering)
        
    
    elif option == "About Quantum Concepts":
        st.write("Quantum Computing is a rapidly evolving field that leverages the principles of quantum mechanics to perform computations more efficiently than classical computers in certain tasks."
        "This program demonstrates basic concepts of quantum computing. It includes Superposition and collapse of quantum states. A particle can exist in multiple states simultaneously until measured."
        "This can shown by the superposition symbol |ψ⟩. When the particle is measured, the superposition collapses to a definite state |0⟩ or |1⟩. This is how we are able " \
        "to incorperate classical computing concepts into quantum computing. My game is a perfect demonstration of advanced topics like quantum superposition and measurement in a fun and interactive way"
        "that is fun and easy for players to grasp.")

    elif option == "About My Game":
        st.write("How I built my game")

        st.write("Players learn about superposition and measurement by choosing a square and watching its state change. I used Streamlit to build the pages and interactive parts of the app. The menu uses st.sidebar.selectbox(), the board uses st.columns() and st.button(), and st.session_state keeps track of the board and turns when the app refreshes.")

        st.write("I used pandas DataFrame() and st.dataframe() to show example boards on the Instructions page. I used st.markdown() for styled text and st.image() to show Qubit the cat. The win celebrations use Streamlit's st.balloons() and st.snow() functions.")

        st.write("The quantum circuit is in my game file. It uses Qiskit's QuantumCircuit, applies a Hadamard gate with circuit.h(0), and measures the qubit with circuit.measure(0, 0). Qiskit's BasicSimulator runs the circuit in software; the game does not use a real quantum computer. The validate() function checks the board for a winning row, column, diagonal, or a draw.")

        st.write("Problems I fixed")

        st.write("I had Qiskit import and measurement-result errors. I updated the simulator import and changed the measurement code to return either |0> or |1>. The simulator also sometimes crashed when it ran inside Streamlit, so I moved each measurement into a separate Python process.")

        st.write("I also had trouble putting the board and example tables on the right pages. I kept the playable board in Play and the example boards in Instructions. When I added Qubit's messages and celebrations, older open sessions were missing the new values, so I added defaults for them.")


if __name__ == "__main__":
    main()
