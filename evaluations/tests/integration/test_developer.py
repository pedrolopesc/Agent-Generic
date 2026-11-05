from langchain_openai import ChatOpenAI

from agents.developer import build_developer
from sandbox.runner import SandboxRunner


def test_real_deep_agent_compiles_without_network(tmp_path):
    model = ChatOpenAI(model="gpt-4.1", api_key="not-a-real-key")
    agent = build_developer(model, SandboxRunner(tmp_path))
    assert agent.get_graph().nodes
