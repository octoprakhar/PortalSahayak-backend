from disease.repository.DiseaseRepositoryAbstract import DiseaseRepositoryAbstract
from disease.models.DiseaseDefinition import DiseaseDefinition


class CombinedDiseaseRepository(DiseaseRepositoryAbstract):

    def __init__(self, repositories: list[DiseaseRepositoryAbstract]):
        self.repositories = repositories

    def get_by_name(self, name: str) -> DiseaseDefinition | None:
        for repo in self.repositories:
            disease = repo.get_by_name(name)
            if disease is not None:
                return disease
        return None

    def get_by_code(self, code: str) -> DiseaseDefinition | None:
        for repo in self.repositories:
            disease = repo.get_by_code(code)
            if disease is not None:
                return disease
        return None