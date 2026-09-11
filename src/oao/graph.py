from langgraph.graph import StateGraph, START, END

from oao.nodes.recommendation import recommend
from oao.state import AgentState
from oao.nodes.wallet import analyze_wallet
from oao.nodes.opportunities import discover_opportunities
from oao.nodes.protocols import discover_protocol_candidates
from oao.nodes.optimizer import optimize_eligible_markets

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("analyze_wallet", analyze_wallet)
    graph.add_node("discover_protocol_candidates", discover_protocol_candidates)
    graph.add_node("discover_opportunities", discover_opportunities)
    graph.add_node("optimize_eligible_markets", optimize_eligible_markets)
    graph.add_node("recommend", recommend)

    graph.add_edge(START, "analyze_wallet")
    graph.add_edge("analyze_wallet", "discover_protocol_candidates")
    graph.add_edge("discover_protocol_candidates", "discover_opportunities")
    graph.add_edge("discover_opportunities", "optimize_eligible_markets")
    graph.add_edge("optimize_eligible_markets", "recommend")
    graph.add_edge("recommend", END)
    
    return graph.compile()

graph = build_graph()