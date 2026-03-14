import inspect
from langgraph.prebuilt import create_react_agent
with open("out4.log", "w") as f:
    f.write(str(inspect.signature(create_react_agent)))
