class DiseaseCountManager:
    """
    This class will handle each disease counts of managed diseases both max and current ones
    """

    def __init__(self, max_counts: dict[str,int]):
        self.max_counts = max_counts

        self.current_counts = {
            disease: 0
            for disease in max_counts
        }

    def get_current_counts(self):
        return self.current_counts

    def get_max_counts(self):
        return self.max_counts

    def increment(self, disease_name):
        self.current_counts[disease_name] += 1