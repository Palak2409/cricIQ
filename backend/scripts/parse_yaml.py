import yaml
import os

# Path to a single match file for testing
DATA_DIR = os.path.join("data", "bronze", "cricsheet")


def parse_match(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        match = yaml.safe_load(f)

    info = match["info"]
    match_id = os.path.splitext(os.path.basename(filepath))[0]

    # --- Match summary ---
    print(f"Match ID: {match_id}")
    print(f"Date: {info['dates'][0]}")
    print(f"Venue: {info.get('venue', 'Unknown')}, {info.get('city', 'Unknown')}")
    print(f"Teams: {' vs '.join(info['teams'])}")
    print(f"Toss: {info['toss']['winner']} chose to {info['toss']['decision']}")
    if "outcome" in info and "winner" in info["outcome"]:
        print(f"Winner: {info['outcome']['winner']}")
    print(f"Format: {info['match_type']}")
    print()

    # --- Parse deliveries ---
    deliveries = []
    for inning in match["innings"]:
        inning_name = list(inning.keys())[0]  # e.g. "1st innings"
        inning_data = inning[inning_name]
        team = inning_data["team"]

        for ball_entry in inning_data["deliveries"]:
            ball_key = list(ball_entry.keys())[0]
            ball_data = ball_entry[ball_key]

            # Use actual_delivery (a quoted string) instead of the dict key,
            # since the key gets parsed as an unreliable float by YAML
            actual = ball_data.get("actual_delivery")
            if actual is not None:
                over_num, ball_num = str(actual).split(".")
            else:
                # fallback if actual_delivery is missing in some files
                over_num, ball_num = str(ball_key).split(".")

            deliveries.append({
                "match_id": match_id,
                "innings_team": team,
                "over": int(over_num),
                "ball": int(ball_num),
                "batsman": ball_data.get("batsman"),
                "bowler": ball_data.get("bowler"),
                "non_striker": ball_data.get("non_striker"),
                "runs_batsman": ball_data["runs"]["batsman"],
                "runs_extras": ball_data["runs"]["extras"],
                "runs_total": ball_data["runs"]["total"],
                "is_wicket": "wicket" in ball_data,
                "wicket_kind": ball_data.get("wicket", {}).get("kind"),
                "player_out": ball_data.get("wicket", {}).get("player_out"),
            })

    print(f"Total deliveries parsed: {len(deliveries)}")
    print()
    print("First 5 deliveries:")
    for d in deliveries[:5]:
        print(d)

    return match_id, info, deliveries


if __name__ == "__main__":
    # Grab the first .yaml file in the bronze folder to test
    yaml_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".yaml")]
    if not yaml_files:
        print("No YAML files found in", DATA_DIR)
    else:
        first_file = os.path.join(DATA_DIR, yaml_files[0])
        parse_match(first_file)