import gradio as gr
import json
from typing import *
from app.prompt_record import PromptRecord
from functions.function import Function

def load_prompts(path):
    
    function_data = json.load(open(path))
    user = "erow"
    function_data = function_data[user]
    apps = []
    for i in range(len(function_data)):
        app = PromptRecord(**function_data[i])
        apps.append(app)
    return apps

def create_fun(apps):
    from langchain.llms import OpenAI
    llm = OpenAI(temperature=0.9)
    
    functions = []
    for function in apps:
        fun = Function(llm, "erow")
        fun.from_model(function)
        functions.append(fun)
    return functions


def create_fun_interface(func_list:List[Function]):
    def warp_call(fun:Function):
        def _run(*args):
            input = {}
            for var,value in zip(fun.prompt.input_variables,args):
                input[var]=value
            output=fun.engine.run(input)
            return output
        return _run
    def _create_fun(fun:Function):
        
        gr.Textbox(fun.description,label="Description",interactive=False)
        inputs = []
        with gr.Row():
            for var in fun.prompt.input_variables:
                input = gr.Textbox(label=var,interactive=True)
                inputs.append(input)
        with gr.Row():
            run_bt=gr.Button("Run")
            output=gr.Textbox(label="Output",interactive=False)
        
        return run_bt,inputs,output
        
        
    with gr.Column():
        for fun in func_list:
            
            run_bt,inputs,output = _create_fun(fun)
            run_bt.click(warp_call(fun),inputs,output,api_name=fun.name)
            
    

def add_fun_interface():
    def _add_fun(name:str,description:str,prompt:str):
        user = "erow"
        app_prompt=PromptRecord(name=name,description=description,prompt=prompt,type="function")
        
        data=json.load(open("database/prompts.json"))
        data[user].append(app_prompt.json())
        json.dump(data,open("database/prompts.json","w"),indent=2)
    gr.Label("Add function")
    with gr.Row():
        with gr.Column():
            prompt=gr.Textbox(label="Prompt",interactive=True,lines=5)
        with gr.Column():
            name=gr.Textbox(label="Name",interactive=True)
            description=gr.Textbox(label="Description",interactive=True)
            add_btn=gr.Button("Add") 
        add_btn.click(_add_fun,[name,description,prompt],api_name="add_fun")
        

            
def demo():
    apps=load_prompts("database/prompts.json")
    functions=create_fun(apps)
    with gr.Blocks() as demo:
        create_fun_interface(functions)
        add_fun_interface()
    return demo
    
if __name__ == '__main__':
    demo().launch()

    