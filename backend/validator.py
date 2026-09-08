def validate_record(record):

    confidence = {}


    # Survey Number

    if record["survey_number"] != "Not detected":

        confidence["survey_number"] = 0.98

    else:

        confidence["survey_number"] = 0.40


    # Owner Name

    if record["owner_name"] != "Not detected":

        confidence["owner_name"] = 0.96

    else:

        confidence["owner_name"] = 0.40


    # Land Area

    if record["land_area"] != "Not detected":

        confidence["land_area"] = 0.95

    else:

        confidence["land_area"] = 0.50


    # Location

    if record["location"] != "Not detected":

        confidence["location"] = 0.94

    else:

        confidence["location"] = 0.40


    # Human review required
    # if any confidence < 80%

    human_review = any(
        score < 0.80
        for score in confidence.values()
    )


    return {

        "data": record,

        "confidence": confidence,

        "human_review_required":
            human_review

    }