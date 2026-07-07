import json

from disease.models.DiseaseDefinition import DiseaseDefinition
from disease.models.DiseaseCategory import DiseaseCategory
from disease.models.DiseaseDefinition import DiseaseQuestion

from disease.repository.DiseaseRepositoryAbstract import DiseaseRepositoryAbstract


class AdolscentBoysDiseaseRepository(DiseaseRepositoryAbstract):
    """
    The disease repo for child of adolscent age and boy
    """
    def __init__(self):
        
        with open(
            "disease/data/adolscent_boys_diseases.json",
            encoding="utf-8"
        ) as f:

            raw = json.load(f)

        self.all_diseases = [
            DiseaseDefinition(
                name=d["name"],
                code=d["code"],
                category=DiseaseCategory[d["category"]],
                questions=[
                    DiseaseQuestion(
                        code=q["code"],
                        text=q["text"]
                    )
                    for q in d["questions"]
                ]
            )
            for d in raw
        ]

        self.by_name = {
            disease.name.lower(): disease
            for disease in self.all_diseases
        }

        self.by_code = {
            disease.code.lower(): disease
            for disease in self.all_diseases
        }


    
    
    def get_by_name(self,name:str)-> DiseaseDefinition:
        """
        Pass the name of the disease to get all the diseases
        """
        return self.by_name.get(name.lower())
    
    def get_by_code(self,code:str):
        return self.by_code.get(code.lower())