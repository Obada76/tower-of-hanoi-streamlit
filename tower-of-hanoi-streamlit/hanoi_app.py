from pywebio.input import input
from pywebio.output import put_text, put_buttons, put_row, put_column, put_html, clear, toast
from pywebio import start_server
import time
import os

colors = ["red", "orange", "gold", "green", "blue", "indigo", "violet"]

class HanoiWeb:
    def __init__(self):
        self.num_disks = 0
        self.pegs = [[], [], []]
        self.move_count = 0
        self.move_history = []
        self.selected_peg = None
        self.allow_autosolve = True
        self.solving = False
        self.select_disk_count()

    def setup(self):
        self.pegs = [list(range(self.num_disks, 0, -1)), [], []]
        self.move_count = 0
        self.move_history = []
        self.selected_peg = None
        self.allow_autosolve = True
        self.solving = False
        self.render()

    def render(self):
        clear()
        put_html("<h2 style='text-align:center;'>Tower of Hanoi</h2>")
        put_text(f"Moves: {self.move_count} | Optimal: {2**self.num_disks - 1}")

        peg_outputs = []
        for i in range(3):
            peg_html = """
            <div style='position: relative; height: 220px; width: 120px; border: 2px solid black; padding-top: 10px; display: flex; flex-direction: column-reverse; align-items: center; background-color: #f5f5f5;'>
                <div style='position: absolute; bottom: 10px; left: 50%; transform: translateX(-50%); width: 8px; height: 200px; background-color: #444; border-radius: 4px; z-index: 0;'></div>
            """
            for disk in self.pegs[i]:
                disk_width = 20 + disk * 20
                color = colors[disk - 1]
                peg_html += f"<div style='margin: 2px; height: 20px; width: {disk_width}px; background:{color}; border-radius: 5px; z-index: 1; position: relative;'></div>"
            peg_html += "</div>"

            peg_column = [put_html(peg_html)]
            if not self.solving:
                def make_handler(peg_idx):
                    return lambda btn_val=None: self.handle_click(peg_idx)
                peg_column.append(put_buttons([f"Select Peg {i+1}"], [make_handler(i)], small=True))

            peg_outputs.append(put_column(peg_column, scope=f'peg{i}'))

        put_row(peg_outputs, size='auto')
        put_html("<div style='margin-top: 10px;'></div>")

        if not self.solving:
            put_row([
                put_buttons(['Undo', 'Reset', 'Auto Solve', 'Disk Selection', 'Exit'],
                            [self.undo_move, self.setup, self.auto_solve, self.go_to_disk_selection, self.exit_game])
            ], size='auto')

    def handle_click(self, peg_idx):
        if self.solving:
            return  # Ignore clicks during auto solve
        if self.selected_peg is None:
            if self.pegs[peg_idx]:
                self.selected_peg = peg_idx
                toast(f"Selected Peg {peg_idx+1}", color='info')
        else:
            if self.selected_peg != peg_idx:
                self.move_disk(self.selected_peg, peg_idx)
            else:
                toast("Cancelled selection", color='warning')
            self.selected_peg = None
            self.render()

    def move_disk(self, from_peg, to_peg):
        if not self.pegs[from_peg]:
            return
        if self.pegs[to_peg] and self.pegs[to_peg][-1] < self.pegs[from_peg][-1]:
            toast("Invalid move: larger disk on smaller one", color='error')
            return

        disk = self.pegs[from_peg].pop()
        self.pegs[to_peg].append(disk)
        self.move_count += 1
        self.move_history.append((disk, from_peg, to_peg))
        self.allow_autosolve = False  # Disable auto solve after a manual move

        if len(self.pegs[2]) == self.num_disks:
            toast(f"🎉 You solved it in {self.move_count} moves!", color='success')

    def select_disk_count(self):
        while True:
            user_input = input("Enter number of disks (3-7):")
            try:
                count = int(user_input)
                if 3 <= count <= 7:
                    self.num_disks = count
                    break
                else:
                    toast("Please enter a number between 3 and 7.", color='warn')
            except:
                toast("Invalid input. Please enter a number.", color='error')

        self.setup()

    def go_to_disk_selection(self, _=None):
        self.select_disk_count()

    def undo_move(self):
        if not self.move_history:
            return
        disk, from_peg, to_peg = self.move_history.pop()
        self.pegs[to_peg].pop()
        self.pegs[from_peg].append(disk)
        self.move_count -= 1
        self.render()

    def auto_solve(self):
        if not self.allow_autosolve:
            toast("⚠️ Auto Solve is only available at the start or after Reset.", color='warn')
            return

        self.solving = True
        self.render()

        def solve(n, src, dest, aux):
            if n == 0:
                return
            solve(n - 1, src, aux, dest)
            time.sleep(0.5)
            self.move_disk(src, dest)
            self.render()
            solve(n - 1, aux, dest, src)

        solve(self.num_disks, 0, 2, 1)
        self.solving = False
        self.render()

    def exit_game(self, _=None):
        toast("Exiting game...", color='warn')
        time.sleep(0.5)
        os._exit(0)

def main():
    HanoiWeb()

if __name__ == '__main__':
    start_server(main, port=8080, debug=True)
