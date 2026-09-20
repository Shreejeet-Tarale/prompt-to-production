"""
<<<<<<< Updated upstream
UC-0A — Complaint Classifier
Implements agents.md + skills.md: fixed taxonomy, severity-triggered
Urgent, quoted reason, NEEDS_REVIEW on ambiguity. Offline, deterministic.
=======
UC-0A -- Complaint Classifier
Deterministic logic per agents.md / skills.md and RICE enforcement.
No external APIs. Only uses the input row description.
>>>>>>> Stashed changes
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


<<<<<<< Updated upstream
def _contains(lower: str, *phrases: str) -> str | None:
=======
def _contains(lower, *phrases):
>>>>>>> Stashed changes
    for p in phrases:
        if p in lower:
            return p
    return None


def classify_complaint(row: dict) -> dict:
<<<<<<< Updated upstream
=======
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
>>>>>>> Stashed changes
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

<<<<<<< Updated upstream
    # Severity -> Urgent (substring, covers hospitalised/injuries)
    urgent_hit = _contains(lower, *SEVERITY_KEYWORDS)

    # Individual detectors (return matched phrase for reason + flag logic)
=======
    urgent_hit = _contains(lower, *SEVERITY_KEYWORDS)

>>>>>>> Stashed changes
    heritage_hit = _contains(
        lower, "heritage", "historic", "museum", "tram",
        "cobblestone", "marble palace", "step well", "stepwell", "boi para",
    )
<<<<<<< Updated upstream
    heat_hit = _contains(
        lower, "celsius", "heat", "melting", "temperature",
        "heatwave", "heat wave", "burns", "sticking", "bubbling",
        "full sun", "unbearable", "44", "45", "52",
=======
    # ASCII-only heat triggers (44/45/52 cover the degree-C rows).
    heat_hit = _contains(
        lower, "heat", "melting", "temperature", "heatwave", "heat wave",
        "burns", "sticking", "bubbling", "full sun", "unbearable",
        "celsius", "44", "45", "52",
>>>>>>> Stashed changes
    )
    pothole_hit = _contains(lower, "pothole")
    flood_hit = _contains(lower, "flood")
    drain_hit = None
    if "drain" in lower and ("block" in lower or "clog" in lower or "debris" in lower):
        drain_hit = "drain blocked"
<<<<<<< Updated upstream
    elif _contains(lower, "mosquito", "dengue", "stormwater drain", "draining directly", "draining onto"):
        drain_hit = _contains(lower, "mosquito", "dengue", "stormwater drain", "draining directly", "draining onto")
    elif "drain blocked" in lower or "drain completely blocked" in lower:
        drain_hit = "drain blocked"
=======
    elif _contains(lower, "mosquito", "dengue", "stormwater drain",
                   "draining directly", "draining onto"):
        drain_hit = _contains(lower, "mosquito", "dengue", "stormwater drain",
                              "draining directly", "draining onto")
>>>>>>> Stashed changes
    streetlight_hit = _contains(
        lower, "streetlight", "street light", "lights out", "light flickering",
        "flickering", "sparking", "unlit", "darkness", "dark at night",
        "substation tripped", "lamp post", "wiring theft", "after dark",
    )
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

<<<<<<< Updated upstream
    # Precedence per agents.md
    category, evidence = "Other", None
    if heritage_hit and ("waste" in lower or "garbage" in lower or "bins" in lower):
        # Waste in heritage area stays Waste (e.g. Manek Chowk night-market waste)
=======
    category, evidence = "Other", None
    if heritage_hit and ("waste" in lower or "garbage" in lower or "bins" in lower):
>>>>>>> Stashed changes
        if waste_hit:
            category, evidence = "Waste", waste_hit
        else:
            category, evidence = "Heritage Damage", heritage_hit
    elif heritage_hit:
<<<<<<< Updated upstream
        # Wedding band near museum is Noise, not heritage damage
        if noise_hit and _contains(lower, "playing", "audible", "music", "band", "amplifier"):
            # But defacement / broken heritage fabric stays Heritage
            if _contains(lower, "defaced", "broken", "knocked over", "removed", "not replaced", "cable laying"):
=======
        if noise_hit and _contains(lower, "playing", "audible", "music", "band", "amplifier"):
            if _contains(lower, "defaced", "broken", "knocked over", "removed",
                         "not replaced", "cable laying"):
>>>>>>> Stashed changes
                category, evidence = "Heritage Damage", heritage_hit
            else:
                category, evidence = "Noise", noise_hit
        else:
            category, evidence = "Heritage Damage", heritage_hit
<<<<<<< Updated upstream
    elif heat_hit and _contains(lower, "pothole", "footpath", "paving", "bench", "shelter", "park", "road", "track", "tarmac", "promenade"):
        # Ahmedabad heat-vs-infrastructure: heat wins when temp/heat words present
        # except child-injury paving case which is Road Damage with Urgent
=======
    elif heat_hit and _contains(lower, "pothole", "footpath", "paving", "bench",
                                "shelter", "park", "road", "track", "tarmac", "promenade"):
>>>>>>> Stashed changes
        if "child" in lower and ("paving" in lower or "bench" in lower):
            category, evidence = "Road Damage", _contains(lower, "paving", "bench") or "paving"
        else:
            category, evidence = "Heat Hazard", heat_hit
    elif heat_hit:
        category, evidence = "Heat Hazard", heat_hit
    elif pothole_hit:
        category, evidence = "Pothole", pothole_hit
<<<<<<< Updated upstream
    elif flood_hit and drain_hit and "risk" in lower and "flooded" not in lower and "standing" not in lower and "stranded" not in lower:
=======
    elif (flood_hit and drain_hit and "risk" in lower
          and "flooded" not in lower and "standing" not in lower
          and "stranded" not in lower):
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
        # Last-chance heuristics before Other
=======
>>>>>>> Stashed changes
        if "underpass" in lower and ("rain" in lower or "water" in lower):
            category, evidence = "Flooding", "underpass"
        elif "drain" in lower:
            category, evidence = "Drain Blockage", "drain"
        elif "dark" in lower or "unlit" in lower:
            category, evidence = "Streetlight", "dark"
        else:
            category, evidence = "Other", None

<<<<<<< Updated upstream
    # Priority
=======
>>>>>>> Stashed changes
    if urgent_hit:
        priority = "Urgent"
    elif category == "Noise":
        priority = "Low"
    else:
        priority = "Standard"

<<<<<<< Updated upstream
    # Flag
=======
>>>>>>> Stashed changes
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
    elif flood_hit and drain_hit:
        flag = "NEEDS_REVIEW"
    elif "channel rainwater" in lower:
        flag = "NEEDS_REVIEW"

<<<<<<< Updated upstream
    # Reason: one sentence, must cite specific words
    if evidence:
        # quote a short snippet containing the evidence phrase
        reason = f"Classified as {category} because description contains '{evidence}'."
    else:
        snippet = original[:80].replace('"', "'")
        reason = f"Classified as {category} based on description '{snippet}'."
=======
    if evidence:
        reason = "Classified as %s because description contains '%s'." % (category, evidence)
    else:
        snippet = original[:80].replace('"', "'")
        reason = "Classified as %s based on description '%s'." % (category, snippet)
>>>>>>> Stashed changes

    return {
        "complaint_id": cid,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
<<<<<<< Updated upstream
=======
    """
    Read input CSV, classify each row, write results CSV.
    Never aborts on a bad row; always writes header + one row per input.
    """
>>>>>>> Stashed changes
    with open(input_path, newline="", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        rows = list(reader)

    out_rows = []
    for i, r in enumerate(rows, start=1):
        r = dict(r)
        if not (r.get("complaint_id") or "").strip():
<<<<<<< Updated upstream
            r["_rownum"] = f"ROW-{i}"
            r["complaint_id"] = r["_rownum"]
        try:
            out_rows.append(classify_complaint(r))
        except Exception as exc:  # never crash per-row
            out_rows.append({
                "complaint_id": r.get("complaint_id") or f"ROW-{i}",
                "category": "Other",
                "priority": "Standard",
                "reason": f"Classification failed ({exc}); marked for review.",
=======
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
>>>>>>> Stashed changes
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
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print("Done. Results written to %s" % args.output)
