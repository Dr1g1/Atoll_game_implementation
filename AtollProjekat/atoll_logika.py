# atoll_logika.py
from collections import deque
import math

class AtollLogic:
    def __init__(self, board):
        self.board = board

    # treba da vraca sve susedne sestouhlove koji postoje na tabli za dat sestougao
    def ret_neighbors(self, coord):
        q, r = coord # heks koordinate u aksijalnom sistemu
        #ovo dole su 6 smerova u aksijalnoj mrezi:
        dirs = [(+1, 0), (-1, 0), (0, +1), (0, -1), (+1, -1), (-1, +1)]
        result = [] # lista gde se cuvaju validni susedi
        # za svaki smer ide nova koordinata suseda; dq i dr su kao pomeraji
        for dq, dr in dirs:
            n = (q + dq, r + dr)
            if n in self.board.points:
                result.append(n)
        return result

    # nalazi ostrva i vraca ih grupisane po boji:
    def ret_islands(self):
        edge_cells = {coord: p for coord, p in self.board.points.items() if p.base_color != "#ffffff"}
        visited = set()
        islands_bycolor = {}

        for coord, p in edge_cells.items():
            if coord in visited:
                continue
            color = p.base_color
            stack = [coord]
            comp = set()
            while stack:
                c = stack.pop()
                if c in visited:
                    continue
                visited.add(c)
                comp.add(c)
                for n in self.ret_neighbors(c):
                    if n in edge_cells and edge_cells[n].base_color == color and n not in visited:
                        stack.append(n)
            islands_bycolor.setdefault(color, []).append(comp)
        return islands_bycolor

    # vraca ostrva redom po okviru kako idu
    def ret_islands_order_by_perimeter(self):
        cx, cy = self.board.cx, self.board.cy # centar mape
        edge = [] # zauzete tacke sa njihovim uglom
        for coord, p in self.board.points.items():
            if p.base_color != "#ffffff":
                angle = math.atan2(p.y - cy, p.x - cx)
                edge.append((angle, coord, p.base_color))
        if not edge:
            return []

        edge.sort(key=lambda t: t[0])
        sequence = [(coord, color) for (_, coord, color) in edge]

        groups = []
        current_color = None
        current_set = set() # boja i koordinate trenutnog ostrva
        for coord, color in sequence:
            if color == '#000000':
                if current_set:
                    groups.append((current_color, current_set))
                    current_color = None
                    current_set = set()
                continue
            if current_color is None:
                current_color = color
                current_set = {coord}
            elif color == current_color:
                current_set.add(coord)
            else:
                groups.append((current_color, current_set))
                current_color = color
                current_set = {coord}
        if current_set:
            groups.append((current_color, current_set))

        if len(groups) >= 2 and groups[0][0] == groups[-1][0]:
            merged_color = groups[0][0]
            merged_set = groups[-1][1] | groups[0][1]
            groups = [(merged_color, merged_set)] + groups[1:-1]

        islands_in_order = [comp for (color, comp) in groups if color != '#000000']
        return islands_in_order

    # treba da proveri da li se 2 ostrva dodiruju preko bar jednog susednog polja:
    # ako bar jedno bolje iz jednog ostrva ima suseda koji je u drugom onda su susedi
    def is_adj_islands(self, island1, island2):
        for i1_cor in island1:
            for i2_cor in self.ret_neighbors(i1_cor): # i2_cor - svi susedi za i1_cor
                if i2_cor in island2:
                    return True
        return False

    # ova fja proverava da li postoji povezan put izmedju dva ostrva za jednog igraca
    def path_between_islands(self, island1, island2, player_color):
        player_hex = self.board.player_colors[player_color] # boja igraca u heks formatu
        player_coords = {coord for coord, p in self.board.stones.items() if p == player_color}
        dst_island = set(island2) # ostrvo do kog se ide

        q = deque()
        visited = set()

        for s in island1:
            if (s in player_coords) or (self.board.points[s].base_color == player_hex):
                q.append(s)
                visited.add(s)

        if not q:
            for c in player_coords:
                if any(nb in island1 for nb in self.ret_neighbors(c)):
                    q.append(c)
                    visited.add(c)

        while q:
            cur = q.popleft()
            if cur in dst_island:
                return True
            for n in self.ret_neighbors(cur):
                if n in visited:
                    continue
                if (n in player_coords) or (self.board.points[n].base_color == player_hex):
                    visited.add(n)
                    q.append(n)
        return False

    # najmanji broj kamencica da bi se povezals dva ostrva
    # koristi se 0-1 BFS
    def ret_shortest_path(self, island_a, island_b, player_color_name):
        player_hex = self.board.player_colors[player_color_name]
        player_coords = {coord for coord, p in self.board.stones.items() if p == player_color_name}
        target = set(island_b)

        INF = 10**9 # kao beskonacno
        dist = {coord: INF for coord in self.board.points.keys()}
        dq = deque()

        for s in island_a:
            if (s in player_coords) or (self.board.points[s].base_color == player_hex):
                cost = 1 if s in player_coords else 0
                if cost < dist[s]:
                    dist[s] = cost
                    if cost == 0:
                        dq.appendleft(s)
                    else:
                        dq.append(s)

        if all(dist[s] == INF for s in island_a):
            for c in player_coords:
                if any(nb in island_a for nb in self.ret_neighbors(c)):
                    if 1 < dist[c]:
                        dist[c] = 1
                        dq.append(c)

        while dq:
            cur = dq.popleft()
            if cur in target:
                return dist[cur]
            for n in self.ret_neighbors(cur):
                if (n in player_coords) or (self.board.points[n].base_color == player_hex):
                    add_cost = 1 if n in player_coords else 0
                    nd = dist[cur] + add_cost
                    if nd < dist[n]:
                        dist[n] = nd
                        if add_cost == 0:
                            dq.appendleft(n)
                        else:
                            dq.append(n)
        return None

    # fja koja trazi pobednicku putanju ili najblizi put do pobede konkretnog igraca:
    def find_winner_path(self, player_color_name):
        perimeter_islands = self.ret_islands_order_by_perimeter()
        total_islands = len(perimeter_islands)
        if total_islands == 0:
            return False, []

        threshold = (total_islands // 2) + 1 # ovo je prag - ako je tabla gde je stranica 5 onda je ovo 7
        player_hex = self.board.player_colors[player_color_name]

        same_color_indices = []
        for idx, comp in enumerate(perimeter_islands):
            sample_coord = next(iter(comp))
            if self.board.points[sample_coord].base_color == player_hex:
                same_color_indices.append((idx, comp))

        found_pairs = []
        n = total_islands
        for a in range(len(same_color_indices)):
            for b in range(a + 1, len(same_color_indices)):
                ia, A = same_color_indices[a]
                ib, B = same_color_indices[b]

                forward = (ib - ia) % n + 1
                other = n - ((ib - ia) % n) + 1
                min_arc = min(forward, other)
                if min_arc <= 1:
                    continue

                if self.path_between_islands(A, B, player_color_name):
                    stones = self.ret_shortest_path(A, B, player_color_name)
                    found_pairs.append((A, B, stones, min_arc))
                    if min_arc >= threshold:
                        return True, (A, B, stones, min_arc, threshold)

        return False, found_pairs

    # na osnovu zadatog stanja igre i igraca na potezu formira
    # sve moguce poteze:
    def form_all_possible_moves(self, state_stones=None):
        used = state_stones if state_stones is not None else self.board.stones
        possible = []
        for coord, point in self.board.points.items():
            if point.base_color == "#ffffff" and coord not in used:
                possible.append(coord)
        return possible

    # na osnovu zadatog igraca na potezu, zadatog poteza i
    #zadatog stanja igre formira novo stanje:
    def form_new_state(self, state_stones, coord, player_color_name):
        if coord not in self.board.points:
            return None
        if coord in state_stones:
            return None
        if self.board.points[coord].base_color != "#ffffff":
            return None
        new_state = dict(state_stones)
        new_state[coord] = player_color_name
        return new_state

    def ret_all_next_states(self, state_stones, player_color_name):
        next_states = []
        possible_moves = self.form_all_possible_moves(state_stones)
        for move in possible_moves:
            new_state = self.form_new_state(state_stones, move, player_color_name)
            if new_state is not None:
                next_states.append((move, new_state))
        return next_states
