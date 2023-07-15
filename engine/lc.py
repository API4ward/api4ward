"""Implement function call engine using Langchain Agent

Reference: 
1. https://langchain-langchain.vercel.app/docs/modules/agents/
2. ReAct

"""

if __name__ == '__main__':
    import os

    os.environ["LANGCHAIN_TRACING"] = "true"

    from langchain import OpenAI
    from langchain.agents import load_tools
    from langchain.agents import initialize_agent
    from langchain.agents import AgentType

    llm = OpenAI(temperature=0)
    
    tools = load_tools(["llm-math"], llm=llm)
    agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
    
    agent.run("Who is Leo DiCaprio's girlfriend? What is her current age raised to the 0.43 power?")