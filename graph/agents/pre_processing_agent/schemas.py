from pydantic import BaseModel, Field

class PreProcessingOutputSchema(BaseModel):
    question: str = Field(description="Enunciado da questão limpa")
    prompt: str = Field(description="Comando da questão limpo")
    options: str = Field(description="Comando da questão limpo")
    