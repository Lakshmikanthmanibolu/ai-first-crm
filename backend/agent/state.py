"""LangGraph agent state definition."""
from typing import Annotated, TypedDict, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State that flows through the LangGraph agent."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
