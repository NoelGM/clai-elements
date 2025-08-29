from src.infrastructure.adapters.agents.ds_forms_agent import DsformsAgent


class AgentManager:
    def __init__(self, max_retries=2, verbose=True):
        self.agents = {
            "forms": DsformsAgent()
        }

    def get_agent(self, agent_name):
        agent = self.agents.get(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found.")
        return agent