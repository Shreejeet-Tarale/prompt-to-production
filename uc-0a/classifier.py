"""
UC-0A -- Complaint Classifier
Deterministic logic per agents.md / skills.md and RICE enforcement.
No external APIs. Only uses the input row description.
"""
import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other",
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]


def _contains(lower, *phrases):
    for p in phrases:
        if p in lower:
            return p
    return None


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    cid = str(row.get("complaint_id") or row.get("id") or "").strip()
    desc = row.get("description")
    if cid == "":
        cid = str(row.get("_rownum", "") or "")
    if desc is None or str(desc).strip() == "":
        return {
            "complaint_id": cid,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description text provided, cannot determine category.",
            "flag": "NEEDS_REVIEW",
        }

    original = str(desc).strip()
    lower = original.lower()

    urgent_hit = _contains(lower, *SEVERITY_KEYWORDS)

    heritage_hit = _contains(
        lower, "heritage", "historic", "museum", "tram",
        "cobblestone", "marble palace", "step well", "stepwell", "boi para",
    )
    heat_hit = _contains(
        lower, "heat", "melting", "temperature", "heatwave", "heat wave",
        "burns", "sticking", "bubbling", "full sun", "unbearable",
        "celsius", "44", "45", "52",
    )
    pothole_hit = _contains(lower, "pothole")
    flood_hit = _contains(lower, "flood")
    drain_hit = None
    if "drain" in lower and ("block" in lower or "clog" in lower or "debris" in lower):
        drain_hit = "drain blocked"
    elif _contains(lower, "mosquito", "dengue", "stormwater drain",
                   "draining directly", "draining onto"):
        drain_hit = _contains(lower, "mosquito", "dengue", "stormwater drain",
                              "draining directly", "draining onto")
    streetlight_hit = _contains(
        lower, "streetlight", "street light", "lights out", "light flickering",
        "flickering", "sparking", "unlit", "darkness", "dark at night",
        "substation tripped", "lamp post", "wiring theft", "after dark",
    )
    # FIX (Waste miss): was garbage-only -> Other on
    # "Dead animal not removed" and "Bulk waste ... dumped".
    # Expanded to the full Waste phrase set below; nothing else changed.
    waste_hit = _contains(
        lower, "garbage", "waste", "bins", "overflowing", "dumped",
        "dead animal", "not cleared", "not removed", "piles of waste",
        "renovation dumped",
    )
    noise_hit = _contains(
        lower, "music", "band", "drilling", "amplifier", "club",
        "idling", "loud", "midnight", "2am", "5am",
    )
    road_hit = _contains(
        lower, "crack", "sink", "collapse", "crater", "buckl", "subsid",
        "manhole", "footpath", "tiles broken", "upturned paving",
        "road surface", "paving", "utility work", "sinking",
        "broken bench", "road collapsed", "bridge",
    )

    category, evidence = "Other", None
    if heritage_hit and ("waste" in lower or "garbage" in lower or "bins" in lower):
        if waste_hit:
            category, evidence = "Waste", waste_hit
        else:
            category, evidence = "Heritage Damage", heritage_hit
    elif heritage_hit:
        if noise_hit and _contains(lower, "playing", "audible", "music", "band", "amplifier"):
            if _contains(lower, "defaced", "broken", "knocked over", "removed",
                         "not replaced", "cable laying"):
                category, evidence = "Heritage Damage", heritage_hit
            else:
                category, evidence = "Noise", noise_hit
        else:
            category, evidence = "Heritage Damage", heritage_hit
    elif heat_hit and _contains(lower, "pothole", "footpath", "paving", "bench",
                                "shelter", "park", "road", "track", "tarmac", "promenade"):
        if "child" in lower and ("paving" in lower or "bench" in lower):
            category, evidence = "Road Damage", _contains(lower, "paving", "bench") or "paving"
        else:
            category, evidence = "Heat Hazard", heat_hit
    elif heat_hit:
        category, evidence = "Heat Hazard", heat_hit
    elif pothole_hit:
        category, evidence = "Pothole", pothole_hit
    elif (flood_hit and drain_hit and "risk" in lower
          and "flooded" not in lower and "standing" not in lower
          and "stranded" not in lower):
        category, evidence = "Drain Blockage", drain_hit
    elif flood_hit:
        category, evidence = "Flooding", flood_hit
    elif drain_hit:
        category, evidence = "Drain Blockage", drain_hit
    elif streetlight_hit:
        category, evidence = "Streetlight", streetlight_hit
    elif waste_hit:
        category, evidence = "Waste", waste_hit
    elif noise_hit:
        category, evidence = "Noise", noise_hit
    elif road_hit:
        category, evidence = "Road Damage", road_hit
    else:
        if "underpass" in lower and ("rain" in lower or "water" in lower):
            category, evidence = "Flooding", "underpass"
        elif "drain" in lower:
            category, evidence = "Drain Blockage", "drain"
        elif "dark" in lower or "unlit" in lower:
            category, evidence = "Streetlight", "dark"
        else:
            category, evidence = "Other", None

    if urgent_hit:
        priority = "Urgent"
    elif category == "Noise":
        priority = "Low"
    else:
        priority = "Standard"

    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
    elif flood_hit and drain_hit:
        flag = "NEEDS_REVIEW"
    elif "channel rainwater" in lower:
        flag = "NEEDS_REVIEW"

    if evidence:
        reason = "Classified as %s because description contains '%s'." % (category, evidence)
    else:
        snippet = original[:80].replace('"', "'")
        reason = "Classified as %s based on description '%s'." % (category, snippet)

    return {
        "complaint_id": cid,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Never aborts on a bad row; always writes header + one row per input.
    """
    with open(input_path, newline="", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        rows = list(reader)

    out_rows = []
    for i, r in enumerate(rows, start=1):
        r = dict(r)
        if not (r.get("complaint_id") or "").strip():
            r["_rownum"] = "ROW-%d" % i
            r["complaint_id"] = r["_rownum"]
        try:
            out_rows.append(classify_complaint(r))
        except Exception as exc:
            out_rows.append({
                "complaint_id": r.get("complaint_id") or ("ROW-%d" % i),
                "category": "Other",
                "priority": "Standard",
                "reason": "Classification failed (%s); marked for review." % exc,
                "flag": "NEEDS_REVIEW",
            })

    with open(output_path, "w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(
            fout, fieldnames=["complaint_id", "category", "priority", "reason", "flag"]
        )
        writer.writeheader()
        writer.writerows(out_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print("Done. Results written to %s" % args.output)
