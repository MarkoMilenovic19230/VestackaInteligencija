import tkinter as tk
from tkinter import messagebox
import copy

class GameWindow(tk.Toplevel):
    def __init__(self, launcher, n):
        super().__init__()
        self.n = n
        self.current_player = launcher.start_color.get()
        self.board = {} # Ovo je naše "stanje igre"
        self.last_move_player = "" 
        self.last_move_coords = ""
        self.game_over = False

        # GUI podešavanja iz tvog originalnog koda
        if n == 5:
            self.r = 22; self.h_gap = 82; self.v_gap = 58
        elif n == 7:
            self.r = 19; self.h_gap = 68; self.v_gap = 48
        else: # n=9
            self.r = 17; self.h_gap = 62; self.v_gap = 42

        num_cols = 2 * n - 1
        self.board_width = (num_cols - 1) * self.h_gap
        self.board_height = (num_cols - 1) * self.v_gap
        self.margin_x = 280; self.margin_y = 170; self.status_w = 360 
        self.win_w = self.board_width + (2 * self.margin_x) + self.status_w
        self.win_h = self.board_height + (2 * self.margin_y)
        
        self.title(f"Atoll - Igra (n={n})")
        self.geometry(f"{int(self.win_w)}x{int(self.win_h)}")
        self.configure(bg="white")

        self.CLR_GREEN = "#74B749"; self.CLR_RED = "#F0503B"; self.CLR_WHITE = "#E6E6E6"
        self.CLR_OUTLINE = "#BFBFBF"; self.CLR_BLUE = "#2B5797"

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

    # =========================================================================
    # ZAHTEV: OPERATORI PROMENE STANJA PROBLEMA (IGRE)
    # =========================================================================

    def get_all_possible_moves(self, state):
        """Vraća listu svih mogućih poteza (praznih polja) za zadato stanje."""
        return [coords for coords, val in state.items() if val is None]

    def get_next_state(self, state, move, player):
        """Formira novo stanje igre na osnovu igrača, poteza i trenutnog stanja."""
        new_state = copy.deepcopy(state)
        new_state[move] = player
        return new_state

    def get_all_possible_states(self, state, player):
        """Formira sva moguća stanja igre za zadatog igrača."""
        moves = self.get_all_possible_moves(state)
        return [self.get_next_state(state, move, player) for move in moves]

    # =========================================================================
    # ZAHTEV: PROVERA KRAJA IGRE I PUTA IZMEĐU NESUSEDNIH OSTRVA (MIN 7)
    # =========================================================================

    def get_neighbors(self, c, r):
        neighbors = []
        if (c, r - 1) in self.board: neighbors.append((c, r - 1))
        if (c, r + 1) in self.board: neighbors.append((c, r + 1))
        if c < self.n - 1:
            offsets = [(c-1, r-1), (c-1, r), (c+1, r), (c+1, r+1)]
        elif c == self.n - 1:
            offsets = [(c-1, r-1), (c-1, r), (c+1, r-1), (c+1, r)]
        else:
            offsets = [(c-1, r), (c-1, r+1), (c+1, r-1), (c+1, r)]
        for nc, nr in offsets:
            if (nc, nr) in self.board: neighbors.append((nc, nr))
        return neighbors

    def get_island_mapping(self):
        """
        Precizno mapira 6 sektora ostrva na polja table u obliku neprekidnog prstena.
        Ovo osigurava da susedna ostrva na tabli imaju susedne indekse u listi (distanca 1).
        """
        n, o, num_stones = self.n, (self.n - 1) // 2, self.n - 1
        mapping = []

        # 1. LEVA ivica (odozgo na dole)
        for i in range(num_stones):
            mapping.append({'color': 'X' if i < o else 'O', 'cells': [(0, i), (0, i+1)]})
        
        # 2. SW ivica (sleva na desno po dnu)
        for i in range(num_stones):
            mapping.append({'color': 'X' if i < o else 'O', 'cells': [(i, self.col_sizes[i]-1), (i+1, self.col_sizes[i+1]-1)]})
            
        # 3. SE ivica (sleva na desno po dnu)
        for i in range(num_stones):
            c1, c2 = n-1+i, n+i
            mapping.append({'color': 'X' if i < o else 'O', 'cells': [(c1, self.col_sizes[c1]-1), (c2, self.col_sizes[c2]-1)]})
            
        # 4. DESNA ivica (odozdo na gore - obrnuto da bi se nastavio krug)
        for i in range(num_stones - 1, -1, -1):
            mapping.append({'color': 'O' if i < o else 'X', 'cells': [(2*n-2, i), (2*n-2, i+1)]})
            
        # 5. NE ivica (zdesna na levo po vrhu)
        for i in range(num_stones - 1, -1, -1):
            mapping.append({'color': 'O' if i < o else 'X', 'cells': [(n-1+i, 0), (n+i, 0)]})
            
        # 6. NW ivica (zdesna na levo ka početku)
        for i in range(num_stones - 1, -1, -1):
            mapping.append({'color': 'O' if i < o else 'X', 'cells': [(i, 0), (i+1, 0)]})
            
        return mapping
    def check_end_game(self, state, player):
        """
        Proverava kraj igre: spajanje dva NESUSEDNA sopstvena ostrva 
        uz poštovanje minimalne perimeter distance od 7 polja.
        """
        mapping = self.get_island_mapping()
        n_side = self.n - 1  # broj polja po jednoj stranici hexagon-a
        total_pos = len(mapping)
        threshold = 7 

        # 1. Određujemo koji 'sektori' (6 komada za svakog igrača) su okupirani
        # sektor_id ide od 0 do 5 (6 strana hexagon-a)
        occupied_sectors = {} # sektor_id -> lista mapping_indeksa koji su zauzeti

        for idx, item in enumerate(mapping):
            if item['color'] == player:
                # Proveravamo da li igrač ima kamenčić na bar jednom polju ovog mapping elementa
                if any(state.get(c) == player for c in item['cells']):
                    sector_id = idx // n_side # Grupišemo mapping elemente u 6 sektora
                    if sector_id not in occupied_sectors:
                        occupied_sectors[sector_id] = []
                    occupied_sectors[sector_id].append(idx)

        # 2. Proveravamo parove sektora
        sector_ids = list(occupied_sectors.keys())
        for i in range(len(sector_ids)):
            for j in range(i + 1, len(sector_ids)):
                s1, s2 = sector_ids[i], sector_ids[j]

                # USLOV NESUSEDNOSTI: Sektori ne smeju biti isti niti direktni susedi (0-1, 1-2... 5-0)
                # U krugu od 6, razlika mora biti bar 2 ili 3
                sector_dist = min(abs(s1 - s2), 6 - abs(s1 - s2))
                if sector_dist < 2: 
                    continue # Preskačemo ako su ostrva na istoj ili susednoj stranici

                # 3. Provera puta (BFS) između bilo koje dve tačke ova dva nesusedna sektora
                for idx1 in occupied_sectors[s1]:
                    for idx2 in occupied_sectors[s2]:
                        
                        # Provera distance u kamenčićima (min 7)
                        dist = min(abs(idx1 - idx2), total_pos - abs(idx1 - idx2))
                        if dist < threshold:
                            continue

                        # BFS pretraga putanje kroz unutrašnjost table
                        starts = [c for c in mapping[idx1]['cells'] if state.get(c) == player]
                        targets = set([c for c in mapping[idx2]['cells'] if state.get(c) == player])
                        
                        queue, visited = list(starts), set(starts)
                        found = False
                        while queue:
                            curr = queue.pop(0)
                            if curr in targets: 
                                found = True
                                break
                            for nb in self.get_neighbors(*curr):
                                if state.get(nb) == player and nb not in visited:
                                    visited.add(nb)
                                    queue.append(nb)
                        
                        if found: return True
        return False

    # =========================================================================
    # GUI I INTERAKCIJA
    # =========================================================================

    def on_click(self, event):
        if self.game_over: return
        ids = self.canvas.find_closest(event.x, event.y)
        if not ids: return
        item = ids[0]

        if item in self.hitboxes:
            move = self.hitboxes[item]
            # ZAHTEV: Provera ispravnosti poteza (polje mora biti None)
            if self.board[move] is None:
                # 1. Odigravanje poteza (promena stanja)
                self.board = self.get_next_state(self.board, move, self.current_player)
                
                # 2. Ažuriranje prikaza
                col_letter = chr(65 + move[0])
                row_label = move[1] + 1 + max(0, move[0] - (self.n - 1))
                self.last_move_player = f"Poslednji potez {self.current_player} igrača:"
                self.last_move_coords = f"('{col_letter}', {row_label})"
                
                # 3. Provera kraja igre i određivanje pobednika
                if self.check_end_game(self.board, self.current_player):
                    self.draw_everything()
                    winner = "ZELENI (X)" if self.current_player == 'X' else "CRVENI (O)"
                    messagebox.showinfo("Kraj igre", f"POBEDA! Igrač {winner} je spojio ostrva udaljena min 7 polja!")
                    self.game_over = True
                    return

                # 4. Naizmenična promena igrača
                self.current_player = 'O' if self.current_player == 'X' else 'X'
                self.draw_everything()
            else:
                messagebox.showwarning("Atoll", "Polje je zauzeto! Unesite ispravan potez.")

    def draw_everything(self):
        self.canvas.delete("all")
        sx, cy = self.margin_x, self.win_h // 2
        self.hitboxes = {}
        col_labels = [chr(65 + i) for i in range(len(self.col_sizes))]

        def get_node_y(c, r):
            y_start = cy - ((self.col_sizes[c] - 1) * self.v_gap / 2)
            return y_start + r * self.v_gap

        for col in range(len(self.col_sizes)):
            x = sx + col * self.h_gap
            self.canvas.create_text(x, cy - (max(self.col_sizes)-1)*self.v_gap/2 - 100, text=col_labels[col], font=("Consolas", 16, "bold"))
            self.canvas.create_text(x, cy + (max(self.col_sizes)-1)*self.v_gap/2 + 100, text=col_labels[col], font=("Consolas", 16, "bold"))
            for row in range(self.col_sizes[col]):
                y = get_node_y(col, row)
                val = self.board[(col, row)]
                color = self.CLR_WHITE if not val else (self.CLR_GREEN if val=='X' else self.CLR_RED)
                self.canvas.create_oval(x-self.r+2, y-2+2, x+self.r+2, y+2+2, fill="#D1D1D1", outline="")
                circle = self.canvas.create_oval(x-self.r, y-self.r, x+self.r, y+self.r, fill=color, outline=self.CLR_OUTLINE, width=1.5)
                self.hitboxes[circle] = (col, row)

        for r in range(self.n):
            self.canvas.create_text(sx - 145, get_node_y(0, r) + 45, text=str(r + 1), font=("Consolas", 14, "bold"))
            last_c = len(self.col_sizes) - 1
            self.canvas.create_text(sx + last_c * self.h_gap + 145, get_node_y(last_c, r) - 45, text=str(r + self.n), font=("Consolas", 14, "bold"))

        self.draw_islands_offset(sx, cy, self.h_gap, self.v_gap, self.r)
        
        side_x = self.win_w - 320
        p_disp_col = self.CLR_GREEN if self.current_player == 'X' else self.CLR_RED
        self.canvas.create_text(side_x + 30, 100, text="Sledeći na potezu:", font=("Segoe UI", 16), anchor="w")
        self.canvas.create_text(side_x + 30, 140, text=f"{self.current_player} igrač", font=("Segoe UI", 16, "bold"), fill=p_disp_col, anchor="w")
        if self.last_move_player:
            self.canvas.create_text(side_x + 30, 220, text=self.last_move_player, font=("Segoe UI", 16), anchor="w")
            self.canvas.create_text(side_x + 30, 260, text=self.last_move_coords, font=("Consolas", 18, "bold"), anchor="w")

    def draw_islands_offset(self, sx, cy, h, v, r):
        def get_y_edge(c, top=True):
            y_s = cy - ((self.col_sizes[c] - 1) * v / 2)
            return y_s if top else y_s + (self.col_sizes[c] - 1) * v
        o, num_stones = (self.n - 1) // 2, self.n - 1
        for i in range(num_stones):
            yf = cy - (num_stones/2 - 0.5)*v + i*v
            self._ball(sx - 70, yf, self.CLR_GREEN if i < o else self.CLR_RED, r)
            self._ball(sx + self.board_width + 70, yf, self.CLR_RED if i < o else self.CLR_GREEN, r)
            xl, xr = sx+(i+0.5)*h-35, sx+(self.n-1+i+0.5)*h+35
            self._ball(xl, (get_y_edge(i)+get_y_edge(i+1))/2-v*0.85, self.CLR_RED if i < o else self.CLR_GREEN, r)
            self._ball(xl, (get_y_edge(i, False)+get_y_edge(i+1, False))/2+v*0.85, self.CLR_GREEN if i < o else self.CLR_RED, r)
            self._ball(xr, (get_y_edge(self.n-1+i)+get_y_edge(self.n+i))/2-v*0.85, self.CLR_RED if i < o else self.CLR_GREEN, r)
            self._ball(xr, (get_y_edge(self.n-1+i, False)+get_y_edge(self.n+i, False))/2+v*0.85, self.CLR_GREEN if i < o else self.CLR_RED, r)

    def _ball(self, x, y, color, r):
        self.canvas.create_oval(x-r+2, y-r+2, x+r+2, y+r+2, fill="#D1D1D1", outline="")
        self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline=self.CLR_OUTLINE, width=1.5)