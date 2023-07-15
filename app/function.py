import json
import os
from typing import *
from typing import Any
from langchain.output_parsers import *
from langchain import PromptTemplate,  LLMChain
from langchain.tools import BaseTool, StructuredTool, Tool

from app.record import PromptRecord, AppRecord
from pydantic import BaseModel, validator,ValidationError

def get_llm(llm_id:str):
    if 'openai' in llm_id:
        from langchain import OpenAI
        return OpenAI()
    


class FunctionApp(BaseModel):
    record: AppRecord
    callable: Callable
    
    class Config:
        validate_assignment = True
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.callable(*args, **kwds)
    
    def run(self, *args: Any,**kwds: Any) -> Any:
        return self.callable.run(*args, **kwds)
    
    @classmethod
    def from_tool(cls, tool:Tool):
        record = AppRecord.from_tool(tool)
        return cls(record=record,callable=tool)
    
    
    @classmethod
    def from_app_record(cls,record:AppRecord):
        llm = get_llm(record.llm_id)
        prompt = PromptTemplate.from_template(record.description)
        llmchain = LLMChain(llm=llm,prompt=prompt)
        return cls(record=record,callable=llmchain)
    
    def to_openai_schema(self):
        return self.record.to_openai_schema()
    

    
if __name__ == '__main__':
    json = {
        "name": "response",
        "description": "Write a follow up response to the following summary in the specified language: \n\nSummary: {summary}\n\nLanguage: {language}",
        "type": "function",
        "parameters": 
            {
                "summary": {
                    "type": "string",
                    "description": "A review to translate"
                },
                "language": {
                    "type": "string",
                    "description": "the language to response"
                }
            },
        "input_variables": ["summary", "language"],

    }
    from langchain import OpenAI
    
    llm = OpenAI()
    try:
        app = AppRecord(**json)
        fun = FunctionApp.from_app_record(app)
        
        print(fun.run(summary="This is a good movie", language="zh"))
    except ValidationError as e:
        # print(e.json())
        # TODO set back to .json() once we add it
        print(e.errors())
        
    
    ## test from tools
    from langchain.agents import load_tools
    from langchain.tools import  format_tool_to_openai_function
    tools = load_tools(["requests_all",])
    for tool in tools:
        fun = FunctionApp.from_tool(tool)
        print("------- call ", tool.name, "-------")
        # print(fun("hello"))
        
        
   