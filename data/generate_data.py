import json
import random
from datetime import datetime, timedelta

NUM_RECORDS = 50000

BUSINESSES = [
    ("b01", "QuickFit Gym", "s01", "Membership Value"),
    ("b02", "GreenLeaf Bistro", "s02", "Dining Experience"),
    ("b03", "AeroTravel", "s03", "Flight Satisfaction"),
]

CHANNELS = ["mobile", "web", "in_person", "kiosk"]

COMMENTS_BY_RATING = {
    1: [
        "Terrible service and long wait times.",
        "Dirty facility and unhelpful staff.",
        "Overpriced and unacceptable quality.",
    ],
    2: [
        "Wait time was far too long.",
        "Food was cold and order was wrong.",
        "App kept crashing while checking in.",
    ],
    3: [
        "Average experience, nothing special.",
        "Decent quality but pricey.",
        "Staff was polite, but wait time could improve.",
    ],
    4: [
        "Great experience! Will come back again.",
        "The food was great but the wait time was slightly long.",
        "Clean amenities and friendly service.",
    ],
    5: [
        "Outstanding service and incredible quality!",
        "Loved everything about this place!",
        "Fast, efficient, and super friendly team.",
    ],
}


def generate_dataset():
    start_date = datetime(2026, 4, 1)
    end_date = datetime(2026, 5, 31)
    delta_days = (end_date - start_date).days

    responses = []
    for i in range(1, NUM_RECORDS + 1):
        b_id, b_name, s_id, s_name = random.choice(BUSINESSES)
        random_day = start_date + timedelta(
            days=random.randint(0, delta_days),
            hours=random.randint(8, 20),
            minutes=random.randint(0, 59),
        )

        # Skew ratings towards positive slightly
        rating = random.choices([1, 2, 3, 4, 5], weights=[0.1, 0.15, 0.2, 0.35, 0.2])[0]
        free_text = random.choice(COMMENTS_BY_RATING[rating])

        responses.append(
            {
                "response_id": f"r{i:06d}",
                "date": random_day.strftime("%Y-%m-%d %H:%M:%S"),
                "business_id": b_id,
                "business_name": b_name,
                "survey_id": s_id,
                "survey_name": s_name,
                "rating": rating,
                "response_channel": random.choice(CHANNELS),
                "free_text": free_text,
            }
        )

    with open("data/survey_responses.json", "w") as f:
        json.dump({"responses": responses}, f, indent=2)

    print(f"Successfully generated {NUM_RECORDS} survey records in data/survey_responses.json")


if __name__ == "__main__":
    generate_dataset()