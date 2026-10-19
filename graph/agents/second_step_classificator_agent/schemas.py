from typing import Literal
from pydantic import BaseModel, Field, create_model
from load_data import get_subject_tree

subject_tree: list[dict] = get_subject_tree()

def get_create_model(model_name: str, classification_options: list[str]) -> type[BaseModel]:
    classification_options += ["Revisar", "Fora"]
    classification_type = Literal.__getitem__(tuple(classification_options))
    
    return create_model(
        model_name,
        child_classification=(
            classification_type,
            Field(description="""Classificação do tópico da questão. 
                    Se não enquadrado nos temas, utilizar 'Fora'.
                    Se tiver dúvida, utilizar 'Revisar'"""),
        ),
        explanation=(str, Field(description="Explicação. Utilizar apenas quando classificação for 'Revisar' ou 'Fora'", default="")),
        confidence=(float, Field(description="O quanto está confiante na classificação dada.", ge=0.0, le=1.0))
    )
    
def get_subject_branch_name_list(root_subject_name: str) -> list[str]:
    subject_branch: list[dict] = next(root_subject["subject_branch"] for root_subject in subject_tree if root_subject["parent"]["name"] == root_subject_name)
    subject_branch_names: list[str] = [child["name"] for child in subject_branch]
    
    return subject_branch_names

subject_branch_names: list[str] = get_subject_branch_name_list(root_subject_name="Criminologia")
CriminologySubjectClassifierOutputSchema: type[BaseModel] = get_create_model("CriminologySubjectClassifierOutputSchema", subject_branch_names)


subject_branch_names: list[str] = get_subject_branch_name_list(root_subject_name="Direito Penal - Legislação Especial")
CriminalLawSpecialLegislationSubjectClassifierOutputSchema: type[BaseModel] = get_create_model("CriminalLawSpecialLegislationSubjectClassifierOutputSchema", subject_branch_names)


subject_branch_names: list[str] = get_subject_branch_name_list(root_subject_name="Penal")
CriminalLawSubjectClassifierOutputSchema: type[BaseModel] = get_create_model("CriminalLawSubjectClassifierOutputSchema", subject_branch_names)


subject_branch_names: list[str] = get_subject_branch_name_list(root_subject_name="Processo Penal")
CriminalProcedureSubjectClassifierOutputSchema: type[BaseModel] = get_create_model("CriminalProcedureSubjectClassifierOutputSchema", subject_branch_names)
