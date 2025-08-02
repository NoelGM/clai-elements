
from langchain_core.runnables import RunnableLambda

echo_chain = RunnableLambda(lambda x: {"output": x["input"]})
