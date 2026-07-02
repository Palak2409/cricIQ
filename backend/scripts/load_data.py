import traceback
import os
import sys
import yaml
from datetime import datetime



sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from database import SessionLocal
from models import Player, Match, Delivery

DATA_DIR = os.path.join("data", "bronze", "cricsheet")


def parse_and_load(filepath, session):
    with open(filepath, "r", encoding="utf-8") as f:
        match_data = yaml.safe_load(f)

    info = match_data["info"]
    match_id = os.path.splitext(os.path.basename(filepath))[0]

    # Skip if this match is already loaded
    if session.get(Match, match_id):
        return "skipped"

    # --- Players ---
    registry = info.get("registry", {}).get("people", {})
    for name, pid in registry.items():
        if not session.get(Player, pid):
            session.add(Player(player_id=pid, name=name))

    # --- Match ---
    teams = info.get("teams", [])
    outcome = info.get("outcome", {})
    winner = outcome.get("winner")  # may not exist (no result / tie)

    # PyYAML may already parse unquoted dates into datetime.date objects
    raw_date = info["dates"][0]
    if isinstance(raw_date, str):
        match_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
    else:
        match_date = raw_date  # already a date object

    match = Match(
        match_id=match_id,
        date=match_date,
        venue=info.get("venue"),
        city=info.get("city"),
        team1=teams[0] if len(teams) > 0 else None,
        team2=teams[1] if len(teams) > 1 else None,
        toss_winner=info.get("toss", {}).get("winner"),
        toss_decision=info.get("toss", {}).get("decision"),
        match_winner=winner,
        match_type=info.get("match_type"),
        player_of_match=", ".join(info.get("player_of_match", [])) or None,
    )
    session.add(match)
    session.flush()   # ensures match row exists before deliveries reference it

    # --- Deliveries ---
    for inning in match_data.get("innings", []):
        inning_name = list(inning.keys())[0]
        inning_data = inning[inning_name]
        team = inning_data.get("team")

        for ball_entry in inning_data.get("deliveries", []):
            ball_key = list(ball_entry.keys())[0]
            ball_data = ball_entry[ball_key]

            actual = ball_data.get("actual_delivery")
            key_source = str(actual) if actual is not None else str(ball_key)
            over_str, ball_str = key_source.split(".")

            wicket_raw = ball_data.get("wicket", {})
            if isinstance(wicket_raw, list):
                wicket = wicket_raw[0] if wicket_raw else {}  # take the first dismissal if multiple
            else:
                wicket = wicket_raw

            delivery = Delivery(
                match_id=match_id,
                innings_team=team,
                over_num=int(over_str),
                ball_num=int(ball_str),
                batsman=ball_data.get("batsman") or ball_data.get("batter"),
                bowler=ball_data.get("bowler"),
                non_striker=ball_data.get("non_striker"),
                runs_batsman=ball_data["runs"].get("batsman", ball_data["runs"].get("batter", 0)),
                runs_extras=ball_data["runs"]["extras"],
                runs_total=ball_data["runs"]["total"],
                is_wicket=bool(wicket),
                wicket_kind=wicket.get("kind"),
                player_out=wicket.get("player_out"),
            )
            session.add(delivery)

    return "loaded"


def main(limit=None):
    yaml_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".yaml")]
    if limit:
        yaml_files = yaml_files[:limit]
    print(f"Processing {len(yaml_files)} match files.")

    session = SessionLocal()
    loaded, skipped, failed = 0, 0, 0

    for i, filename in enumerate(yaml_files, 1):
        filepath = os.path.join(DATA_DIR, filename)
        try:
            result = parse_and_load(filepath, session)
            if result == "loaded":
                loaded += 1
            else:
                skipped += 1
            session.commit()

        except Exception as e:
            session.rollback()
            failed += 1
            print(f"FAILED: {filename} -> {e}")
            traceback.print_exc()

        if i % 50 == 0:
            print(f"Processed {i}/{len(yaml_files)}...")

    session.close()
    print()
    print(f"Done. Loaded: {loaded}, Skipped (already existed): {skipped}, Failed: {failed}")


if __name__ == "__main__":
    main(limit=None)   # process all files now