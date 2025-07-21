import tkinter as tk
from tkinter import messagebox, simpledialog
import winsound
import time
import threading


class HanoiGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Tower of Hanoi")
        self.center_window(640, 500)

        # Title
        self.title_label = tk.Label(root, text="Tower of Hanoi", font=("Arial", 20, "bold"))
        self.title_label.pack(pady=10)

        # Canvas for game
        self.canvas = tk.Canvas(root, width=600, height=400, bg="white")
        self.canvas.pack()

        # Controls
        self.controls_frame = tk.Frame(root)
        self.controls_frame.pack(pady=5)

        self.move_label = tk.Label(self.controls_frame, text="Moves: 0", font=("Arial", 12))
        self.move_label.pack(side="left", padx=10)

        self.optimal_label = tk.Label(self.controls_frame, text="Optimal Moves: 0", font=("Arial", 12))
        self.optimal_label.pack(side="left", padx=10)

        self.reset_button = tk.Button(self.controls_frame, text="Reset", command=self.reset_game)
        self.reset_button.pack(side="left", padx=10)

        self.undo_button = tk.Button(self.controls_frame, text="Undo", command=self.undo_move)
        self.undo_button.pack(side="left", padx=10)

        self.solve_button = tk.Button(self.controls_frame, text="Auto Solve", command=self.start_auto_solver)
        self.solve_button.pack(side="left", padx=10)

        # Pegs & Disk Settings
        self.colors = ["red", "orange", "gold", "green", "blue", "indigo", "violet"]
        self.peg_x = [150, 300, 450]
        self.canvas.bind("<Button-1>", self.handle_click)

        self.interaction_enabled = True
        self.start_game()

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def start_game(self):
        self.num_disks = simpledialog.askinteger("Number of Disks", "Enter number of disks (3-7):", minvalue=3, maxvalue=7)
        if not self.num_disks:
            self.root.destroy()
            return

        self.move_count = 0
        self.pegs = [[], [], []]
        self.move_history = []
        self.selected_disk = None
        self.source_peg = None
        self.canvas.delete("all")
        self.create_pegs()
        self.create_disks()
        self.update_move_labels()

    def create_pegs(self):
        for x in self.peg_x:
            self.canvas.create_rectangle(x - 5, 150, x + 5, 350, fill="black")

    def create_disks(self):
        for size in range(self.num_disks, 0, -1):
            width = size * 30
            x = self.peg_x[0]
            y = 340 - len(self.pegs[0]) * 20
            color = self.colors[size - 1]
            rect = self.canvas.create_rectangle(x - width // 2, y, x + width // 2, y + 20, fill=color)
            self.pegs[0].append((rect, size, color))

    def update_move_labels(self):
        self.move_label.config(text=f"Moves: {self.move_count}")
        optimal = 2 ** self.num_disks - 1
        self.optimal_label.config(text=f"Optimal Moves: {optimal}")

    def handle_click(self, event):
        if not self.interaction_enabled:
            return

        clicked_peg = self.get_peg_from_x(event.x)
        if clicked_peg is None:
            return

        if self.selected_disk is None:
            if self.pegs[clicked_peg]:
                self.selected_disk = self.pegs[clicked_peg][-1]
                self.source_peg = clicked_peg
                self.canvas.itemconfig(self.selected_disk[0], outline="black", width=2)
        else:
            if self.can_place(self.selected_disk[1], clicked_peg):
                self.move_disk(self.source_peg, clicked_peg)
                self.move_count += 1
                self.update_move_labels()
                self.check_win()
            else:
                messagebox.showinfo("Invalid Move", "You can't place a larger disk on a smaller one.")
                self.canvas.itemconfig(self.selected_disk[0], outline="", width=1)
            self.selected_disk = None
            self.source_peg = None

    def get_peg_from_x(self, x):
        for i in range(3):
            if abs(x - self.peg_x[i]) < 50:
                return i
        return None

    def can_place(self, disk_size, peg):
        if not self.pegs[peg]:
            return True
        return disk_size < self.pegs[peg][-1][1]

    def move_disk(self, from_peg, to_peg, record=True, play_sound=True):
        if not self.pegs[from_peg]:
            return  # Nothing to move

        disk = self.pegs[from_peg][-1]
        disk_size = disk[1]

        if self.pegs[to_peg] and self.pegs[to_peg][-1][1] < disk_size:
            print(f"Invalid move: Trying to place disk {disk_size} on smaller disk {self.pegs[to_peg][-1][1]}")
            return  # Prevent invalid move

        disk = self.pegs[from_peg].pop()
        self.canvas.itemconfig(disk[0], outline="", width=1)
        x = self.peg_x[to_peg]
        y = 340 - len(self.pegs[to_peg]) * 20
        width = disk[1] * 30
        self.canvas.coords(disk[0], x - width // 2, y, x + width // 2, y + 20)
        self.pegs[to_peg].append(disk)

        if record:
            self.move_history.append((disk, from_peg, to_peg))

        if play_sound:
            winsound.Beep(440 + 40 * disk[1], 100)


    def undo_move(self):
        if not self.interaction_enabled or not self.move_history:
            return
        disk, from_peg, to_peg = self.move_history.pop()
        self.pegs[to_peg].pop()
        self.canvas.itemconfig(disk[0], outline="", width=1)
        x = self.peg_x[from_peg]
        y = 340 - len(self.pegs[from_peg]) * 20
        width = disk[1] * 30
        self.canvas.coords(disk[0], x - width // 2, y, x + width // 2, y + 20)
        self.pegs[from_peg].append(disk)
        self.move_count -= 1
        self.update_move_labels()

    def check_win(self):
        if len(self.pegs[2]) == self.num_disks:
            messagebox.showinfo("Congratulations!", f"You solved it in {self.move_count} moves!")
            self.interaction_enabled = True

    def reset_game(self):
        self.interaction_enabled = True
        self.start_game()

    def start_auto_solver(self):
        if not self.interaction_enabled:
            return
        self.interaction_enabled = False
        thread = threading.Thread(target=self.solve_hanoi_thread)
        thread.start()

    def solve_hanoi_thread(self):
        time.sleep(0.5)
        self.solve_hanoi(self.num_disks, 0, 2, 1)
        self.interaction_enabled = True

    def solve_hanoi(self, n, src, dest, aux):
        if n == 0:
            return
        self.solve_hanoi(n - 1, src, aux, dest)
        time.sleep(0.4)
        self.move_disk(src, dest, record=True)
        self.move_count += 1
        self.update_move_labels()
        self.root.update()
        self.solve_hanoi(n - 1, aux, dest, src)

# Main program launch
if __name__ == "__main__":
    root = tk.Tk()
    game = HanoiGame(root)
    root.mainloop()

