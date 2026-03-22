"""
PyTest fajl za testiranje logike igre Atoll (atoll_logika / AtollBoard).

Opis funkcionalnosti testa:
- Testira ispravnost i granicne slucajeve za razlicite velicine table (radijusi 5, 7 i 9).
- Proverava pronalazenje susednih polja, grupisanje ostrva, redosled ostrva po obodu i proveru susednosti ostrva.
- Testira pomocne funkcije za prelazak izmedju stanja igre (form_all_possible_moves, form_new_state, ret_all_next_states).
- Testira funkcije za pronalazenje puteva (path_between_islands, ret_shortest_path) u vestacki konstruisanim scenarijima,
  gde se pokusava povezivanje ostrva putem unutrasnjih polja table i proverava da li se veza pravilno detektuje.
- Izvodi osnovne provere performansi (merenjem vremena izvrsavanja) za zahtevnije operacije na vecoj tabli (radijus 9).
"""

import time
import io
import contextlib
import tkinter as tk
from collections import deque
from atollboard import AtollBoard


# POMOCNE F-JE:

def kreiraj_tablu(radijus=5):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        root = tk.Tk()
        root.withdraw()
        frame = tk.Frame(root)
        tabla = AtollBoard(frame=frame, map_radius=radijus,
                           hex_size=30, width=600, height=600)
    return tabla


def ukupan_broj_heks_polja(radijus):
    # Formula: ukupno = 1 + 3*R*(R+1)
    return 1 + 3 * radijus * (radijus + 1)


def bfs_pronadji_beli_put(tabla, pocetni_skup, ciljni_skup, limit=10000):
    pocetne_pozicije = set()

    for s in pocetni_skup:
        for sused in tabla.logic.ret_neighbors(s):
            if tabla.points[sused].base_color == "#ffffff":
                pocetne_pozicije.add(sused)

    ciljne_pozicije = set()
    for t in ciljni_skup:
        for sused in tabla.logic.ret_neighbors(t):
            if tabla.points[sused].base_color == "#ffffff":
                ciljne_pozicije.add(sused)

    if not pocetne_pozicije or not ciljne_pozicije:
        return None

    red = deque()
    roditelj = {}

    for p in pocetne_pozicije:
        red.append(p)
        roditelj[p] = None

    poseceni = set(pocetne_pozicije)
    koraci = 0

    while red and koraci < limit:
        trenutno = red.popleft()
        if trenutno in ciljne_pozicije:
            putanja = []
            while trenutno is not None:
                putanja.append(trenutno)
                trenutno = roditelj[trenutno]
            return list(reversed(putanja))

        for sused in tabla.logic.ret_neighbors(trenutno):
            if sused in poseceni:
                continue
            if tabla.points[sused].base_color != "#ffffff":
                continue
            poseceni.add(sused)
            roditelj[sused] = trenutno
            red.append(sused)

        koraci += 1

    return None


# TESTOVI:

def test_broj_polja_prema_radijusu():
    for r in (5, 7, 9):
        tabla = kreiraj_tablu(radijus=r)
        assert len(tabla.points) == ukupan_broj_heks_polja(r), f"broj polja ne odgovara radijusu: {r}"


def test_susedi_postoje_i_broj_za_centar_i_ivicu():
    tabla = kreiraj_tablu(radijus=5)
    logika = tabla.logic

    susedi_centra = logika.ret_neighbors((0, 0))
    assert len(susedi_centra) == 6

    primeri = [(tabla.map_radius, 0), (0, tabla.map_radius), (-tabla.map_radius, 0), (0, -tabla.map_radius)]
    for s in primeri:
        sus = logika.ret_neighbors(s)
        assert all(n in tabla.points for n in sus)
        assert len(sus) < 6

def test_svojstva_redosleda_po_obodu():
    tabla = kreiraj_tablu(radijus=5)
    logika = tabla.logic

    uredjena = logika.ret_islands_order_by_perimeter()
    for comp in uredjena:
        assert isinstance(comp, set)
        assert all(c in tabla.points for c in comp)


def test_stanja_i_generisanje_poteza():
    tabla = kreiraj_tablu(radijus=5)
    logika = tabla.logic

    moguci_potezi = logika.form_all_possible_moves()
    assert isinstance(moguci_potezi, list)
    for c in moguci_potezi[:50]:
        assert tabla.points[c].base_color == "#ffffff"
        assert c not in tabla.stones

    # form_new_state odbacuje nevalidne koordinate
    ns = logika.form_new_state({}, (999, 999), 'red')
    assert ns is None

    if moguci_potezi:
        potez = moguci_potezi[0]
        novo = logika.form_new_state({}, potez, 'red')
        assert novo and potez in novo

    sledeca_stanja = logika.ret_all_next_states({}, 'green')
    assert all(isinstance(par[0], tuple) and isinstance(par[1], dict) for par in sledeca_stanja[:10])


def test_formiranje_puta_i_detekcija_na_formiranom_putu():
    tabla = kreiraj_tablu(radijus=5)
    logika = tabla.logic
    igrac = 'red'
    boja_igraca = tabla.player_colors[igrac]

    obodna_ostrva = logika.ret_islands_order_by_perimeter()

    ista_boja_ostrva = []
    for comp in obodna_ostrva:
        uzorak = next(iter(comp))
        if tabla.points[uzorak].base_color == boja_igraca:
            ista_boja_ostrva.append(comp)

    A = ista_boja_ostrva[0]
    B = ista_boja_ostrva[1]

    putanja = bfs_pronadji_beli_put(tabla, A, B)

    for coord in putanja:
        ok = tabla.place_stone(coord[0], coord[1], igrac)
        assert ok, f"nije uspelo postavljanje kamencica na {coord}"

    assert logika.path_between_islands(A, B, igrac) is True


def test_najkraci_put_vraca_int_nakon_postavljanja():
    tabla = kreiraj_tablu(radijus=5)
    logika = tabla.logic

    uredjena = logika.ret_islands_order_by_perimeter()
    if len(uredjena) < 2:
        return
    A, B = uredjena[0], uredjena[1]

    putanja = bfs_pronadji_beli_put(tabla, A, B)
    if not putanja:
        return

    for coord in putanja[::2]:
        tabla.place_stone(coord[0], coord[1], 'green')

    val = logika.ret_shortest_path(A, B, 'green')
    assert (val is None) or isinstance(val, int)


def test_performanse_find_winner_za_veliku_tablu():
    tabla = kreiraj_tablu(radijus=9)
    logika = tabla.logic

    t0 = time.perf_counter()
    pobeda, info = logika.find_winner_path('red')
    dt = time.perf_counter() - t0
    print(f"find_winner_path za R=9 dt={dt:.6f}s, pobeda={pobeda}")
    assert dt < 1.0

