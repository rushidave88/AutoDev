from typing import Dict, Any, List
from pydantic import BaseModel, Field
from agents.utils import get_llm
from langchain_core.prompts import ChatPromptTemplate

class Step(BaseModel):
    step_number: int = Field(description="The order of the step")
    description: str = Field(description="Description of what to do")

class Plan(BaseModel):
    steps: List[Step] = Field(description="List of steps to execute the task")

from langchain_core.output_parsers import PydanticOutputParser

def architect_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("--- ARCHITECT ---")
    user_prompt = state.get("user_prompt", "")
    
    parser = PydanticOutputParser(pydantic_object=Plan)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert Software Architect. Break down the user prompt into a step-by-step implementation plan.\n{format_instructions}"),
        ("human", "{user_prompt}")
    ])
    
    llm = get_llm()
    chain = prompt | llm | parser
    
    for attempt in range(3):
        try:
            plan = chain.invoke({
                "user_prompt": user_prompt,
                "format_instructions": parser.get_format_instructions()
            })
            print(f"Generated {len(plan.steps)} steps.")
            break
        except Exception as e:
            if attempt == 2:
                print(f"Failed to parse LLM output after 3 attempts. Error: {e}")
                plan = Plan(steps=[Step(step_number=1, description="Fallback step due to parsing failure")])
            else:
                print(f"JSON Parsing error, retrying (attempt {attempt + 1})...")
    
    return {"plan": plan.model_dump()}
