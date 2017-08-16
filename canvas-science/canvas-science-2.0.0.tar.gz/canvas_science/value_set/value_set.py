class ValueSystems(type):

    @property
    def values(cls):
        return {system.lower(): getattr(cls, system)
                for system in cls.value_systems
                if hasattr(cls, system)}


class ValueSet(object, metaclass=ValueSystems):

    value_systems = [
        'CPT',
        'CVX',
        'HCPCS',
        'ICD10CM',
        'ICD10PCS',
        'ICD9CM',
        'LOINC',
        'RXNORM',
        'SNOMEDCT',
    ]
