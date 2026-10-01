from typing import Dict, Any
from pydantic import BaseModel, Field
from agents.utils import get_llm
from langchain_core.prompts import ChatPromptTemplate

class CodeOutput(BaseModel):
    code: str = Field(description="The generated Python code (main.py content)")
    tests: str = Field(description="The generated pytest code (test_main.py content)")

from langchain_core.output_parsers import PydanticOutputParser

def coder_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("--- CODER ---")
    user_prompt = state.get("user_prompt", "")
    plan = state.get("plan", {})
    fix_context = state.get("fix_context", "")
    test_results = state.get("test_results", {}).get("output", "")
    
    context_str = f"Original Request: {user_prompt}\nPlan: {plan}\n"
    if fix_context:
        context_str += f"\nPrevious Test Errors:\n{test_results}\n\nAdditional Context for Fixing:\n{fix_context}\n"
        
    parser = PydanticOutputParser(pydantic_object=CodeOutput)
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Staff-Level Python Coder. Generate raw Python code and a pytest suite based on the plan. The main file should have logic, test file must import from main. If fixing an error, address the provided logs and context.\n{format_instructions}"),
        ("human", "{context}")
    ])
    
    llm = get_llm()
    chain = prompt | llm | parser
    
    for attempt in range(3):
        try:
            output = chain.invoke({
                "context": context_str,
                "format_instructions": parser.get_format_instructions()
            })
            print("Generated code and tests.")
            break
        except Exception as e:
            if attempt == 2:
                print(f"Failed to parse LLM output after 3 attempts. Error: {e}")
                output = CodeOutput(code="# LLM Parsing Error", tests="def test_error(): assert False")
            else:
                print(f"JSON Parsing error, retrying (attempt {attempt + 1})...")
    
    return {"code": output.code, "tests": output.tests}
