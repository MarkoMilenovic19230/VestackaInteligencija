import tkinter as tk
from tkinter import messagebox

class GameWindow(tk.Toplevel):
    def __init__(self, launcher, n):
        super().__init__()
        self.n = n
        self.current_player = launcher.start_color.get()
        self.board = {}
        self.last_move_player = "" 
        self.last_move_coords = ""

        # Podešavanje razmaka zavisno od n
        if n == 5:
            self.r = 22; self.h_gap = 82; self.v_gap = 58
        elif n == 7:
            self.r = 19; self.h_gap = 68; self.v_gap = 48
        else: # n=9
            self.r = 17; self.h_gap = 62; self.v_gap = 42

        num_cols = 2 * n - 1
        self.board_width = (num_cols - 1) * self.h_gap
        self.board_height = (num_cols - 1) * self.v_gap
        
        self.margin_x = 280  
        self.margin_y = 170  
        self.status_w = 360 
        
        self.win_w = self.board_width + (2 * self.margin_x) + self.status_w
        self.win_h = self.board_height + (2 * self.margin_y)
        
        self.title(f"Atoll - Igra (n={n})")
        self.geometry(f"{int(self.win_w)}x{int(self.win_h)}")
        self.configure(bg="white")

        self.CLR_GREEN = "#74B749"
        self.CLR_RED = "#F0503B"
        self.CLR_WHITE = "#E6E6E6"
        self.CLR_OUTLINE = "#BFBFBF"
        self.CLR_BLUE = "#2B5797"

        self.init_logic()
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.canvas.pack(expand=True, fill="both")
        self.canvas.bind("<Button-1>", self.on_click)
        self.draw_everything()

    def init_logic(self):
        self.col_sizes = []
        for i in range(self.n, 2*self.n): self.col_sizes.append(i)
        for i in range(2*self.n-2, self.n-1, -1): self.col_sizes.append(i)
        for c in range(len(self.col_sizes)):
            for r in range(self.col_sizes[c]): self.board[(c, r)] = None

    def draw_everything(self):
        self.canvas.delete("all")
        sx = self.margin_x 
        cy = self.win_h // 2
        
        self.hitboxes = {}
        col_labels = [chr(ord('A') + i) for i in range(len(self.col_sizes))]

        max_col_h = (max(self.col_sizes) - 1) * self.v_gap / 2
        label_y_top = cy - max_col_h - 100
        label_y_bot = cy + max_col_h + 100

        def get_node_y(c, r):
            size = self.col_sizes[c]
            y_start = cy - ((size - 1) * self.v_gap / 2)
            return y_start + r * self.v_gap

        for col in range(len(self.col_sizes)):
            x = sx + col * self.h_gap
            self.canvas.create_text(x, label_y_top, text=col_labels[col], font=("Consolas", 16, "bold"))
            self.canvas.create_text(x, label_y_bot, text=col_labels[col], font=("Consolas", 16, "bold"))

            for row in range(self.col_sizes[col]):
                y = get_node_y(col, row)
                val = self.board[(col, row)]
                color = self.CLR_WHITE
                if val == 'X': color = self.CLR_GREEN
                elif val == 'O': color = self.CLR_RED

                self.canvas.create_oval(x-self.r+2, y-2+2, x+self.r+2, y+2+2, fill="#D1D1D1", outline="")
                circle = self.canvas.create_oval(x-self.r, y-self.r, x+self.r, y+self.r, fill=color, outline=self.CLR_OUTLINE, width=1.5)
                self.hitboxes[circle] = (col, row)

        for r in range(self.n):
            self.canvas.create_text(sx - 145, get_node_y(0, r) + 45, text=str(r + 1), font=("Consolas", 14, "bold"))
            last_c = len(self.col_sizes) - 1
            self.canvas.create_text(sx + last_c * self.h_gap + 145, get_node_y(last_c, r) - 45, text=str(r + self.n), font=("Consolas", 14, "bold"))

        self.draw_islands_offset(sx, cy, self.h_gap, self.v_gap, self.r)

        side_x = self.win_w - 320
        curr_p_col = "zeleni" if self.current_player == 'X' else "crveni"
        
        self.canvas.create_text(side_x, 100, text="▶", font=("Segoe UI", 18), fill=self.CLR_BLUE, anchor="w")
        self.canvas.create_text(side_x + 30, 100, text="Sledeći na potezu:", font=("Segoe UI", 16), fill="black", anchor="w")
        self.canvas.create_text(side_x + 30, 140, text=f"{self.current_player} ({curr_p_col}) igrač", font=("Segoe UI", 16, "bold"), fill=self.CLR_BLUE, anchor="w")
        
        if self.last_move_player:
            self.canvas.create_text(side_x, 220, text="▶", font=("Segoe UI", 18), fill=self.CLR_BLUE, anchor="w")
            self.canvas.create_text(side_x + 30, 220, text=self.last_move_player, font=("Segoe UI", 16), fill="black", anchor="w")
            self.canvas.create_text(side_x, 260, text="▶", font=("Segoe UI", 18), fill=self.CLR_BLUE, anchor="w")
            self.canvas.create_text(side_x + 30, 260, text=self.last_move_coords, font=("Consolas", 18, "bold"), fill="black", anchor="w")

    def draw_islands_offset(self, sx, cy, h, v, r):
        def get_y_edge(c, top=True):
            size = self.col_sizes[c]
            y_s = cy - ((size - 1) * v / 2)
            return y_s if top else y_s + (size - 1) * v

        o = (self.n - 1) // 2
        num_stones = self.n - 1 
        off_y = v * 0.85 
        off_x_diag = 35 

        for i in range(num_stones):
            yf = cy - (num_stones/2 - 0.5)*v + i*v
            self._ball(sx - 70, yf, self.CLR_GREEN if i < o else self.CLR_RED, r)
            self._ball(sx + self.board_width + 70, yf, self.CLR_RED if i < o else self.CLR_GREEN, r)

        for i in range(num_stones):
            x_gap_left = sx + (i + 0.5) * h - off_x_diag
            y_nw = (get_y_edge(i) + get_y_edge(i+1)) / 2 - off_y
            self._ball(x_gap_left, y_nw, self.CLR_RED if i < o else self.CLR_GREEN, r)
            y_sw = (get_y_edge(i, False) + get_y_edge(i+1, False)) / 2 + off_y
            self._ball(x_gap_left, y_sw, self.CLR_GREEN if i < o else self.CLR_RED, r)
            idx_e = self.n - 1 + i
            x_gap_right = sx + (idx_e + 0.5) * h + off_x_diag
            y_ne = (get_y_edge(idx_e) + get_y_edge(idx_e+1)) / 2 - off_y
            self._ball(x_gap_right, y_ne, self.CLR_RED if i < o else self.CLR_GREEN, r)
            y_se = (get_y_edge(idx_e, False) + get_y_edge(idx_e+1, False)) / 2 + off_y
            self._ball(x_gap_right, y_se, self.CLR_GREEN if i < o else self.CLR_RED, r)

    def _ball(self, x, y, color, r):
        self.canvas.create_oval(x-r+2, y-r+2, x+r+2, y+r+2, fill="#D1D1D1", outline="")
        self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline=self.CLR_OUTLINE, width=1.5)

    def on_click(self, event):
        item = self.canvas.find_closest(event.x, event.y)[0]
        if item in self.hitboxes:
            c, r = self.hitboxes[item]
            if self.board[(c, r)] is None:
                col_letter = chr(ord('A') + c)
                row_label = r + 1 + max(0, c - (self.n - 1))
                p_col_txt = "zeleni" if self.current_player == 'X' else "crveni"
                self.last_move_player = f"Poslednji potez {self.current_player} igrača:"
                self.last_move_coords = f"('{col_letter}', {row_label})"
                self.board[(c, r)] = self.current_player
                self.current_player = 'O' if self.current_player == 'X' else 'X'
                self.draw_everything()
            else:
                messagebox.showwarning("Atoll", "Polje je već zauzeto!")