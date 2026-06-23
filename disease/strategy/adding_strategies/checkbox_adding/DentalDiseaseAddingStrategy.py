from disease.strategy.adding_strategies.checkbox_adding.CheckboxAdditionStrategy import CheckboxAdditionStrategy


class DentalDiseaseAdditionStrategy(CheckboxAdditionStrategy):
    def get_disease(self, repository):
        
        return repository.get_by_name("Dental Conditions")