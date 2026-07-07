"""
This script will help generate all the diseases if we just paste the full response from this request:: "/Get_DefectAnd_DefectQue_Mapping", and then run it.
"""

import json

CATEGORY_MAP = {
    "1": "DEFECTS_AT_BIRTH",
    "2": "DEFICIENCIES",
    "3": "CHILDHOOD_DISEASES",
    "4": "DEVELOPMENTAL_DELAY",
    "5": "ADOLSCENT_HEALTH_CONCERNS"
}

with open("adolscent_girl_disease_raw.json", encoding="utf-8") as f:
    response = json.load(f)

all_diseases = []

for category in response["data"]:

    for defect in category["Defects"]:

        questions = []

        for q in defect["subQuestions"]:

            if q["checklist"]:

                questions.append(
                    {
                        "code": q["checklist"],
                        "text": q["qname"]
                    }
                )

        all_diseases.append(
            {
                "name": defect["dname"],
                "code": defect["dcode"],
                "category": CATEGORY_MAP[defect["dclasscode"]],
                "questions": questions
            }
        )

with open("disease/data/adolscent_girls_diseases.json", "w", encoding="utf-8") as f:
    json.dump(
        all_diseases,
        f,
        indent=4,
        ensure_ascii=False
    )

print(f"Generated {len(all_diseases)} diseases")