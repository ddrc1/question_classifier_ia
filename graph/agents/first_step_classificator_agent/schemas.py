from pydantic import BaseModel, Field
from typing import Literal
from load_data import get_subject_tree

subject_tree: list[dict] = get_subject_tree()

subject_names = [root_subject["parent"]["name"] for root_subject in subject_tree]
subject_names += ["Revisar", "Fora"]

class RootSubjectClassifierOutputSchema(BaseModel):
    root_classification: Literal["Criminologia", "Direito Penal - Legislação Especial", "Penal", "Processo Penal"] = Field(
        description="""Classificação do tópico da questão. 
              Se não enquadrado nos temas, utilizar 'Fora'.
              Se tiver dúvida, utilizar 'Revisar'"""
    )
    explanation: str = Field(description="Explicação. Utilizar apenas quando classificação for 'Revisar' ou 'Fora'", default="")
    confidence: float = Field(description="O quanto está confiante na classificação dada.", ge=0.0, le=1.0)
