# Prompt

Use the prompt template to create a function or an application.

A prompt template can contain, see in [Prompt template](https://langchain-langchain.vercel.app/docs/modules/model_io/prompts/prompt_templates/):

- instructions to the language model,
- a set of few shot examples to help the language model generate a better response,
- a question to the language model.

Here is an example of a prompt template:

```
You are a naming consultant for new companies.
What is a good name for a company that makes {product}?
```

Usage:

```python   
from langchain import PromptTemplate

template = "Tell me a {adjective} joke about {content}."
prompt_template = PromptTemplate.from_template(template)
prompt_template.input_variables
# -> ['adjective', 'content']
prompt_template.format(adjective="funny", content="chickens")
```

## Create a function prompt

