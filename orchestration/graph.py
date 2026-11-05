import json

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from agents.diagnostic import diagnose
from agents.monitor import monitor
from agents.validator import validate
from orchestration.state import AgentState
from orchestration.tdd import assess_tdd


def build_graph(diagnostic_model, developer, validator_model, runner, checkpointer=None):
    def diagnostic(state):
        return {"diagnosis": diagnose(diagnostic_model, state["prompt"])}

    def develop(state):
        request = (
            f"Task: {state['prompt']}\nDiagnosis: {state['diagnosis']}\n"
            f"Previous feedback: {state.get('feedback', '')}"
        )
        runner.history.clear()
        result = developer.invoke({"messages": [("human", request)]}, {"recursion_limit": 100})
        return {
            "delivery": str(result["messages"][-1].content),
            "iteration": state.get("iteration", 0) + 1,
        }

    def verify(state):
        tdd_history = runner.tdd_history
        evidence = json.dumps(
            {
                "current_attempt": [r.model_dump() for r in runner.history],
                "tdd_history": [r.model_dump() for r in tdd_history],
            },
            ensure_ascii=False,
        )
        verdict = validate(
            validator_model, state["prompt"], state["diagnosis"], state["delivery"], evidence
        )
        tdd_ok, tdd_feedback = assess_tdd(tdd_history)
        execution_ok = bool(runner.history) and runner.history[-1].exit_code == 0
        approved = verdict.approved and execution_ok and tdd_ok
        feedback = verdict.feedback
        if not tdd_ok:
            feedback += " " + tdd_feedback
        if not execution_ok:
            feedback += " A successful execution in the current attempt is required."
        return {
            "approved": approved,
            "feedback": feedback,
            "evidence": [r.model_dump_json() for r in runner.history],
            "tdd_evidence": [r.model_dump_json() for r in tdd_history],
        }

    graph = StateGraph(AgentState)
    graph.add_node("diagnostic", diagnostic)
    graph.add_node("developer", develop)
    graph.add_node("validator", verify)
    graph.add_node("monitor", monitor)
    graph.add_edge(START, "diagnostic")
    graph.add_edge("diagnostic", "developer")
    graph.add_edge("developer", "validator")
    graph.add_edge("validator", "monitor")
    graph.add_conditional_edges(
        "monitor",
        lambda s: "end" if s["status"] != "retrying" else "retry",
        {"end": END, "retry": "developer"},
    )
    return graph.compile(checkpointer=checkpointer if checkpointer is not None else InMemorySaver())
