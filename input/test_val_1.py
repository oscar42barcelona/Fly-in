from receiver import receiver
from validator import Map_

control = receiver()
dicforpy = control.Process()
if dicforpy:  
    modelo_py = Map_.model_validate(dicforpy, extra="forbid")
