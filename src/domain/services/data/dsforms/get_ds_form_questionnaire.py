
from src.domain.services.data.fhir.get_fhir_resources import GetFHIRResources


class GetDsFormQuestionnaire(GetFHIRResources):

    def __init__(
            self,
            base_url: str
    ):
        super().__init__("Get DS Form Questionnaire", base_url, 'Questionnaire')
