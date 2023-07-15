from openai import api_resources
import functools

BASE_URL = "https://api.openai.com/v1"
for k, v in api_resources.__dict__.items():
    api_resources.__dict__[k] = functools.partial(v, api_base = BASE_URL)