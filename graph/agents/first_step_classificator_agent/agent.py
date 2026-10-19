from dotenv import load_dotenv
from pydantic import ValidationError
import logging
from logging import Logger

from langgraph.types import Command
from langchain_openai import ChatOpenAI
from langchain_core.runnables import Runnable
from langchain.messages import HumanMessage, SystemMessage, AnyMessage
from langgraph.graph.state import END

from graph.agents.first_step_classificator_agent.prompt import prompt
from graph.agents.first_step_classificator_agent.schemas import RootSubjectClassifierOutputSchema
from load_data import get_subject_tree

logger: Logger = logging.getLogger(__name__)
load_dotenv()

model: ChatOpenAI = ChatOpenAI(
    model="gpt-5.6-luna",
    # model="gpt-6.1-sol",
    temperature=0,
    reasoning={ 
        "effort": "high",  # 'low', 'medium', or 'high'
        "summary": "auto",  # 'detailed', 'auto', or None
    }
)

model_with_structured_output: Runnable = model.with_structured_output(schema=RootSubjectClassifierOutputSchema)


async def agent(state: dict) -> Command:
    raw_question: dict = state.get("question", {})
    question_id: str = raw_question.get("question_id", "")
    question: str = raw_question.get("question", {})
    question_prompt: str = raw_question.get("prompt", "")
    options: str = raw_question.get("options", [])
    
    messages: list[AnyMessage] = [
        SystemMessage(content=prompt),
        HumanMessage(content=f"{question}\n{question_prompt}\n\nAlternativas: {options}")
    ]
    
    goto: str = "second_step_classificator_agent"
    for i in range(3):
        try:
            response: RootSubjectClassifierOutputSchema = await model_with_structured_output.ainvoke(input=messages) # type: ignore
            parent_id: str = next(root["parent"]["subject_id"] for root in get_subject_tree() if root["parent"]["name"] == response.root_classification)
                            
            if response.root_classification not in ["Fora", "Revisar"]:
                return Command(
                    update={"result": {
                        "question_id": question_id,
                        "decision": "",
                        "parent_id": str(parent_id),
                        "parent_name": response.root_classification,
                        "child_id": "",
                        "child_name": "",
                        "explanation": "",
                        "confidence": response.confidence
                    }}, goto=goto)
            else:
                parent_id: str = next(root["parent"]["subject_id"] for root in get_subject_tree() if root["parent"]["name"] == response.root_classification)
                return Command(
                    update={"result": {
                        "question_id": question_id,
                        "decision": response.root_classification.lower(),
                        "parent_id": "",
                        "parent_name": "",
                        "child_id": "",
                        "child_name": "",
                        "explanation": response.explanation,
                        "confidence": response.confidence
                    }}, 
                    goto=END)
        
        except ValidationError as e:
            logger.warning(f"Saída inválida (tentativa {i}): {e}")
            messages.append(HumanMessage(content=(
                f"Sua resposta anterior não seguiu o formato exigido: {e}\n"
                f"Chame a ferramenta '{RootSubjectClassifierOutputSchema.__name__}'com todos os campos exigidos."
            )))
    
    return Command(goto=END)
