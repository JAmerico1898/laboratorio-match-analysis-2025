# Copied from JAmerico1898/plataforma-scouting @ c027daa: pipelines/opta/processing/opta/conventions.py
# Unchanged except imports (opta. -> opta_ref.). Do not edit here; re-copy from the reference.
"""Convenções Opta F24 / WhoScored: fonte única de tipos e qualificadores (spec §2, §5.1; B3.2)."""

# --- tipos de evento ---
PASS = 1
OFFSIDE_PASS = 2
TAKE_ON = 3
FOUL = 4
CORNER_AWARDED = 6
TACKLE = 7
CLAIM = 11
GOAL = 16
AERIAL = 44
OFFSIDE_PROVOKED = 55
OFFSIDE_GIVEN = 10000  # sintético do WhoScored: sem `second`; às vezes repete o `id` (ajuste A1)
PROG_CARRY_TYPE = 1000
CARRY_TYPE = 2000

SHOT_TYPES = (13, 14, 15, 16)
ADMIN_TYPES = (17, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28, 30, 32, 34, 35, 36, 37,
               38, 39, 40, 43, 47, 63, 64, 65, OFFSIDE_GIVEN)
REMOVED_AFTER_SHOT = (10, 58, 53)
PLAY_PERIODS = (1, 2, 3, 4)  # 14 = pós-jogo, 16 = pré-jogo, 5 = disputa de pênaltis (ajuste A3)

# --- contador `stop` das cadeias (spec §5.1) ---
OWN_BAD_IF_OUTCOME0 = (PASS, TAKE_ON, 61)
OWN_BAD_ALWAYS = (50,)
OPP_GOOD_IF_OUTCOME1 = (PASS, TAKE_ON, AERIAL, TACKLE)
DEFENSIVE_IF_NEXT_SAME = (8, 12, 49, 45, 74, 41, 59)  # mais TACKLE com outcome 0
KEEPER_HANDS = (52, 54)  # mais CLAIM com outcome 1 (D14)
OFFSIDE_TYPES = (OFFSIDE_PASS, OFFSIDE_PROVOKED)
FOUL_COMMITTED_OUTCOME = 0  # WhoScored: 1 = sofreu, 0 = cometeu (inverso da F24)
RESTART_PASS_QUALIFIERS = (107, 124, 5, 6)
XT_SET_PIECE_QUALIFIERS = (6, 107, 124)  # escanteio, lateral, tiro de meta: fora do xT de passe; falta (5) fica

# --- conduções sintéticas, em unidades Opta (A3.1) ---
CARRY_MIN_GAIN = 5.0
CARRY_PROG_X = 50.0
CARRY_MAX_GAP_S = 30.0  # pausa maior sem evento rompe a condução (auditoria A8)
CARRY_BREAKING_TYPES = (7, 8, 12, 44, 45, 49, 74)  # disputa/ação defensiva no fim: não houve bola controlada (A8)

# --- qualificadores ---
Q_PENALTY = 9
Q_OWN_GOAL = 28
Q_RELATED_EVENT = 55
Q_SHOT_ASSIST = 210
RED_CARD_QUALIFIERS = (32, 33)  # segundo amarelo, vermelho direto (evento 17)
XG_FLAG_QUALIFIERS = {
    "head": (15,), "left_foot": (72,), "right_foot": (20,), "big_chance": (214,),
    "set_piece": (24, 25, 26), "fast_break": (23,), "assisted": (29,),
}  # q89, q108 e q328 fora: ausentes em 24 das 37 temporadas de treino (auditoria A13, G9)
XA_FLAG_QUALIFIERS = {"cross": (2,), "through_ball": (4,), "set_piece": (5, 6, 107), "head_pass": (3,)}

# União dos qualificadores citados na metodologia, na spec e no legado (colunas bool q<N>).
QUALIFIERS_USED = (1, 2, 3, 4, 5, 6, 9, 13, 14, 15, 16, 20, 22, 23, 24, 25, 26, 28, 29, 32, 33,
                   72, 82, 89, 107, 108, 123, 124, 155, 156, 160, 168, 196, 210, 214, 218, 328)
QUALIFIERS_NUMERIC = (55, 140, 141, 212, 213)

# --- posição → função (spec §5.3, D13) ---
POSITION_TO_FUNCAO = {
    "GK": "Goleiro",
    "DC": "Zagueiro",
    "DR": "Lateral", "DL": "Lateral",
    "DMC": "Meio Campo", "DMR": "Meio Campo", "DML": "Meio Campo",
    "MC": "Meio Campo", "MR": "Meio Campo", "ML": "Meio Campo", "AMC": "Meio Campo",
    "AMR": "Extremo", "AML": "Extremo", "FWR": "Extremo", "FWL": "Extremo",
    "FW": "Atacante",
}
OUTRA_FUNCAO = "Outra Função"


def funcao_of(code: str | None) -> str:
    return POSITION_TO_FUNCAO.get(code, OUTRA_FUNCAO)
