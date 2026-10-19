import pandas as pd
import asyncio
from dotenv import load_dotenv
from langgraph.graph.state import CompiledStateGraph
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler
import random

from graph.graph import compile
from load_data import get_questions

load_dotenv()

langfuse: Langfuse = Langfuse(
    timeout=600,
    flush_at=20,
    flush_interval=5
)
langfuse_handler = CallbackHandler()

async def main():
    try:
        graph: CompiledStateGraph = compile()
        question_list: list[dict] = get_questions()
        # question_list = random.sample(question_list, 80)
        
        response: dict = await graph.ainvoke(
            input={"questions": question_list},
            config={"callbacks": [langfuse_handler]}
        )
        result: list[dict] = response["result"]
        result = sorted(result, key=lambda x: x["question_id"])
        
        result_df: pd.DataFrame = pd.DataFrame(result)
        result_df = result_df[["question_id", "decision", "parent_id", "child_id", "confidence", "explanation"]]
        result_df.columns = ["id", "decisao", "tema_central_id", "extras_ids", "confianca", "motivo"]
        result_df.to_csv("./publicacao.csv", index=False)
        # result_df.to_csv("./referencia.csv", index=False)
    finally:
        langfuse.flush()
        langfuse.shutdown()

if __name__ == "__main__":
    asyncio.run(main())