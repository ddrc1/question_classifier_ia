from langgraph.types import Send

from graph.schemas import GraphStateSchema

def process_split(state: GraphStateSchema):    
    return [
        Send(
            "classificator_graph", 
            {
                "question": question
            }) 
        for question in state["questions"]
    ]