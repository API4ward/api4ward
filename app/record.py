""" create a quickstart app with prompt

Reference:
1. https://docs.pydantic.dev/latest/usage/types/list_types/
2. openapi schema: https://fastapi.tiangolo.com/tutorial/schema-extra-example/
"""
from typing import Deque, List, Optional, Tuple,Dict
from enum import Enum
from langchain import PromptTemplate
from pydantic import BaseModel, Field

from langchain.tools import Tool
import inspect
class AppTypeEnum(str, Enum):
    function = 'function'
    chatbot = 'chatbot'

class VariableSchema(BaseModel):
    type: str
    description: str = ""
    default: Optional[str] = None

class PromptRecord(BaseModel):
    name: str
    description: str
    priority: int = 0
    # input and output variables
    input_variables: Optional[List[str]] = None
    output_variables: Optional[List[str]] = None
    parameters: Optional[Dict[str,VariableSchema]] = None
    type: Optional[AppTypeEnum ] = AppTypeEnum.function
    
    @classmethod
    def from_tool(cls, tool:Tool,priority:int=0):
        if tool.args_schema:
            parameters = {}
            for k,v in tool.args_schema.schema()["properties"].items():
                del v["title"]
                parameters[k] = v
            inputs = tool.args_schema.schema()["required"]
            
        elif hasattr(tool,'func'):
            # TODO: parse function docstring
            fullargs=inspect.getfullargspec(tool.func)
            inputs = fullargs.args
            parameters = {
                "__output1":{ "type": "string", "description": "output string"},
            }
            for k in inputs:
                parameters[k] = { "type": "string",}
        elif tool.args:
            inputs = list(tool.args.keys())
            parameters = {
                "__output1":{ "type": "string", "description": "output string"},
            }
            for k in inputs:
                parameters[k] = { "type": "string",}
            
        
        record = cls(
            name=tool.name,
            description=tool.description,
            priority=priority,
            input_variables=inputs,
            output_variables=["__output1"],
            parameters=parameters,
            
        )
        return record
    
    @classmethod
    def from_template(cls, name:str, template: str, priority:int=0):
        prompt = PromptTemplate.from_template(template)
        schema_= prompt.schema()
        parameters = schema_["properties"]
        record = cls(
            name = name,
            description = prompt.template,
            priority = priority,
            input_variables = prompt.input_variables,
            output_variables=["__output1"],
            parameters=parameters,            
        )
        return record
    
    
    
    def to_openai_schema(self):
        parameters = {'required':self.input_variables}
        parameters['properties'] = {}
        parameters['type']="object"
        for var in self.input_variables:
            value = self.parameters[var].dict()
            value = {k:v for k,v in value.items() if v}
            parameters['properties'][var] = value
            
            # parameters['required'].append(var)
        
        schema = {
            "name":self.name,
            "description": self.description,
            "parameters": parameters,
        }
        return schema
    
    def to_json(self,*args,**kwargs):
        return self.json(*args,**kwargs)
    
    
class AppRecord(PromptRecord):
    # project information
    llm_id: str = "openai"
    user_id: str = 'test_user'
    project_id: str = 'test_project'

    

    
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
    fun = PromptRecord(**json)
    
    def response(summary:str, language:str):
        """_summary_

        Args:
            summary (str): a review to translate
            language (str): _description_

        Returns:
            _type_: _description_
        """
        print(f"Response to {summary} in {language}")
        return f"Response to {summary} in {language}"
    
    tool = Tool.from_function(response, "response", "Response to {summary} in {language}")
    
    prompt = PromptRecord.from_tool(tool)
    print(prompt)
    
    
    ## test from tools
    from langchain.agents import load_tools
    from langchain.tools import  format_tool_to_openai_function
    tools = load_tools(["requests_all",])
    for tool in tools:
        record = PromptRecord.from_tool(tool)
        print(record)