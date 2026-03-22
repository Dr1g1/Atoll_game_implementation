import math
import tkinter as tk
from tkinter import messagebox
import atoll_logika

SQRT3 = math.sqrt(3)

try:
    import atoll_alfabeta
    COMP_AVAILABLE = True
except ImportError:
    COMP_AVAILABLE = False
    print("Igra protiv racunara nije dostupna!")

class Point:
    def __init__(self, q, r, x, y, row, col, color):
        self.q = q
        self.r = r
        self.x = x
        self.y = y
        self.row = row
        self.col = col
        # trenutna prikazana boja
        self.color = color
        # base_color cuva originalnu boju polja (npr. polja po obodu: crvena/zelena)
        # koristi se za identifikaciju ostrva i strana po obodu nezavisno od trenutne boje
        self.base_color = color

    def draw(self, canvas, radius=12):
        canvas.create_oval(
            self.x - radius, self.y - radius,
            self.x + radius, self.y + radius,
            fill=self.color,
            outline=""
        )


class AtollBoard:
    def __init__(self, frame, map_radius=5, hex_size=30, width=700, height=700, vs_computer = False, comp_difficulty = "medium"):
        self.frame = frame
        self.move_log_text_id = None
        self.map_radius = map_radius
        self.hex_size = hex_size

        self.width = width
        self.height = height
        self.cx = width / 2
        self.cy = height / 2

        self.canvas = tk.Canvas(frame, width=self.width, height=self.height, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.bind("<Button-1>", self.on_click)

        self.points = {}   # (q,r) - point
        self.stones = {}   # (q,r) - 'red'/'green'

        self.players = ["red", "green"]
        self.player_colors = {"red": "#ff0000", "green": "#00ff00"}
        self.current_player_index = 0

        # konfiguracija igre protiv racunara
        self.vs_computer = vs_computer
        self.comp_difficulty = comp_difficulty
        self.computer_player = None
        self.alfabeta_instance = None # instanca atoll_alfabeta klase
        self.comp_turn = False # flag koji kaze da cekamo da komp odigra
        self.gameover_flag = False # da li je igra zavrsena

        self.turn_label = tk.Label(frame, text="", bg="black", fg="white", font=("Arial", 12))
        self.turn_label.pack(side="bottom", fill="x")

        self.update_hex_size()
        self.build_points()
        self.paint_sides()

        self.logic = atoll_logika.AtollLogic(self)

        self.draw_current_board()
        self.update_turn_label()

    def axial_to_pixel(self, q, r):
        x = self.cx + self.hex_size * 1.5 * q
        y = self.cy + self.hex_size * SQRT3 * (q / 2 + r)
        return x, y

    # fja za skaliranje table - kad se menjaju dimenzije:
    def update_hex_size(self):
        if self.map_radius <= 0:
            return
        max_width = self.width * 0.9
        max_height = self.height * 0.9
        hex_size_w = max_width / (1.5 * 2 * self.map_radius)
        hex_size_h = max_height / (SQRT3 * 2 * self.map_radius)
        self.hex_size = min(hex_size_w, hex_size_h)

    def build_points(self):
        radius = self.map_radius
        centers = {}
        row_groups = {}

        for q in range(-radius, radius + 1):
            for r in range(-radius, radius + 1):
                s = -q - r
                if abs(s) <= radius:
                    x, y = self.axial_to_pixel(q, r)
                    centers[(q, r)] = (x, y)
                    raw_row = q + r
                    row_groups.setdefault(raw_row, []).append((q, r))

        sorted_raw_rows = sorted(row_groups.keys())
        row_map = {raw: idx for idx, raw in enumerate(sorted_raw_rows)}

        all_q = sorted({q for (q, r) in centers.keys()})
        q_to_col = {q: idx for idx, q in enumerate(all_q)}

        self.points.clear()
        for (q, r), (x, y) in centers.items():
            row = row_map[q + r]
            col = q_to_col[q]
            p = Point(q=q, r=r, x=x, y=y, row=row, col=col, color="#ffffff")
            # base_color inicijalno isto kao color; paint_sides ce da prepravi base boju za polja po obodu
            p.base_color = p.color
            self.points[(q, r)] = p

    def paint_sides(self):
        R = self.map_radius
        cx, cy = self.cx, self.cy

        corner_coords = {(R, 0), (0, R), (-R, R), (-R, 0), (0, -R), (R, -R)}
        edge_points = []

        block_size = max(1, (R - 1) // 2)

        # prvo da se obeleze polja po obodu
        for (q, r), p in self.points.items():
            if abs(q) == R or abs(r) == R or abs(q + r) == R:
                if (q, r) in corner_coords:
                    p.color = "#000000"
                    p.base_color = p.color
                else:
                    angle = math.atan2(p.y - cy, p.x - cx)
                    edge_points.append((angle, p))

        # sortiramo po uglu i delimo na blokove za dve boje
        edge_points.sort(key=lambda t: t[0])

        for i, (_, p) in enumerate(edge_points):
            if (i // block_size) % 2 == 0:
                p.color = "#ff0000"
                p.base_color = p.color
            else:
                p.color = "#00ff00"
                p.base_color = p.color

    def draw_initial_board(self):
        self.canvas.delete("all")
        for point in self.points.values():
            point.draw(self.canvas, radius=self.hex_size * 0.6)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def draw_current_board(self):
        self.canvas.delete("all")
        for point in self.points.values():
            point.draw(self.canvas, radius=self.hex_size * 0.6)
        self.draw_board_labels()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def on_canvas_resize(self, event):
        self.width = event.width
        self.height = event.height
        self.cx = self.width / 2
        self.cy = self.height / 2
        self.update_hex_size()

        for point in self.points.values():
            point.x, point.y = self.axial_to_pixel(point.q, point.r)

        self.draw_current_board()

    def set_starting_player(self, player_name_or_index):
        if isinstance(player_name_or_index, int):
            if player_name_or_index in (0, 1):
                self.current_player_index = player_name_or_index
        else:
            if player_name_or_index in self.players:
                self.current_player_index = self.players.index(player_name_or_index)

        if self.vs_computer:
            human_player = self.players[self.current_player_index]
            self.computer_player = "green" if human_player == "red" else "red"

            if COMP_AVAILABLE:
                self.alfabeta_instance = atoll_alfabeta.AtollAlfaBeta(self, self.computer_player, self.comp_difficulty)
                print(f"Kompjuter igra kao: {self.computer_player}; Tezina: {self.comp_difficulty}")
            else:
                self.alfabeta_instance = None

            if self.current_player() == self.computer_player:
                self.canvas.after(0, self.computer_move)

        self.update_turn_label()

    def update_turn_label(self):
        current = self.players[self.current_player_index]
        color = self.player_colors[current]

        if self.vs_computer and current == self.computer_player and not self.gameover_flag:
            self.turn_label.config(text=f"Računar razmišlja... ({current.upper()})  ●", fg="yellow", bg="black")
        else:
            self.turn_label.config(text=f"Trenutni igrač: {current.upper()}  ●", fg="white", bg="black")
        # kratki log u konzoli
        print(f"[INFO] Trenutni igrač: {current} (boja {color})")

    def current_player(self):
        return self.players[self.current_player_index]

    def is_valid_move(self, point):
        if point is None:
            return False
        # boja polja #ffffff znaci slobodno
        return point.base_color == "#ffffff" and (point.q, point.r) not in self.stones

    def switch_player(self):
        self.current_player_index = 1 - self.current_player_index
        self.update_turn_label()

        # ako je sledeci computer, neka odigra nakon kratke pauze
        if self.vs_computer and not self.gameover_flag:
            current = self.current_player()
            if current == self.computer_player:
                self.canvas.after(0, self.computer_move)

    def log_move(self, point, valid=True):
        # ako je validan - igrac koji je upravo igrao; ako nije - igrac na potezu je ostao isti
        player = self.current_player() if valid else self.players[self.current_player_index]
        if valid:
            print(f"[MOVE] {player.upper()} igra: (q={point.q}, r={point.r}, row={point.row}, col={point.col})")
        else:
            print(f"[INVALID] {player.upper()} je pokušao potez na zauzetom polju: (q={point.q}, r={point.r})")

    def place_stone(self, q, r, player):
        if (q, r) not in self.points:
            return False
        if (q, r) in self.stones:
            return False
        # ako su polja na okviru onda ne moze
        # to je ako je base_color != white
        if self.points[(q, r)].base_color != "#ffffff":
            return False
        self.stones[(q, r)] = player
        # osvezi prikaz boje na tom pointu:
        self.points[(q, r)].color = self.player_colors.get(player, "#ffffff")
        self.draw_current_board() # ponovo tabla mora da se iscrta
        return True

    def nearest_point(self, x, y):
        # pretvaranje koordinata eventa u stvarne koordinate na canvasu
        canvas_x = self.canvas.canvasx(x)
        canvas_y = self.canvas.canvasy(y)

        best_point = None
        min_dist_sq = float('inf')

        for point in self.points.values():
            dx = canvas_x - point.x
            dy = canvas_y - point.y
            dist_sq = dx * dx + dy * dy

            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                best_point = point

        # dozvoljavamo se malo veci prag za detektovanje tj ceo hex_size
        if best_point and math.sqrt(min_dist_sq) < self.hex_size:
            return best_point
        return None

    def on_click(self, event):
        if self.gameover_flag or self.comp_turn:
            return

        if self.vs_computer and self.current_player() == self.computer_player:
            return

        print(f"Kliknuto: event.x={event.x}, event.y={event.y}")
        point = self.nearest_point(event.x, event.y)
        if not point:
            return

        current_player = self.current_player()  # igrac koji pokusava potez
        color = self.player_colors[current_player]

        if self.is_valid_move(point):
            # postavi vizuelno i u state
            ok = self.place_stone(point.q, point.r, current_player)
            if ok:
                # point.draw vec radi draw_current_board; ovde logujemo i zapisujemo potez
                self.log_move(point, valid=True)
                self.draw_move_log(point, current_player)

                # PROVERA KRAJA - provera da li igrac koji je upravo odigrao blize pobedi
                won, info = self.find_winning_path_for_player(current_player)
                if won:
                    messagebox.showinfo("Kraj igre", f"Igrač {current_player.upper()} je pobedio!\nPovezan put sa >= 7 kamenčića.")
                    # TO DO(MILA :D): RESTART ILI BACK TO MAIN MENU!!!!
                else:
                    # ako nema pobede igra se nastavlja
                    self.switch_player()
            else:
                # nije validno mesto, npr. base_color nije bela - mora se loguje
                self.log_move(point, valid=False)
                print(f"Igrač {current_player.upper()} pokušao je potez na nevalidnom polju. Pokušaj ponovo.")
        else:
            self.log_move(point, valid=False)
            print(f"Igrač {current_player.upper()} pokušao je potez na zauzetom polju ili na rubu. Pokušaj ponovo.")

    def computer_move(self):
        if self.gameover_flag:
            return
        if not self.vs_computer or self.alfabeta_instance is None:
            return
        current = self.current_player()
        if current != self.computer_player:
            return

        self.comp_turn = True
        self.update_turn_label()

        print(f"Kompjuter razmišlja...")

        best_move = self.alfabeta_instance.find_best_move()

        if best_move is None:
            print("Kompjuter nije nasao validan potez!")
            self.comp_turn = False
            return

        q, r = best_move
        point = self.points.get((q, r))

        if point and self.is_valid_move(point):
            # kompjuter odigrava potez
            ok = self.place_stone(q, r, self.computer_player)
            if ok:
                self.log_move(point, valid=True)
                self.draw_move_log(point, self.computer_player)
                print(f"Kompjuter je odigrao: ({q}, {r})")

                # provera pobede
                won, info = self.find_winning_path_for_player(self.computer_player)
                if won:
                    self.gameover_flag = True
                    self.comp_turn = False
                    messagebox.showinfo("Kraj igre",
                                        f"Kompjuter ({self.computer_player.upper()}) je pobedio!\nPovezan put sa >= 7 kamenčića.")
                    print(f"[KRAJ IGRE] Kompjuter ({self.computer_player.upper()}) je pobedio!")
                else:
                    # prebacujemo na coveka
                    self.comp_turn = False
                    self.switch_player()
        else:
            print(f"[COMPUTATION ERROR] Kompjuter vratio nevalidan potez: {best_move}")
            self.comp_turn = False

    def col_to_letter(self, col):
        if col == 0:
            return "Z"
        else:
            return chr(ord("A") + col - 1)

    def draw_move_log(self, point, player):
        col_letter = self.col_to_letter(point.col)
        row_number = point.row

        text = f"{player.upper()} -> {col_letter}{row_number}"

        if self.move_log_text_id is not None:
            self.canvas.delete(self.move_log_text_id)

        self.move_log_text_id = self.canvas.create_text(
            self.width - 10,
            10,
            anchor="ne",  # north-east kao desni gornji ugao
            text=text,
            fill="white",
            font=("Arial", 14, "bold")
        )

    def draw_board_labels(self):
        font_size = int(self.hex_size * 0.6)
        offset = self.hex_size * 2.2
        R = self.map_radius

        white = [p for p in self.points.values() if p.base_color == "#ffffff"]

        if not white:
            return

        min_x = min(p.x for p in white)
        max_x = max(p.x for p in white)
        min_y = min(p.y for p in white)
        max_y = max(p.y for p in white)

        y_top = min_y - offset
        y_bottom = max_y + offset
        x_left = min_x - offset
        x_right = max_x + offset

        # kolone(slova:)
        cols = {}
        for p in white:
            cols.setdefault(p.col, []).append(p)

        for col, points in cols.items():
            if col == 0:
                continue
            if any(abs(p.q) == R for p in points):
                continue

            letter = self.col_to_letter(col)
            ref_point = points[0]

            # gore
            self.canvas.create_text(ref_point.x, y_top, text=letter, fill="white", font=("Arial", font_size, "bold"))

            self.canvas.create_text(ref_point.x, y_bottom, text=letter, fill="white", font=("Arial", font_size, "bold"))

        # vrste(brojevi):
        rows = {}
        for p in self.points.values():
            if p.base_color == "#ffffff":
                rows.setdefault(p.row, []).append(p)

        if not rows:
            return

        max_row = max(rows.keys())

        for row, points in rows.items():
            if row == 0:
                continue
            # leva strana:
            if row <= R:
                anchor_point = min(points, key=lambda p: p.x)
                self.canvas.create_text(anchor_point.x - (offset * 1.2), anchor_point.y + 30,
                                        text=str(row), fill="white", font=("Arial", font_size, "bold"), anchor="e")
            # desna strana:
            else:
                anchor_point = max(points, key=lambda p: p.x)
                self.canvas.create_text(anchor_point.x + (offset * 1.2), anchor_point.y - 30,
                                        text=str(row), fill="white", font=("Arial", font_size, "bold"), anchor="w")

    # WRAPPERI ZA LOGIKU:

    def neighbors(self, coord):
        return self.logic.ret_neighbors(coord) # vraca sve susedne koordinate za datu koordinatu

    def compute_islands(self):
        return self.logic.ret_islands() # vraca ostrva grupisana po boji

    def compute_perimeter_island_order(self):
        return self.logic.ret_islands_order_by_perimeter() # vraca ostrva u redosledu kako se pojavljuju po obimu

    def path_exists_between_islands(self, island_a, island_b, player_color_name):
        return self.logic.path_between_islands(island_a, island_b, player_color_name) # proverava da li postoji put izmedju dva ostrva za igraca

    def shortest_stone_path_between_islands(self, island_a, island_b, player_color_name):
        return self.logic.ret_shortest_path(island_a, island_b, player_color_name) # vraca najkracu putanju(broj kamencica) izmedju dva ostrva

    def find_winning_path_for_player(self, player_color_name, min_stones_required=None):
        return self.logic.find_winner_path(player_color_name) # proverava da li igrac ima pobednicku putanju

    def generate_possible_moves(self, state_stones=None):
        return self.logic.form_all_possible_moves(state_stones) # generise sve moguce validne poteze za dato stanje

    def apply_move_to_state(self, state_stones, coord, player_color_name):
        return self.logic.form_new_state(state_stones, coord, player_color_name) # primenjuje potez na dato stanje i vraca novo stanje

    def generate_all_next_states(self, state_stones, player_color_name):
        return self.logic.ret_all_next_states(state_stones, player_color_name) # generose sva moguca sledeca stanja za igraca

