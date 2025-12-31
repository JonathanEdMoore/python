# ncsrcp.py
import csv
import math
from collections import defaultdict, Counter
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

# -----------------------
# Base point tables for all competitions
# -----------------------
COMPETITION_BASE_POINTS = {
    "2025-26 NBA season": {
        "champion": 1000.00, "runner_up": 594.60, "conf_runner_up": 394.18,
        "conf_semi": 248.52, "round_1": 152.35, "playin_8_9": 116.93,
        "playin_9_10": 107.81, "miss_playoffs_playin": 88.54
    },
    "2026 WNBA season": {
        "champion": 755.00, "runner_up": 448.93, "semi_finalist": 297.60,
        "quarter_finalist": 187.63, "miss_playoffs": 88.09
    },
    "2025-26 NHL season": {
        "champion": 1000.00, "runner_up": 594.60, "conf_finalist": 394.18,
        "conf_semi": 248.52, "round_1": 152.35, "miss_playoffs": 92.05
    },
    "2025-26 NFL season": {
        "champion": 976, "runner_up": 976/(2**0.75), "conf_runner_up": 976/(3.46**0.75),
        "conf_semi": 976/(6.40**0.75), "wild_card": 976/(11.37**0.75), "miss_playoffs": 976/(20.66**0.75)
    },
    "2026 MLB season": {
        "ws_winner": 1000.00, "ws_runner_up": 594.60, "lcs": 394.18,
        "lds": 248.52, "wild_card": 172.18, "miss_postseason": 102.49
    },
    "2026 FIFA World Cup": {
        "champion": 1126.00, "runner_up": 669.52, "semi_finalist": 443.84,
        "quarter_finalist": 279.84, "round_of_16": 171.54, "round_of_32": 103.65,
        "group_stage": 70.48, "playoff_finalist": 58.60, "playoff_semi": 52.61
    },
    "2025-26 UEFA Champions League": {
        "champion": 1000.00, "runner_up": 594.60, "semi_finalist": 394.18,
        "quarter_finalist": 248.52, "round_of_16": 152.35, "round_of_24": 104.29,
        "miss_knockout": 77.43
    },
    "2025-26 UEFA Women's Champions League": {
        "champion": 800.00, "runner_up": 475.68, "semi_finalist": 315.34,
        "quarter_finalist": 198.82, "round_of_12": 137.74, "miss_knockout": 84.72
    },
    "2025-26 NCAA Division I men's basketball": {
        "champion": 1400.00, "runner_up": 832.44, "semi_finalist": 551.85,
        "regional_finalist": 347.93, "regional_semi": 213.29, "second_round": 128.87,
        "first_round": 77.25, "first_four": 60.13, "miss_tournament": 46.64
    },
    "2025-26 NCAA Division I women's basketball": {
        "champion": 1400.00, "runner_up": 832.44, "semi_finalist": 551.85,
        "regional_finalist": 347.93, "regional_semi": 213.29, "second_round": 128.87,
        "first_round": 77.25, "first_four": 60.13, "miss_tournament": 46.64
    },
    "2026 NCAA Division I baseball": {
        "champion": 1400.00, "runner_up": 832.44, "semi_finalist": 551.85,
        "cws_1_2": 390.88, "cws_0_2": 309.53, "super_regional": 213.29,
        "regional_finalist": 128.87, "regional_1_2": 87.63, "regional_0_2": 68.11,
        "miss_tournament": 47.49
    }
}

# -----------------------
# Option B defaults
# -----------------------
OPTIONB_DEFAULTS = {
    "tournament": {
        "stages_ordered": ["champion", "runner_up", "semi_finalist", "quarter_finalist",
                           "round_of_16", "round_of_32", "group_stage"],
        "k": {"champion":1.0, "runner_up":2.0, "semi_finalist":4.0,
              "quarter_finalist":8.0, "round_of_16":16.0, "round_of_32":32.0, "group_stage":64.0},
        "gamma": 0.8
    },
    "league": {
        "stages_ordered": ["champion", "runner_up", "conf_runner_up", "conf_semi",
                           "round_1", "miss_playoffs"],
        "k": {"champion":1.0, "runner_up":1.8, "conf_runner_up":3.5,
              "conf_semi":6.0, "round_1":12.0, "miss_playoffs":None},
        "gamma": 0.8
    }
}

# -----------------------
# Helper functions
# -----------------------
def league_value(n_contenders, method="sqrt"):
    return math.sqrt(float(n_contenders)) if n_contenders>0 else 1.0

def round_multiplier(round_number):
    return 1.0 + 0.12*(round_number-1)

def duplicate_multiplier(prior_picks):
    return max(0.0, 1.0 - 0.25*prior_picks)

def expand_pchamp_to_outcomes(p_champ, competition_style="tournament", overrides=None):
    conf = OPTIONB_DEFAULTS[competition_style].copy()
    if overrides:
        if "gamma" in overrides: conf["gamma"] = overrides["gamma"]
        if "k" in overrides: conf["k"].update(overrides["k"])
        if "stages_ordered" in overrides: conf["stages_ordered"] = overrides["stages_ordered"]

    gamma = conf["gamma"]
    kmap = conf["k"]
    stages = conf["stages_ordered"]

    reach = {}
    for s in stages:
        if s == "champion":
            reach[s] = p_champ
        else:
            k = kmap.get(s,None)
            if (k is None) or (k <= 0):
                reach[s] = None
            else:
                reach[s] = min(1.0, k*(p_champ**gamma))

    exact = {}
    cumulative = 0.0
    for s in stages:
        r = reach[s]
        if r is None:
            exact[s] = None
            continue
        e = max(0.0, r - cumulative)
        exact[s] = e
        cumulative += e

    total_assigned = sum(v for v in exact.values() if v is not None)
    remainder = max(0.0,1.0-total_assigned)
    last = stages[-1]
    exact[last] = (exact[last] or 0.0) + remainder

    for s in stages:
        if exact.get(s) is None:
            exact[s] = 0.0
    return exact

# -----------------------
# Draft Tracker Class
# -----------------------
class DraftTracker:
    def __init__(self, teams, my_player_id, competition_contenders):
        self.teams = teams
        self.my_player_id = my_player_id
        self.comp_contenders = competition_contenders

        self.taken = set()
        self.rounds = {}
        self.picks_count = Counter()
        self.mine = defaultdict(set)

    def register_pick(self, team_id, by_me=False, round_number=None):
        self.taken.add(team_id)
        self.rounds[team_id] = round_number
        self.picks_count[team_id] += 1
        if by_me:
            comp = self.teams[team_id]["competition"]
            self.mine[comp].add(team_id)

    def available_teams(self, competition=None):
        if competition:
            return [tid for tid,meta in self.teams.items()
                    if tid not in self.taken and meta["competition"]==competition]
        else:
            return [tid for tid in self.teams if tid not in self.taken]

    def p_avail(self, team_id):
        # unconditional probability relative to all teams in the competition
        comp = self.teams[team_id]["competition"]
        total = sum(self.teams[tid]["p_champ"] for tid in self.teams if self.teams[tid]["competition"]==comp)
        return self.teams[team_id]["p_champ"]/total if total>0 else 0.0

    def p_mine(self, team_id):
        comp = self.teams[team_id]["competition"]
        existing = self.mine[comp]
        p_this = self.p_avail(team_id)
        if not existing:
            return p_this
        deduction = sum(self.p_avail(tid) for tid in existing if tid != team_id)
        return max(0.0, p_this * (1 - deduction))

    def expected_points(self, team_id, round_number):
        p_mine = self.p_mine(team_id)
        E_base = 0.0
        comp = self.teams[team_id]["competition"]

        if "World Cup" in comp or "Champions" in comp or "NCAA" in comp:
            style = "tournament"
        else:
            style = "league"

        stage_probs = expand_pchamp_to_outcomes(self.p_avail(team_id), competition_style=style)
        base_map = COMPETITION_BASE_POINTS.get(comp)
        if base_map is None:
            raise KeyError(f"No base points for competition '{comp}'")
        for stage, prob in stage_probs.items():
            base = base_map.get(stage,0.0)
            E_base += prob*base

        L = league_value(self.comp_contenders.get(comp,len(stage_probs)))
        R = round_multiplier(round_number)
        D = duplicate_multiplier(self.picks_count[team_id])
        return E_base * p_mine * L * R * D

    def recommend_greedy(self, round_number, top_n=10):
        avail = self.available_teams()
        recs = []
        for tid in avail:
            val = self.expected_points(tid, round_number)
            recs.append({"team_id":tid, "team_name":self.teams[tid]["name"],
                         "competition":self.teams[tid]["competition"],
                         "expected_points":val})
        recs.sort(key=lambda x: x["expected_points"], reverse=True)
        return recs[:top_n]

# -----------------------
# CSV Loader
# -----------------------
def load_teams_from_csv(csv_file):
    teams = {}
    with open(csv_file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            team_id = row['team'].replace(" ", "_")
            if "women" in row['competition'].lower() or "wnba" in row['competition'].lower():
                team_id += "_w"
            if "baseball" in row['competition'].lower() and "ncaa" in row['competition'].lower():
                team_id += "_bb"

            teams[team_id] = {
                "name": row['team'],
                "competition": row['competition'],
                "p_champ": float(row['champ_prob'])
            }
    return teams

def name_to_id(teams, name):
    tid = name.replace(" ", "_")
    for t_id, meta in teams.items():
        if meta['name'].lower() == name.lower():
            return t_id
    raise ValueError(f"Team '{name}' not found in CSV")

# -----------------------
# Live Draft Assistant
# -----------------------
def live_draft_assistant(teams_csv, my_player_id, comp_contenders):
    teams = load_teams_from_csv(teams_csv)
    tracker = DraftTracker(teams, my_player_id, comp_contenders)

    team_completer = WordCompleter([t["name"] for t in teams.values()], ignore_case=True)
    current_round = 1

    print("Live Draft Assistant Started!")
    print("Commands: 'next' = show top picks, 'pick' = register pick, 'round' = advance round, 'exit' = quit\n")

    while True:
        cmd = input("Command (next/pick/round/exit): ").strip().lower()
        if cmd == "exit":
            break
        elif cmd == "next":
            recs = tracker.recommend_greedy(round_number=current_round, top_n=5)
            print(f"\nTop recommendations for round {current_round}:")
            for r in recs:
                print(f"{r['team_name']} ({r['competition']})")
            print("")
        elif cmd == "pick":
            team_name = prompt("Enter picked team name: ", completer=team_completer).strip()
            by_me = input("Was this you? (y/n): ").strip().lower() == "y"
            try:
                team_id = name_to_id(teams, team_name)
                tracker.register_pick(team_id, by_me=by_me, round_number=current_round)
                print(f"Registered pick: {team_name} (by_me={by_me})\n")
            except ValueError as e:
                print(e)
        elif cmd == "round":
            current_round += 1
            print(f"Advanced to round {current_round}\n")
        else:
            print("Unknown command. Use next/pick/round/exit.\n")

# -----------------------
# Main
# -----------------------
if __name__=="__main__":
    csv_file = "teams_tagged.csv"  # your CSV file path
    my_player_id = "me"

    comp_contenders = {
        "2026 FIFA World Cup":64,
        "2025-26 NBA season":30,
        "2026 WNBA season":12,
        "2025-26 NHL season":32,
        "2025-26 NFL season":26,
        "2026 MLB season":30,
        "2025-26 UEFA Champions League":32,
        "2025-26 UEFA Women's Champions League":32,
        "2025-26 NCAA Division I men's basketball":68,
        "2025-26 NCAA Division I women's basketball":68,
        "2026 NCAA Division I baseball":64
    }

    live_draft_assistant(csv_file, my_player_id, comp_contenders)
