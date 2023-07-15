from enum import Enum
from typing import *

class CallState(Enum):
    Continue = 0
    Sccuess = 1
    Failed = -1
    
class CallEngine(Callable):
    """Use state machine to process function call"""
    
    
    def __call__(self, *args,**kwargs)-> Tuple[Any, CallState]:
        raise NotImplementedError()
    
    
        