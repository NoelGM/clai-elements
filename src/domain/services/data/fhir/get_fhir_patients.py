from src.domain.services.data.fhir.get_fhir_resources import GetFHIRResources


class GetFHIRPatients(GetFHIRResources):

    def __init__(
            self,
            base_url: str
    ):
        super().__init__(base_url, "Get FHIR Patients", 'Patient')
