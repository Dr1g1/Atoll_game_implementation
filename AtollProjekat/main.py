import os
import tkinter as tk
from tkinter import font, messagebox
import webbrowser
import atollboard

againstComp = False
firstPlayer = None
boardSize = 5
compDifficulty = "medium"

window = tk.Tk()
window.geometry("600x400")
window.minsize(600, 400)

def show_frame(frame):
    frame.tkraise()

def changeOnHover(button, colorOnHover, colorOnLeave):
    button.bind("<Enter>", func=lambda e: button.config(
       background=colorOnHover))
    button.bind("<Leave>", func=lambda e: button.config(
            background=colorOnLeave))

def open_help():
    pdf_path = os.path.abspath("Atoll_rules.pdf")
    webbrowser.open_new(pdf_path)



# ------------------ Frame za meni ------------------
menu_frame = tk.Frame(window, bg="#031c73")
menu_frame.place(relwidth=1, relheight=1)

title_label = tk.Label(menu_frame, text="Atoll Game", fg="white", bg="#031c73")
title_label.pack(pady=20)

play_btn = tk.Button(menu_frame, text="Play", fg="white", bg="#cc3669", cursor="hand2",
                     command=lambda: show_frame(play_frame))
play_btn.pack(pady=10, fill="x", padx=200)
changeOnHover(play_btn, "#a94183", play_btn['bg'])

help_btn = tk.Button(menu_frame, text="Help", fg="white", bg="#f77156", cursor="hand2", command=open_help)
help_btn.pack(pady=10, fill="x", padx=200)
changeOnHover(help_btn, "#dd5d7c", help_btn['bg'])

quit_btn = tk.Button(menu_frame, text="Quit", fg="white", bg="#ffb44f",
                     command=window.destroy, cursor="hand2")
quit_btn.pack(pady=150, fill="x", padx=200)
changeOnHover(quit_btn, "#a7af48", quit_btn['bg'])

# ------------------ Frame za Play ekran -----------------------
play_frame = tk.Frame(window, bg="#031c73")
play_frame.place(relwidth=1, relheight=1)

def choose_cpu_mode():
    """Postavlja mod igre na čovek vs računar i prelazi na izbor težine."""
    global againstComp
    againstComp = True
    print("Izabran mod: Čovek vs Računar")
    show_frame(difficulty_frame)

def choose_human_mode():
    """Postavlja mod igre na čovek vs čovek i prelazi na izbor prvog igrača."""
    global againstComp
    againstComp = False
    print("Izabran mod: Čovek vs Čovek")
    show_frame(chooseFirst_frame)

btn_cpu = tk.Button(play_frame, text="Human VS Computer", fg="white", bg="#851977", cursor="hand2",  command=choose_cpu_mode)
btn_cpu.pack(fill="both", expand=True)
changeOnHover(btn_cpu, "#c02d6d", btn_cpu['bg'])

btn_human = tk.Button(play_frame, text="Human VS Human", fg="white", bg="#ffb44f", cursor="hand2",  command=choose_human_mode)
btn_human.pack(fill="both", expand=True)
changeOnHover(btn_human, "#a7af48", btn_human['bg'])

# ------------------ Frame za izbor težine AI-a (samo za mod protiv računara) -----------------------
difficulty_frame = tk.Frame(window, bg="#031c73")
difficulty_frame.place(relwidth=1, relheight=1)

difficulty_frame.columnconfigure(0, weight=1)
difficulty_frame.columnconfigure(1, weight=1)
difficulty_frame.columnconfigure(2, weight=1)
difficulty_frame.rowconfigure(0, weight=0)
difficulty_frame.rowconfigure(1, weight=3)

exit_difficulty_btn = tk.Button(
    difficulty_frame,
    text="Back",
    fg="white",
    bg="#ffb44f",
    font=("Impact", 18),
    cursor="hand2",
    command=lambda: show_frame(play_frame)
)
exit_difficulty_btn.place(relx=0.98, rely=0.05, anchor="ne")

title_difficulty = tk.Label(
    difficulty_frame,
    text="Choose AI Difficulty",
    font=("Impact", 32),
    fg="white",
    bg="#031c73"
)
title_difficulty.grid(row=0, column=0, columnspan=3, pady=50)

def set_difficulty_easy():
    """Postavlja laku težinu AI-a i prelazi na izbor prvog igrača."""
    global compDifficulty
    compDifficulty = "easy"
    print("Težina AI-a: Lako")
    show_frame(chooseFirst_frame)

def set_difficulty_medium():
    """Postavlja srednju težinu AI-a i prelazi na izbor prvog igrača."""
    global compDifficulty
    compDifficulty = "medium"
    print("Težina AI-a: Srednje")
    show_frame(chooseFirst_frame)

def set_difficulty_hard():
    """Postavlja tešku težinu AI-a i prelazi na izbor prvog igrača."""
    global compDifficulty
    compDifficulty = "hard"
    print("Težina AI-a: Teško")
    show_frame(chooseFirst_frame)

easy_btn = tk.Button(
    difficulty_frame,
    text="EASY",
    font=("Impact", 20),
    bg="#4ac100",
    fg="white",
    relief="flat",
    cursor="hand2",
    command=set_difficulty_easy
)
easy_btn.grid(row=1, column=0, sticky="nsew", pady=100, padx=20)
changeOnHover(easy_btn, "#6ae000", "#4ac100")

medium_btn = tk.Button(
    difficulty_frame,
    text="MEDIUM",
    font=("Impact", 20),
    bg="#ffb44f",
    fg="white",
    relief="flat",
    cursor="hand2",
    command=set_difficulty_medium
)
medium_btn.grid(row=1, column=1, sticky="nsew", pady=100, padx=20)
changeOnHover(medium_btn, "#ffc870", "#ffb44f")

hard_btn = tk.Button(
    difficulty_frame,
    text="HARD",
    font=("Impact", 20),
    bg="#dd5d7c",
    fg="white",
    relief="flat",
    cursor="hand2",
    command=set_difficulty_hard
)
hard_btn.grid(row=1, column=2, sticky="nsew", pady=100, padx=20)
changeOnHover(hard_btn, "#eb0505", "#dd5d7c")

#------------------------Frame za after play------------------------
chooseFirst_frame = tk.Frame(window, bg="#031c73")
chooseFirst_frame.place(relwidth=1, relheight=1)

chooseFirst_frame.columnconfigure(0, weight=1)
chooseFirst_frame.columnconfigure(1, weight=1)
chooseFirst_frame.rowconfigure(0, weight=0)
chooseFirst_frame.rowconfigure(1, weight=0)
chooseFirst_frame.rowconfigure(2, weight=3)

#--------------------Exit to menu dugme--------------------------------
exit_btn = tk.Button(
    chooseFirst_frame,
    text="Exit to main menu",
    fg="white",
    bg = "#ffb44f",
    font=("Impact", 18),
    cursor="hand2",
    command = lambda: show_frame(menu_frame)
)
exit_btn.place(relx = 0.98, rely = 0.05, anchor = "ne")

title_first = tk.Label(
    chooseFirst_frame,
    text="First player",
    font=("Impact", 32),
    fg="white",
    bg="#031c73"
)
title_first.grid(row=0, column=0, columnspan=2, pady=100)

size_frame = tk.Frame(chooseFirst_frame, bg="#031c73")
size_frame.grid(row=1, column=0, columnspan=2, pady=10)

size_label = tk.Label(
    size_frame,
    text="Board size:",
    font=("Impact", 18),
    fg="white",
    bg="#031c73"
)
size_label.pack(side="left", padx=10)

size_spinbox = tk.Spinbox(
    size_frame,
    values=(5, 7, 9),
    font=("Impact", 18),
    width=5,
    justify="center",
    state="readonly"
)
size_spinbox.pack(side="left")
size_spinbox.delete(0, "end")
size_spinbox.insert(0, "5")


def choose_red():
    global firstPlayer
    firstPlayer = "red"
    print("Red starts")
    start_game()

def choose_green():
    global firstPlayer
    firstPlayer = "green"
    print("Green starts")
    start_game()

red_btn = tk.Button(
    chooseFirst_frame,
    text="RED starts",
    font=("Impact", 26),
    bg="#dd5d7c",
    fg="white",
    relief="flat",
    cursor="hand2",
    command=choose_red
)
red_btn.grid(row=2, column=0, sticky="nsew",pady=100, padx=30)
changeOnHover(red_btn, "#eb0505", "#dd5d7c")

green_btn = tk.Button(
    chooseFirst_frame,
    text="GREEN starts",
    font=("Impact", 26),
    bg="#00b9bd",
    relief="flat",
    fg="white",
    cursor="hand2",
    command=choose_green
)
green_btn.grid(row=2, column=1, sticky="nsew",  pady=100, padx=30)
changeOnHover(green_btn, "#4ac100", "#00b9bd")

# ------------------ Frame za igranje igre ------------------

game_frame = tk.Frame(window, bg="black")
game_frame.place(relwidth=1, relheight=1)

board_frame = tk.Frame(game_frame, bg="black")
board_frame.pack(expand=True, fill="both")


def start_game():
    global boardSize, firstPlayer, againstComp, compDifficulty

    boardSize = int(size_spinbox.get())

    for widget in board_frame.winfo_children():
        widget.destroy()

    board = atollboard.AtollBoard(
        frame=board_frame,
        map_radius=boardSize,
        hex_size=30,
        width=500,
        height=500,
        vs_computer = againstComp,
        comp_difficulty = compDifficulty
    )

    if firstPlayer is not None:
        board.set_starting_player(firstPlayer)

    board.draw_initial_board()
    show_frame(game_frame)

    # Informacije o pokrenutoj igri
    mode_str = "Čovek vs Računar" if againstComp else "Čovek vs Čovek"
    diff_str = f" (Težina: {compDifficulty})" if againstComp else ""
    print(f"[IGRA ZAPOČETA] Mod: {mode_str}{diff_str}, Veličina: {boardSize}x{boardSize}, Prvi igra: {firstPlayer}")

# ------------------ Responsive font i padding ------------------
def resize(event):
    title_size = max(12, int(event.height / 10))
    button_size = max(10, int(event.height / 20))

    title_label.config(font=("Impact", title_size))
    play_btn.config(font=("Impact", button_size))
    help_btn.config(font=("Impact", button_size))
    quit_btn.config(font=("Impact", button_size))
    btn_cpu.config(font=("Impact", button_size))
    btn_human.config(font=("Impact", button_size))

    title_label.pack_configure(pady=int(event.height / 40))
    play_btn.pack_configure(pady=int(event.height / 80))
    help_btn.pack_configure(pady=int(event.height / 80))
    quit_btn.pack_configure(pady=int(event.height / 80))

window.bind("<Configure>", resize)

show_frame(menu_frame)

window.mainloop()
