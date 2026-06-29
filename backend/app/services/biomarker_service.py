import statistics
from collections import defaultdict


def extract_biomarkers(game_type, raw_events):
    """Extract biomarker records from raw tap/keystroke events."""
    if not raw_events:
        return []

    if game_type == "bubble_pop":
        return _extract_bubble_pop(raw_events)
    if game_type == "piano_tiles":
        return _extract_piano_tiles(raw_events)
    if game_type == "typing_race":
        return _extract_typing_race(raw_events)
    return []


def _extract_bubble_pop(events):
    results = []
    by_side = defaultdict(list)

    for ev in events:
        rt = ev.get("reaction_time_ms")
        side = ev.get("hand_side", "center")
        if rt is not None:
            by_side[side].append(rt)
            results.append(
                {
                    "reaction_time_ms": rt,
                    "hand_side": side,
                    "accuracy_pct": 100.0 if ev.get("hit", True) else 0.0,
                }
            )

    asymmetry = _calc_asymmetry(by_side, metric_key="reaction_time_ms", results=results)
    for r in results:
        r["asymmetry_ratio"] = asymmetry
        r["variance_ms"] = _side_variance(by_side.get(r["hand_side"], []))

    return results


def _extract_piano_tiles(events):
    results = []
    by_side = defaultdict(list)
    prev_ts = None

    for ev in events:
        side = ev.get("hand_side", "center")
        ft = ev.get("flight_time_ms")
        if ft is None and prev_ts is not None:
            ft = ev.get("timestamp_ms", 0) - prev_ts
        if ft is not None and ft > 0:
            by_side[side].append(ft)
            results.append(
                {
                    "flight_time_ms": ft,
                    "hand_side": side,
                    "accuracy_pct": 100.0 if ev.get("on_time", True) else 0.0,
                }
            )
        prev_ts = ev.get("timestamp_ms", prev_ts)

    asymmetry = _calc_asymmetry(by_side, metric_key="flight_time_ms", results=results)
    for r in results:
        r["asymmetry_ratio"] = asymmetry
        r["variance_ms"] = _side_variance(by_side.get(r["hand_side"], []))

    return results


def _extract_typing_race(events):
    results = []
    by_side = defaultdict(list)

    for ev in events:
        side = ev.get("hand_side", "left")
        ht = ev.get("hold_time_ms")
        ft = ev.get("flight_time_ms")

        entry = {"hand_side": side}
        if ht is not None:
            entry["hold_time_ms"] = ht
            by_side[side].append(ht)
        if ft is not None:
            entry["flight_time_ms"] = ft
        entry["accuracy_pct"] = 100.0 if ev.get("correct", True) else 0.0
        results.append(entry)

    asymmetry = _calc_asymmetry(by_side, metric_key="hold_time_ms", results=results)
    for r in results:
        r["asymmetry_ratio"] = asymmetry
        r["variance_ms"] = _side_variance(by_side.get(r["hand_side"], []))

    return results


def _calc_asymmetry(by_side, metric_key, results):
    left_vals = by_side.get("left", [])
    right_vals = by_side.get("right", [])
    if not left_vals or not right_vals:
        return 1.0
    left_mean = statistics.mean(left_vals)
    right_mean = statistics.mean(right_vals)
    if right_mean == 0:
        return 1.0
    return round(left_mean / right_mean, 4)


def _side_variance(values):
    if len(values) < 2:
        return 0.0
    return round(statistics.variance(values), 2)
