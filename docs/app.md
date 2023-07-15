# Create Function App from Tool
```python

from langchain.agents import load_tools
from langchain.tools import  format_tool_to_openai_function
from engine.engine_openai import FunctionApp, CallEngineOpenAI

fun_apps = list(map(FunctionApp.from_tool,load_tools(["requests_all",]))) 
    
chat = CallEngineOpenAI(functions=fun_apps)
messages = [
    HumanMessage(content="Translate this sentence from English to French. I love programming.")
]

req_msg,params = chat._create_message_dicts(messages,stop=[])     

# test
print(chat.run("Get the content of http://qq.com"))
```

# Expore a Function App to API:

```Python

```