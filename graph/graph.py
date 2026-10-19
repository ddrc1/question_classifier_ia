from langgraph.graph.state import CompiledStateGraph, StateGraph, START

from graph.schemas import GraphStateSchema, SingleQuestionGraphStateSchema
from graph.agents.pre_processing_agent.agent import agent as pre_processing_agent
from graph.agents.first_step_classificator_agent.agent import agent as first_step_classificator_agent
from graph.agents.second_step_classificator_agent.agent import agent as second_step_classificator_agent
from graph.conditionals.process_split import process_split

def classificator_graph():
    graph: StateGraph = StateGraph(SingleQuestionGraphStateSchema)
    
    graph.add_node(node="pre_processing_agent", action=pre_processing_agent)
    graph.add_node(node="first_step_classificator_agent", action=first_step_classificator_agent)
    graph.add_node(node="second_step_classificator_agent", action=second_step_classificator_agent)
    
    graph.add_edge(start_key=START, end_key="pre_processing_agent")
    
    return graph.compile()

def compile() -> CompiledStateGraph:
    graph: StateGraph = StateGraph(state_schema=GraphStateSchema)

    graph.add_node(node="classificator_graph", action=classificator_graph())
    
    graph.add_conditional_edges(source=START, path=process_split)
    
    return graph.compile()