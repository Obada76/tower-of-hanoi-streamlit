import streamlit as st
import time

# Constants
PEG_COUNT = 3
COLORS = ["#ff4b4b", "#ffa500", "#ffd700", "#32cd32", "#1e90ff", "#4b0082", "#ee82ee"]

# Initialize session state
def initialize_state():
    st.session_state.pegs = [[i for i in range(st.session_state.num_disks, 0, -1)], [], []]
    st.session_state.selected_peg = None
    st.session_state.move_count = 0
    st.session_state.solving = False
    st.session_state.auto_moves = []
    st.session_state.last_num_disks = st.session_state.num_disks

# Valid move
def is_valid_move(from_peg, to_peg):
    if not st.session_state.pegs[from_peg]:
        return False
    if not st.session_state.pegs[to_peg]:
        return True
    return st.session_state.pegs[from_peg][-1] < st.session_state.pegs[to_peg][-1]

# Move disk
def move_disk(from_peg, to_peg):
    if is_valid_move(from_peg, to_peg):
        disk = st.session_state.pegs[from_peg].pop()
        st.session_state.pegs[to_peg].append(disk)
        st.session_state.move_count += 1

# Handle clicks
def handle_peg_click(peg_index):
    if st.session_state.selected_peg is None:
        if st.session_state.pegs[peg_index]:  # Select only if peg has disk
            st.session_state.selected_peg = peg_index
    else:
        if st.session_state.selected_peg != peg_index:
            move_disk(st.session_state.selected_peg, peg_index)
        st.session_state.selected_peg = None

# Draw the game
def render_game():
    cols = st.columns(PEG_COUNT)
    for i in range(PEG_COUNT):
        with cols[i]:
            peg_disks = st.session_state.pegs[i]
            is_selected = st.session_state.selected_peg == i

            peg_html = "<div style='height: 250px; position: relative;'>"
            peg_html += "<div style='position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); width: 6px; height: 200px; background-color: black;'></div>"

            for idx, disk in enumerate(reversed(peg_disks)):  # Top to bottom
                disk_width = 20 + disk * 20
                color = COLORS[disk - 1]
                top_position = 180 - (idx * 25)
                border = "4px solid yellow" if is_selected and idx == 0 else "none"
                peg_html += f"<div style='position: absolute; top: {top_position}px; left: 50%; transform: translateX(-50%); background: {color}; width: {disk_width}px; height: 20px; border-radius: 5px; border: {border};'></div>"

            peg_html += "</div>"
            st.markdown(peg_html, unsafe_allow_html=True)

            if st.button(" ", key=f"peg_click_{i}"):
                handle_peg_click(i)

# Solve logic
def generate_hanoi_moves(n, src, dest, aux, moves):
    if n == 1:
        moves.append((src, dest))
    else:
        generate_hanoi_moves(n - 1, src, aux, dest, moves)
        moves.append((src, dest))
        generate_hanoi_moves(n - 1, aux, dest, src, moves)

def auto_solve():
    if not st.session_state.solving:
        st.session_state.auto_moves = []
        generate_hanoi_moves(st.session_state.num_disks, 0, 2, 1, st.session_state.auto_moves)
        st.session_state.solving = True

    if st.session_state.auto_moves:
        from_peg, to_peg = st.session_state.auto_moves.pop(0)
        move_disk(from_peg, to_peg)
        time.sleep(0.3)
        st.rerun()

# Sidebar controls
st.sidebar.title("Tower of Hanoi Settings")

if "num_disks" not in st.session_state:
    st.session_state.num_disks = 3

st.session_state.num_disks = st.sidebar.slider("Number of Disks", 3, 7, st.session_state.num_disks)

if "last_num_disks" not in st.session_state or st.session_state.num_disks != st.session_state.get("last_num_disks", 0):
    initialize_state()

if st.sidebar.button("Reset Game"):
    initialize_state()

if st.sidebar.button("Auto Solve"):
    auto_solve()

# Game title and status
st.title("Tower of Hanoi")
optimal_moves = 2 ** st.session_state.num_disks - 1
st.write(f"Moves: {st.session_state.move_count} | Optimal: {optimal_moves}")

render_game()

# Win condition
if len(st.session_state.pegs[2]) == st.session_state.num_disks:
    st.success(f"🎉 Congratulations! You solved it in {st.session_state.move_count} moves.")
    st.session_state.solving = False
