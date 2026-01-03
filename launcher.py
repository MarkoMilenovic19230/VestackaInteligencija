import tkinter as tk
from tkinter import messagebox
from game_window import GameWindow # Uvozimo drugu klasu

class AtollLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Atoll - Podešavanja")
        self.root.geometry("500x550")
        self.root.configure(bg="#F8F9FA")

        self.n = tk.IntVar(value=5)
        self.game_mode = tk.StringVar(value="PvC")
        self.first_player = tk.StringVar(value="Covek")
        self.start_color = tk.StringVar(value="X")

        self.setup_menu()

    def setup_menu(self):
        main_f = tk.Frame(self.root, bg="white", padx=30, pady=30, highlightthickness=1, highlightbackground="#D1D1D1")
        main_f.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(main_f, text="Atoll - Podešavanja", font=("Segoe UI", 18, "bold"), bg="white", fg="#2C5F91").pack(pady=(0, 20))
        tk.Label(main_f, text="Veličina table n (5, 7 ili 9):", bg="white").pack(anchor="w")
        tk.Entry(main_f, textvariable=self.n, width=10).pack(anchor="w", pady=(0, 15))

        tk.Label(main_f, text="Mod igre:", font=("Segoe UI", 10, "bold"), bg="white").pack(anchor="w")
        tk.Radiobutton(main_f, text="Čovek protiv Računara", variable=self.game_mode, value="PvC", bg="white").pack(anchor="w")
        tk.Radiobutton(main_f, text="Čovek protiv Čoveka", variable=self.game_mode, value="PvP", bg="white").pack(anchor="w")

        tk.Label(main_f, text="\nKo igra prvi:", font=("Segoe UI", 10, "bold"), bg="white").pack(anchor="w")
        tk.Radiobutton(main_f, text="Čovek", variable=self.first_player, value="Covek", bg="white").pack(anchor="w")
        tk.Radiobutton(main_f, text="Računar", variable=self.first_player, value="Racunar", bg="white").pack(anchor="w")

        tk.Label(main_f, text="\nBoja prvog igrača:", font=("Segoe UI", 10, "bold"), bg="white").pack(anchor="w")
        tk.Radiobutton(main_f, text="Zeleni (X)", variable=self.start_color, value="X", bg="white").pack(anchor="w")
        tk.Radiobutton(main_f, text="Crveni (O)", variable=self.start_color, value="O", bg="white").pack(anchor="w")

        tk.Button(main_f, text="ZAPOČNI IGRU", bg="#2C5F91", fg="white", font=("Segoe UI", 11, "bold"), 
                  command=self.launch_game, padx=20, pady=10, relief="flat", cursor="hand2").pack(pady=(30, 0))

    def launch_game(self):
        n_val = self.n.get()
        if n_val not in [5, 7, 9]:
            messagebox.showerror("Greška", "n mora biti 5, 7 ili 9!")
            return
        self.root.withdraw()
        # Otvara se prozor za igru
        GameWindow(self, n_val)