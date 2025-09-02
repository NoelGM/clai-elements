from src.infrastructure.adapters.agents.ds_forms_agent import DsFormsAgent
from src.infrastructure.utils.agents import FORMS
from src.infrastructure.utils.factories.factory import Factory


class AgentFactory(Factory):

    def __init__(self):
        instances: dict = {
            FORMS: DsFormsAgent()
        }
        super().__init__(instances)

agent_factory: AgentFactory = AgentFactory()