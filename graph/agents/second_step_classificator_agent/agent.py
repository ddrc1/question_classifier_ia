from dotenv import load_dotenv
from pydantic import ValidationError
from typing import Any
import logging
from logging import Logger

from langgraph.types import Command
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage, SystemMessage, AnyMessage
from langgraph.graph.state import END

from graph.agents.second_step_classificator_agent.prompt import prompt
from graph.agents.second_step_classificator_agent.schemas import (
    CriminalLawSpecialLegislationSubjectClassifierOutputSchema,
    CriminalLawSubjectClassifierOutputSchema,
    CriminalProcedureSubjectClassifierOutputSchema,
    CriminologySubjectClassifierOutputSchema
)
from load_data import get_subject_tree, get_main_part_multipart_child_subjects, get_removed_multipart_child_subjects

logger: Logger = logging.getLogger(__name__)
load_dotenv()

model: ChatOpenAI = ChatOpenAI(
    model="gpt-5.6-terra",
    # model="gpt-6.1-sol",
    # temperature=0,
    reasoning={ 
        "effort": "high",  # 'low', 'medium', or 'high'
        "summary": "auto",  # 'detailed', 'auto', or None
    }
)

model_with_structured_output_dict: dict = {
    "Criminologia": model.with_structured_output(schema=CriminologySubjectClassifierOutputSchema),
    "Direito Penal - Legislação Especial": model.with_structured_output(schema=CriminalLawSpecialLegislationSubjectClassifierOutputSchema),
    "Penal": model.with_structured_output(schema=CriminalLawSubjectClassifierOutputSchema),
    "Processo Penal": model.with_structured_output(schema=CriminalProcedureSubjectClassifierOutputSchema)
}

output_schema: dict = {
    "Criminologia": CriminologySubjectClassifierOutputSchema,
    "Direito Penal - Legislação Especial": CriminalLawSpecialLegislationSubjectClassifierOutputSchema,
    "Penal": CriminalLawSubjectClassifierOutputSchema,
    "Processo Penal": CriminalProcedureSubjectClassifierOutputSchema
}


async def agent(state: dict) -> Command:
    raw_question: dict = state.get("question", {})
    question: str = raw_question.get("question", {})
    question_prompt: str = raw_question.get("prompt", "")
    options: str = raw_question.get("options", [])
    partial_result: dict = state.get("result", {})
    
    messages: list[AnyMessage] = [
        SystemMessage(content=prompt),
        HumanMessage(content=f"{question}\n{question_prompt}\n\nAlternativas: {options}")
    ]
    
    for i in range(3):
        try:
            response: Any = await model_with_structured_output_dict[partial_result["parent_name"]].ainvoke(input=messages) # type: ignore
            parent_subject: str = next(root for root in get_subject_tree() if root["parent"]["name"] == partial_result["parent_name"])
            
            if response.child_classification not in ["Fora", "Revisar"] and response.child_classification not in get_main_part_multipart_child_subjects():
                child_id: str = str(next(child["subject_id"] for child in parent_subject["subject_branch"] if child["name"] == response.child_classification))
                partial_result["decision"] = "publicar"
                partial_result["child_id"] = child_id
                partial_result["child_name"] = response.child_classification
            
            elif response.child_classification in get_main_part_multipart_child_subjects():
                revision_multipart: list[dict] = [subject for subject in get_removed_multipart_child_subjects() if response.child_classification.lower() in subject.lower()]
                revision_multipart += [response.child_classification]
                
                partial_result["decision"] = "revisar"
                partial_result["explanation"] = f"A classificação desse assunto possui diferentes partes ({", ".join(revision_multipart)}). Verificar qual é a correta."
                            
            else:
                partial_result["decision"] = response.child_classification.lower()
                partial_result["explanation"] = response.explanation    
            
            partial_result["confidence"] *= response.confidence
            
            return Command(goto=END, update={"result": [partial_result]})
            
        except ValidationError as e:
            logger.warning(f"Saída inválida (tentativa {i}): {e}")
            messages.append(HumanMessage(content=(
                f"Sua resposta anterior não seguiu o formato exigido: {e}\n"
                f"Chame a ferramenta '{output_schema[partial_result["parent_name"]].__name__}'com todos os campos exigidos."
            )))
            
    
    
    return Command(goto=END)
