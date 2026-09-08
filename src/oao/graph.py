from langgraph.graph import StateGraph, START, END

from oao.state import AgentState
from oao.nodes.wallet import analyze_wallet

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("analyze_wallet", analyze_wallet)

    graph.add_edge(START, "analyze_wallet")
    graph.add_edge("analyze_wallet", END)
    
    return graph.compile()