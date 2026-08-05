class DiseaseQuotaConfig:

    """
    It will tell the total number of children max to be assigned for each diseases.
    """
    QUOTAS = {
        "SAM/Severe Thinness/SUW": 0,
        "Referactive Problems": 0,
        "Mild Anaemia": 0.20,
        "Moderate Anaemia": 0.25,
        "Severe Stunting": 0,
        "Skin Conditions": 0,
        "Dental Conditions": 0,
    }

    # QUOTAS = {
    #     "SAM/Severe Thinness/SUW": 0.02,
    #     "Referactive Problems": 0.1, ## Technically from the portal we don't wanna select this disease at all, only user should do it.
    #     "Mild Anaemia": 0.20,
    #     "Moderate Anaemia": 0.25,
    #     "Severe Stunting": 0.03,
    #     "Skin Conditions": 0.05,
    #     "Dental Conditions": 0.03,
    # }