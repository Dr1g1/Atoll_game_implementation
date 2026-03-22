import random
import math
from collections import deque

class AtollAlfaBeta:
    """" klasa koja implementira alfa beta logiku i fje evaluacije"""

    def __init__(self, board,computer_color, difficulty = "medium"):
        self.board = board
        # inicijalizuje racunar-igraca:
        self.computer_color = computer_color
        # suprotna boja - ovo je potrebno za evaluaciju
        self.human_color = "green" if computer_color == "red" else "red"
        self.difficulty = difficulty

        # dubina pretrazivanja u zavisnosti od tezine:
        self.depth_map = {
            "easy": 1,
            "medium": 2,
            "hard": 3,
        }
        self.max_depth = self.depth_map.get(difficulty, 2)

        # brojac za evaluirana stanja
        self.evaluated_nodes_counter = 0

    def find_best_move(self):
        """ glavna fja koja evaluira stanje table i vraca najbolji potez za racunar:"""
        self.evaluated_nodes_counter = 0
        current_state = dict(self.board.stones)

        possible_moves = self.board.generate_possible_moves(current_state)

        if possible_moves is None:
            return None

        # alfa-beta inicijalne vrednosti:
        alpha = -math.inf
        beta = math.inf
        best_move = None
        best_value = -math.inf

        # za svaki potez od mogucih cemo da evaluiamo stanje table
        for move in possible_moves:
            new_state = self.board.apply_move_to_state(current_state, move, self.computer_color)
            if new_state is None:
                continue

            value = self.alfabeta(new_state, self.max_depth - 1, alpha, beta, False)

            if value > best_value:
                best_value = value
                best_move = move

            alpha = max(alpha, value)

        print(f"Evaluirano cvorova: {self.evaluated_nodes_counter}; Najbolji potez: {best_move}; Vrednost: {best_value}")
        return best_move

    def alfabeta(self, state, depth, alpha, beta, max_player):
        self.evaluated_nodes_counter += 1

        if depth == 0:
            return self.evaluation_function(state)

        # proveravamo da li je neko pobedio
        winner = self.check_winner(state)
        if winner == self.computer_color:
            return 10000  # racunar pobedio
        elif winner == self.human_color:
            return -10000  # covek pobedio

        current_player = self.computer_color if max_player else self.human_color

        next_states = self.board.generate_all_next_states(state, current_player)

        if not next_states:
            return self.evaluation_function(state) # ako nema vise poteza evaluiramo trenutno stanje

        if max_player:
            # kompjuter igra
            max_evaluation = -math.inf
            for move, new_state in next_states:
                e_score = self.alfabeta(new_state, depth - 1, alpha, beta, False)
                max_evaluation = max(max_evaluation, e_score)
                alpha = max(alpha, e_score)
                if beta <= alpha:
                    break  # beta odsecanje
            return max_evaluation
        else:
            # covek igra
            min_evaluation = math.inf
            for move, new_state in next_states:
                e_score = self.alfabeta(new_state, depth - 1, alpha, beta, True)
                min_evaluation = min(min_evaluation, e_score)
                beta = min(beta, e_score)
                if beta <= alpha:
                    break  # alfa odsecanje
            return min_evaluation

    def check_winner(self, state):
        """ proverava da li je neko od igraca na putu da pobedi u datom stanju """

        #postavimo stanje privremeno:
        prev_stones = dict(self.board.stones)
        self.board.stones = state

        # proveravamo oba igraca
        for player in [self.computer_color, self.human_color]:
            winner, _ = self.board.find_winning_path_for_player(player)
            if winner:
                self.board.stones = prev_stones
                return player

        # vracamo originalno stanje
        self.board.stones = prev_stones
        return None

    # fja koja poziva odgovarajucu heuristiku na osnovu tezine
    # vraca float vrednost - ako racunar vodi onda je pozitivna, ako je negativna onda covek vodi
    def evaluation_function(self, state):
        prev_stones = dict(self.board.stones)
        self.board.stones = state

        score = 0.0

        # faktor 1: progress ka pobedi - koliko smo blizu da povezemo dovoljno ostrva
        computer_win_progress = self.progress_evaluation(self.computer_color)
        human_win_progress = self.progress_evaluation(self.human_color)
        score += (computer_win_progress - human_win_progress) * 200

        # faktor 2: najkrace putanje izmedju suprotnih ostrva - kraca putanja = bolja pozicija
        computer_path_len = self.shortest_paths_evaluation(self.computer_color)
        human_path_len = self.shortest_paths_evaluation(self.human_color)
        score += (computer_path_len - human_path_len) * 100

        # faktor 3: povezanost - vise povezanih ostrva = bolja pozicija
        computer_island_connection = self.connectivity_evaluation(self.computer_color)
        human_island_connection = self.connectivity_evaluation(self.human_color)
        score += (computer_island_connection - human_island_connection) * 80

        # faktor 4: blokiranje protivnika
        sabotage_val = self.sabotage_evaluation(state)
        score += sabotage_val * 60

        # faktor 5: kamencici na kljucnim presecima veceg broja putanja su vredniji
        computer_strategy = self.strategy_evaluation(state, self.computer_color)
        human_strategy = self.strategy_evaluation(state, self.human_color)
        score += (computer_strategy - human_strategy) * 30

        # vracamo staro stanje
        self.board.stones = prev_stones

        return score

    # pomocne fje za evaluaciju:

    def progress_evaluation(self, player_color):
        winner, info = self.board.find_winning_path_for_player(player_color)

        if winner:
            # ako je vec pobedio ide maksimalni score
            return 1000.0

        score = 0.0

        # info je lista tuple-ova: (island1, island1, stones_needed, arc_length)
        if isinstance(info, list) and info:
            # nalazimo najduzi luk koji smo formirali
            best_arc = 0
            best_stones = float('inf')

            for i in info:
                if len(i) >= 4:
                    _, _, stones, arc_length = i[:4]

                    # sto je duzi luk (vise ostrva) - to je bolje
                    if arc_length > best_arc:
                        best_arc = arc_length
                        best_stones = stones if stones is not None else float('inf')
                    elif arc_length == best_arc and stones is not None:
                        best_stones = min(best_stones, stones)

            # score baziran na najboljoj formiranoj vezi
            if best_arc > 0:
                # duzi luk = veci score
                score += best_arc ** 2 * 10

                # kraca putanja = veci bonus
                if best_stones != float('inf'):
                    # sto manje kamencica treba to je bolje
                    score += max(0, 100 - best_stones * 8)

        return score

    def shortest_paths_evaluation(self, player_color):
        perimeter_islands = self.board.compute_perimeter_island_order()
        if len(perimeter_islands) < 2:
            return 0.0

        player_hex = self.board.player_colors[player_color]
        player_islands = []

        # identifikujemo nasa ostrva
        for idx, island in enumerate(perimeter_islands):
            sample = next(iter(island))
            if self.board.points[sample].base_color == player_hex:
                player_islands.append((idx, island))

        if len(player_islands) < 2:
            return 0.0

        total_islands = len(perimeter_islands)
        threshold = (total_islands // 2) + 1  # koliko ostrva treba povezati za pobedu

        score = 0.0
        best_path_length = float('inf')

        # Proveravamo parove ostrva i nalazimo najkraće putanje
        for i in range(len(player_islands)):
            for j in range(i + 1, len(player_islands)):
                idx_a, island_a = player_islands[i]
                idx_b, island_b = player_islands[j]

                # Računamo koliko ostrva obuhvata luk između ovih ostrva
                forward = (idx_b - idx_a) % total_islands + 1
                backward = total_islands - ((idx_b - idx_a) % total_islands) + 1
                arc_length = min(forward, backward)

                # Nalazimo najkraću putanju
                path_length = self.board.shortest_stone_path_between_islands(
                    island_a, island_b, player_color
                )

                if path_length is not None:
                    best_path_length = min(best_path_length, path_length)

                    # Što je kraća putanja, to je veći score
                    # Takođe, score je veći ako luk pokriva više ostrva
                    path_score = max(0, 50 - path_length * 4) * (arc_length / threshold)
                    score += path_score

        # Bonus ako imamo vrlo kratke putanje
        if best_path_length < 5:
            score += (5 - best_path_length) * 20

        return score

    def connectivity_evaluation(self, player_color):
        perimeter_islands = self.board.compute_perimeter_island_order()
        player_hex = self.board.player_colors[player_color]

        my_islands = []
        for island in perimeter_islands:
            sample = next(iter(island))
            if self.board.points[sample].base_color == player_hex:
                my_islands.append(island)

        if len(my_islands) < 2:
            return 0.0

        connected_count = 0

        # Brojimo koliko parova ostrva je već povezano
        for i in range(len(my_islands)):
            for j in range(i + 1, len(my_islands)):
                if self.board.path_exists_between_islands(
                        my_islands[i], my_islands[j], player_color
                ):
                    connected_count += 1

        # Više povezanih parova = bolji score
        return float(connected_count) * 15

    def sabotage_evaluation(self, state):
        # Ova funkcija meri razliku u "prosečnoj dužini najkraćih putanja"
        # Ako su protivnikove putanje duže zbog naših kamenčića, to je dobro

        player_hex = self.board.player_colors[self.computer_color]
        opponent_hex = self.board.player_colors[self.human_color]

        # Brojimo kamenčiće svakog igrača koji su "u putu" drugom igraču
        blocking_score = 0.0

        # Pronalazimo kritična polja - ona kroz koja moraju da prođu putanje
        perimeter_islands = self.board.compute_perimeter_island_order()

        opp_islands = []
        for island in perimeter_islands:
            sample = next(iter(island))
            if self.board.points[sample].base_color == opponent_hex:
                opp_islands.append(island)

        # Za svaki naš kamenčić, proveravamo da li smanjuje
        # protivničke opcije za povezivanje
        for coord, color in state.items():
            if color == self.computer_color:
                # Brojimo koliko protivničkih ostrva je blizu ovog kamenčića
                neighbors = self.board.neighbors(coord)
                opponent_island_proximity = 0

                for n in neighbors:
                    if n in self.board.points:
                        if self.board.points[n].base_color == opponent_hex:
                            opponent_island_proximity += 1

                # Kamenčići blizu protivničkih ostrva su vredni
                # jer blokiraju njihove veze
                blocking_score += opponent_island_proximity * 3

        return blocking_score

    def strategy_evaluation(self, state, player_color):
        score = 0.0
        player_hex = self.board.player_colors[player_color]

        perimeter_islands = self.board.compute_perimeter_island_order()
        my_islands = []

        for island in perimeter_islands:
            sample = next(iter(island))
            if self.board.points[sample].base_color == player_hex:
                my_islands.append(island)

        if len(my_islands) < 2:
            return 0.0

        # Za svaki naš kamenčić
        for coord, color in state.items():
            if color == player_color:
                # Brojimo sa koliko naših ostrva je ovaj kamenčić blizu/povezan
                islands_nearby = 0

                for island in my_islands:
                    # Proveravamo da li je kamenčić blizu ovog ostrva
                    for island_coord in island:
                        if island_coord in self.board.neighbors(coord):
                            islands_nearby += 1
                            break

                    # Takođe, proveravamo da li postoji put do ostrva
                    if self.board.path_exists_between_islands(
                            {coord}, island, player_color
                    ):
                        islands_nearby += 0.5

                # Što više ostrva pokriva ovaj kamenčić, to je vredniji
                # (višenamenska polja)
                if islands_nearby >= 2:
                    score += islands_nearby * 8

        return score

    def get_computer_move(board, player_color, difficulty = "medium"):
        computer = AtollAlfaBeta(board, player_color, difficulty)
        return computer.find_best_move()
