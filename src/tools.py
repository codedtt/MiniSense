from typing import Any, Dict, List


def compute_survey_metrics(
    responses: List[Dict[str, Any]],
    business_id: str = None,
    start_date: str = None,
    end_date: str = None,
) -> Dict[str, Any]:
    """Tool: Computes exact CSAT, average ratings, and theme frequencies from response records."""
    filtered = responses

    if business_id:
        filtered = [r for r in filtered if r.get("business_id") == business_id]
    if start_date:
        filtered = [r for r in filtered if r.get("date") >= start_date]
    if end_date:
        filtered = [r for r in filtered if r.get("date") <= end_date]

    if not filtered:
        return {
            "count": 0,
            "avg_rating": 0.0,
            "csat": 0.0,
            "distribution": {},
            "themes": [],
        }

    total = len(filtered)
    ratings = [r["rating"] for r in filtered]
    avg_rating = round(sum(ratings) / total, 2)

    # CSAT = % of 4 and 5 ratings
    promoters = sum(1 for r in ratings if r >= 4)
    csat_pct = round((promoters / total) * 100, 2)

    distribution = {i: ratings.count(i) for i in range(1, 6)}

    # Naive keyword theme extraction for demonstration tool capability
    theme_counts = {"wait_time": 0, "food_quality": 0, "staff": 0, "cleanliness": 0}
    for r in filtered:
        txt = r.get("free_text", "").lower()
        if "wait" in txt or "time" in txt:
            theme_counts["wait_time"] += 1
        if "food" in txt or "taste" in txt or "cold" in txt:
            theme_counts["food_quality"] += 1
        if "staff" in txt or "service" in txt or "friendly" in txt:
            theme_counts["staff"] += 1
        if "clean" in txt or "dirty" in txt:
            theme_counts["cleanliness"] += 1

    return {
        "count": total,
        "avg_rating": avg_rating,
        "csat": csat_pct,
        "distribution": distribution,
        "themes": [
            {"theme": k, "count": v, "pct": round((v / total) * 100, 1)}
            for k, v in theme_counts.items()
        ],
    }