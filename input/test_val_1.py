from receiver import receiver
from validator import Map_

control = receiver()
dicforpy = control.Process()
if dicforpy:  
    modelopy = Map_.model_validate(dicforpy)
