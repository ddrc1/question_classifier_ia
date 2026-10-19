from typing import Annotated, TypedDict, Literal
from operator import add

class Question(TypedDict):
    question_id: str
    question: str
    prompt: str
    options: str


class Subject(TypedDict):
    subject_id: str
    name: str
    
    
class SubjectTree(TypedDict):
    parent: Subject
    subject_branch: list[Subject]


class Result(TypedDict):
    question_id: str
    decision: Literal["publicar", "revisar", "fora"]
    parent_id: str
    parent_name: str
    child_id: str
    child_name: str
    explanation: str
    confidence: float
    

class SingleQuestionGraphStateSchema(TypedDict):
    question: Question
    result: Result
    
    
class GraphStateSchema(TypedDict):
    questions: list[Question]
    result: Annotated[list[Result], add]
