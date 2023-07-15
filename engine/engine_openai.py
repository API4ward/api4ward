"""Implement function call engine using OpenAI API

Reference: https://platform.openai.com/docs/guides/gpt/function-calling


"""
from typing import Any, List, Optional
from langchain.callbacks.manager import Callbacks
from langchain.schema import BaseMessage
from pydantic import BaseModel, validator
from app.function import FunctionApp

from typing import *
from langchain.chat_models import ChatOpenAI

from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser


from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
import json
from engine.engine import CallEngine
from langchain.agents import BaseSingleActionAgent

from langchain.schema import SystemMessage, HumanMessage,  AIMessage, FunctionMessage

class FunctionCallMessage(BaseModel):
    name: str
    arguments: Dict[str,str]
    
    @validator("arguments",pre=True)
    def set_arguments(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return v
        else:
            return v
    
    
    @property
    def type(self) -> str:
        """Type of the message, used for serialization."""
        return "function_call"
    
class CallEngineOpenAI(ChatOpenAI,CallEngine):
    functions: List[FunctionApp] = []
    model_name: str = "gpt-3.5-turbo-0613" # this supports function call
    
    @property
    def _invocation_params(self) -> Mapping[str, Any]:
        """Get the parameters used to invoke the model."""
        openai_creds: Dict[str, Any] = {
            "api_key": self.openai_api_key,
            "api_base": self.openai_api_base,
            "organization": self.openai_organization,
            "model": self.model_name,
            "functions": [fun.to_openai_schema() for fun in self.functions]
        }
        if self.openai_proxy:
            import openai

            openai.proxy = {"http": self.openai_proxy, "https": self.openai_proxy}  # type: ignore[assignment]  # noqa: E501
        return {**openai_creds, **self._default_params}
    
    def run(self, input):
        
        # TODO: the difference between run and __call__ 
        response = self([HumanMessage(content=input)])
        content = ""
        ans = []
        ans.append(response)
        if hasattr(response,'additional_kwargs') and "function_call" in response.additional_kwargs:
            call_msg = FunctionCallMessage(**response.additional_kwargs["function_call"])
            ans.append(self.process_function_call(call_msg))
        content +=response.content
        return content, ans
        
        
    def process_function_call(self, call_message:FunctionCallMessage)->FunctionMessage:
        """process function call"""
        for fun in self.functions:
            if fun.record.name == call_message.name:
                arguments = call_message.arguments
                output=fun.run(arguments)
                return FunctionMessage(content=output,name=call_message.name)

    
    @staticmethod
    def from_agent(cls,agent: BaseSingleActionAgent):
        pass
    
if __name__ == '__main__':
    
    
    ## test from tools
    from langchain.agents import create_csv_agent, Agent
    from langchain.llms import OpenAI
    from langchain.chat_models import ChatOpenAI
    from langchain.agents.agent_types import AgentType
    
    agent = create_csv_agent(
        ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613"),
        "titanic.csv",
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
    )
    
    agent.run("how many rows are there?")
    agent.run("how many people have more than 3 siblings")
    agent.run("whats the square root of the average age?")
    
    
    