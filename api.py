

from langchain import PromptTemplate
from app.record import AppRecord
from functions.tools import *
from langchain.agents import AgentType
from app.function import FunctionApp
from fastapi import FastAPI
import json


records = json.load(open("database/prompts.json"))
def query_records(user_id:str,app_name:str):
    
    for record in records[user_id]:
        if record['name'] == app_name:
            return record
    return None

api = FastAPI(
    contact={
        "name": "Admin",
        "url": "http://www.api4ward.com/contact/",
        "email": "admin@api4ward.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

def add_fastapi_endpoint(app: FunctionApp):
    path = os.path.join("/", app.record.user_id, app.record.name)
    api.get(path=path,
            description=app.record.description,
            tags=[app.record.type],
            )(app.run)

@api.get("/{user_id}/{app_name}")
def call_function(user_id:str,app_name:str,input:str):
    record = query_records(user_id,app_name)
    if record is None:
        return {"error":"not found"}
    else:
        apprecord = AppRecord(**record)
        appfun = FunctionApp.from_app_record(apprecord)
        
        return appfun.run(input)

@api.get("/{user_id}/{app_name}/schema")
def get_schema(user_id:str,app_name:str):
    record = query_records(user_id,app_name)
    if record is None:
        return {"error":"not found"}
    else:
        apprecord = AppRecord(**record)
        return apprecord.to_openai_schema()
    
@api.get("/list_apps")
def list_apps():
    fun_list = []
    for user in records:
        for record in records[user]:
            fun_list.append({
                "endpoint":f"/{user}/{record['name']}",
                "description":record['description'],
                "type":record['type'],
                "input_variables":record['input_variables'],})
    return records

@api.put("/{user_id}/{app_name}")
def add_function(user_id:str,app_name:str,description:str,type:str,priority:int=0):
    prompt = PromptTemplate.from_template(description)
    record = AppRecord(
        name=app_name,description=description,type=type,priority=priority,
        input_variables=prompt.input_variables,
    )
    if user_id not in records:
        records[user_id] = []
    
    records[user_id].append(record.to_json())
    return record
if __name__ == '__main__':
    
    
    import uvicorn
    uvicorn.run(api, host="0.0.0.0", port=8000)