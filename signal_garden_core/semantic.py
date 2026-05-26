from datetime import date


def normalize_concept_record(value):

    if isinstance(value, dict):

        sightings = value.get("sightings", [])

        if not isinstance(sightings, list):

            sightings = []

        sightings = [
            s for s in sightings
            if isinstance(s, str)
        ][-30:]

        score = value.get(
            "score",
            value.get(
                "seen_count",
                value.get("count", 0)
            )
        )

        try:

            score = float(score)

        except (TypeError, ValueError):

            score = 0.0

        try:

            seen_count = int(
                value.get(
                    "seen_count",
                    value.get("count", 0)
                )
            )

        except (TypeError, ValueError):

            seen_count = 0

        return {
            "score": score,
            "seen_count": seen_count,
            "last_seen": value.get("last_seen"),
            "sightings": sightings
        }

    try:

        seen_count = int(value)

    except (TypeError, ValueError):

        seen_count = 0

    return {
        "score": float(seen_count),
        "seen_count": seen_count,
        "last_seen": None,
        "sightings": []
    }


def normalize_relationship_record(value):

    if isinstance(value, dict):

        sightings = value.get("sightings", [])

        if not isinstance(sightings, list):

            sightings = []

        sightings = [
            s for s in sightings
            if isinstance(s, str)
        ][-30:]

        try:

            weight = int(value.get("weight", 0))

        except (TypeError, ValueError):

            weight = 0

        return {
            "weight": weight,
            "last_seen": value.get("last_seen"),
            "sightings": sightings
        }

    return {
        "weight": 0,
        "last_seen": None,
        "sightings": []
    }


def recency_score_from_sightings(sightings, half_life_days=14):

    if not sightings:

        return 0.0

    today = date.today()
    score = 0.0

    for seen_at in sightings:

        try:

            seen_day = date.fromisoformat(seen_at[:10])

        except ValueError:

            continue

        days_old = max(
            (today - seen_day).days,
            0
        )

        score += 0.5 ** (
            days_old / half_life_days
        )

    return round(score, 4)


def concept_momentum(record):

    if record.get("sightings"):

        return recency_score_from_sightings(
            record["sightings"]
        )

    return float(record.get("score", 0.0))


def count_recent_sightings(record, window_days=7):

    if not record.get("sightings"):

        return 0

    today = date.today()
    count = 0

    for seen_at in record["sightings"]:

        try:

            seen_day = date.fromisoformat(seen_at[:10])

        except ValueError:

            continue

        if (today - seen_day).days <= window_days:

            count += 1

    return count


def concept_velocity(record, window_days=7):

    return count_recent_sightings(
        record,
        window_days=window_days
    )


def relationship_velocity(record, window_days=7):

    return count_recent_sightings(
        record,
        window_days=window_days
    )


def signal_window_delta(sightings, recent_window=7, comparison_window=7):

    if not sightings:

        return {
            "recent": 0,
            "previous": 0,
            "delta": 0
        }

    today = date.today()
    recent = 0
    previous = 0

    for seen_at in sightings:

        try:

            seen_day = date.fromisoformat(seen_at[:10])

        except ValueError:

            continue

        days_old = max(
            (today - seen_day).days,
            0
        )

        if days_old <= recent_window:

            recent += 1
        elif days_old <= recent_window + comparison_window:

            previous += 1

    return {
        "recent": recent,
        "previous": previous,
        "delta": recent - previous
    }


def concept_trend_delta(record, recent_window=7, comparison_window=7):

    return signal_window_delta(
        record.get("sightings", []),
        recent_window=recent_window,
        comparison_window=comparison_window
    )
