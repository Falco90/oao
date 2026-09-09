from langgraph.graph import StateGraph, START, END

from oao.state import AgentState
from oao.nodes.wallet import analyze_wallet
from oao.nodes.opportunities import discover_opportunities
from oao.nodes.filtering import filter_opportunities

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("analyze_wallet", analyze_wallet)
    graph.add_node("discover_opportunities", discover_opportunities)
    graph.add_node("filter_opportunities", filter_opportunities)

    graph.add_edge(START, "analyze_wallet")
    graph.add_edge("analyze_wallet", "discover_opportunities")
    graph.add_edge("discover_opportunities", "filter_opportunities")
    graph.add_edge("filter_opportunities", END)
    
    return graph.compile()