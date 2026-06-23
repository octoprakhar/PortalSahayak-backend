class DiseaseCountManager:
    """
    This class will handle each disease counts of managed diseases both max and current ones
    """

    def __init__(self):
        self.current_counts = {
            "SAM/Severe Thinness/SUW": 0,
            "Mild Anaemia": 0,
            "Moderate Anaemia": 0,
            "Severe Stunting": 0,
            "Skin Conditions": 0,
            "Dental Conditions": 0
        }

        self.max_counts = {
            "SAM/Severe Thinness/SUW": 0,
            "Mild Anaemia": 0,
            "Moderate Anaemia": 0,
            "Severe Stunting": 0,
            "Skin Conditions": 0,
            "Dental Conditions": 0
        }

    def get_current_counts(self):
        return self.current_counts

    def get_max_counts(self):
        return self.max_counts

    def increment(self, disease_name):
        self.current_counts[disease_name] += 1