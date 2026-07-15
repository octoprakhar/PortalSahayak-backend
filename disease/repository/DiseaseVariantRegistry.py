from disease.models.Variant import Variant


class DiseaseVariantRegistry:
    def __init__(self):
        variants: dict[str, list[Variant]] = {
            "Skin Conditions": [
                Variant(portal_name="Skin Conditions", max_age=6),
                Variant(portal_name="Skin Condtions Not Leprosy", max_age=19),
            ]  # Always arrange in ascending order of max_age
        }

        # concept -> list[Variant]
        self.by_concept = variants

        # portal_name -> concept
        self.by_variant = {}

        for concept, variant_list in variants.items():
            for variant in variant_list:
                self.by_variant[variant.portal_name] = concept

    def get_disease_concept(self, disease_name: str) -> str:
        """
        If the disease is a variant, return its parent concept.
        Otherwise return the original disease name.
        """
        return self.by_variant.get(disease_name, disease_name)

    def get_correct_variant(self, disease_name: str, curr_age: int) -> str:
        """
        Given a disease concept and patient's age, return the
        appropriate portal variant.
        """

        variants = self.by_concept.get(disease_name)

        # No variants configured
        if variants is None:
            return disease_name

        # Variants are sorted by max_age
        for variant in variants:
            if curr_age < variant.max_age:
                return variant.portal_name

        # Age exceeds all configured limits
        return variants[-1].portal_name