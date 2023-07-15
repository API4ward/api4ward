# [openAI Plugin](https://platform.openai.com/docs/plugins/introduction)

## Plugin manifest

```json
{
    "schema_version": "v1",
    "name_for_human": "TODO List",
    "name_for_model": "todo",
    "description_for_human": "Manage your TODO list. You can add, remove and view your TODOs.",
    "description_for_model": "Help the user with managing a TODO list. You can add, remove and view your TODOs.",
    "auth": {
        "type": "none"
    },
    "api": {
        "type": "openapi",
        "url": "http://localhost:3333/openapi.yaml"
    },
    "logo_url": "http://localhost:3333/logo.png",
    "contact_email": "support@example.com",
    "legal_info_url": "http://www.example.com/legal"
}
```
## [Plugin API](https://swagger.io/specification/)
```json
openapi: 3.0.1
info:
    title: TODO Plugin
    description: A plugin that allows the user to create and manage a TODO list using ChatGPT. If you do not know the user's username, ask them first before making queries to the plugin. Otherwise, use the username "global".
    version: "v1"
servers:
    - url: PLUGIN_HOSTNAME
paths:
    /todos/{username}:
        get:
            operationId: getTodos
            summary: Get the list of todos
            parameters:
                - in: path
                  name: username
                  schema:
                      type: string
                  required: true
                  description: The name of the user.
            responses:
                "200":
                    description: OK
                    content:
                        application/json:
                            schema:
                                $ref: "#/components/schemas/getTodosResponse"
        post:
            operationId: addTodo
            summary: Add a todo to the list
            parameters:
                - in: path
                  name: username
                  schema:
                      type: string
                  required: true
                  description: The name of the user.
            requestBody:
                required: true
                content:
                    application/json:
                        schema:
                            $ref: "#/components/schemas/addTodoRequest"
            responses:
                "200":
                    description: OK
        delete:
            operationId: deleteTodo
            summary: Delete a todo from the list
            parameters:
                - in: path
                  name: username
                  schema:
                      type: string
                  required: true
                  description: The name of the user.
            requestBody:
                required: true
                content:
                    application/json:
                        schema:
                            $ref: "#/components/schemas/deleteTodoRequest"
            responses:
                "200":
                    description: OK

components:
    schemas:
        getTodosResponse:
            type: object
            properties:
                todos:
                    type: array
                    items:
                        type: string
                    description: The list of todos.
        addTodoRequest:
            type: object
            required:
                - todo
            properties:
                todo:
                    type: string
                    description: The todo to add to the list.
                    required: true
        deleteTodoRequest:
            type: object
            required:
                - todo_idx
            properties:
                todo_idx:
                    type: integer
                    description: The index of the todo to delete.
                    required: true
```

Keep in mind the following limits in your OpenAPI specification, which are subject to change:

1. 200 characters max for each API endpoint description/summary field in API specification
2. 200 characters max for each API param description field in API specification

## Writing description

When a user makes a query that might be a potential request that goes to a plugin, the model looks through the descriptions of the endpoints in the OpenAPI specification along with the `description_for_model` in the manifest file. Just like with prompting other language models, you will want to test out multiple prompts and descriptions to see what works best.

1. Your descriptions should not attempt to control the mood, personality, or exact responses of ChatGPT. ChatGPT is designed to write appropriate responses to plugins.
2. Your descriptions should not encourage ChatGPT to use the plugin when the user hasn't asked for your plugin's particular category of service.
3. Your descriptions should not prescribe specific triggers for ChatGPT to use the plugin. ChatGPT is designed to use your plugin automatically when appropriate.
4. Plugin API responses should return raw data instead of natural language responses unless it's necessary. ChatGPT will provide its own natural language response using the returned data.

Good Examples:
```text


```

# [OpenAI Function](https://platform.openai.com/docs/guides/gpt/function-calling)

The latest models (`gpt-3.5-turbo-0613` and `gpt-4-0613`) have been fine-tuned to both detect when a function should to be called.


## define function in [Create chat completion](https://platform.openai.com/docs/api-reference/chat/create)
functions array Optional 

A list of functions the model may generate JSON inputs for.

> name, string, required

The name of the function to be called. Must be a-z, A-Z, 0-9, or contain underscores and dashes, with a maximum length of 64.

> description, string, Optional

The description of what the function does.

> parameters, object, Optional

The parameters the functions accepts, described as a JSON Schema object. See the guide for examples, and the JSON Schema reference for documentation about the format.

Example:
```python

import openai
import json


# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    weather_info = {
        "location": location,
        "temperature": "72",
        "unit": unit,
        "forecast": ["sunny", "windy"],
    }
    return json.dumps(weather_info)


def run_conversation():
    # Step 1: send the conversation and available functions to GPT
    messages = [{"role": "user", "content": "What's the weather like in Boston?"}]
    functions = [
        {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        }
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=functions,
        function_call="auto",  # auto is default, but we'll be explicit
    )
    response_message = response["choices"][0]["message"]

    # Step 2: check if GPT wanted to call a function
    if response_message.get("function_call"):
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_current_weather": get_current_weather,
        }  # only one function in this example, but you can have multiple
        function_name = response_message["function_call"]["name"]
        fuction_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        function_response = fuction_to_call(
            location=function_args.get("location"),
            unit=function_args.get("unit"),
        )

        # Step 4: send the info on the function call and function response to GPT
        messages.append(response_message)  # extend conversation with assistant's reply
        messages.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )  # extend conversation with function response
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
        )  # get a new response from GPT where it can see the function response
        return second_response


print(run_conversation())
```

## Define functions with Structured outputs

We use Langchain to parse the LLM output string into a Python dictionary.

Usage:
```python
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser

gift_schema = ResponseSchema(name="gift",
                             description="Was the item purchased\
                             as a gift for someone else? \
                             Answer True if yes,\
                             False if not or unknown.")
delivery_days_schema = ResponseSchema(name="delivery_days",
                                      description="How many days\
                                      did it take for the product\
                                      to arrive? If this \
                                      information is not found,\
                                      output -1.")
price_value_schema = ResponseSchema(name="price_value",
                                    description="Extract any\
                                    sentences about the value or \
                                    price, and output them as a \
                                    comma separated Python list.")

response_schemas = [gift_schema, 
                    delivery_days_schema,
                    price_value_schema]

output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

format_instructions = output_parser.get_format_instructions()

```

Insert format instructions to LLM:

The output should be a markdown code snippet formatted in the following schema, including the leading and trailing "\`\`\`json" and "\`\`\`":

```json
{
	"gift": string  // Was the item purchased                             as a gift for someone else?                              Answer True if yes,                             False if not or unknown.
	"delivery_days": string  // How many days                                      did it take for the product                                      to arrive? If this                                       information is not found,                                      output -1.
	"price_value": string  // Extract any                                    sentences about the value or                                     price, and output them as a                                     comma separated Python list.
}
```