from langgraph.types import Command
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage, SystemMessage, AnyMessage

import logging
from logging import Logger
from pydantic import ValidationError
from dotenv import load_dotenv

from graph.agents.pre_processing_agent.prompt import prompt
from graph.agents.pre_processing_agent.schemas import PreProcessingOutputSchema

logger: Logger = logging.getLogger(__name__)
load_dotenv()

model: ChatOpenAI = ChatOpenAI(
    model="gpt-5.6-luna", 
    reasoning={ 
        "effort": "none",  # 'low', 'medium', or 'high'
        "summary": "auto",  # 'detailed', 'auto', or None
    }
)

model_with_structured_output: Runnable = model.with_structured_output(schema=PreProcessingOutputSchema)

async def agent(state: dict) -> Command:
    raw_question: dict = state.get("question", {})
    question_id: str = raw_question.get("question_id", "")
    question: str = raw_question.get("question", "")
    question_prompt: str = raw_question.get("prompt", "")
    options: str = raw_question.get("options", [])
    
    messages: list[AnyMessage] = [
        SystemMessage(content=prompt),
        HumanMessage(content=f"Enunciado da questão: {question}\nComando da questão: {question_prompt}\nAlternativas: {options}")
    ]
    
    goto: str = "first_step_classificator_agent"
    for i in range(3):
        try:
            response: PreProcessingOutputSchema = await model_with_structured_output.ainvoke(input=messages)
            
            cleaned_question: dict = {
                "question_id": question_id,
                "question": response.question,
                "prompt": response.prompt,
                "options": response.options
            }
            return Command(update={"question": cleaned_question}, goto=goto)
        
        except ValidationError as e:
            logger.warning(f"Saída inválida (tentativa {i}): {e}")
            messages.append(HumanMessage(content=(
                f"Sua resposta anterior não seguiu o formato exigido: {e}\n"
                f"Chame a ferramenta '{PreProcessingOutputSchema.__name__}'com todos os campos exigidos."
            )))
    
    return Command(goto=goto)
    
    