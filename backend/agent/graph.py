"""LangGraph ReAct agent graph for HCP CRM interactions.

This module builds a StateGraph that:
1. Receives user messages
2. Routes through the LLM to decide which tool(s) to call
3. Executes tools (log, edit, search, history, suggest, recommend, followup, summarize)
4. Returns the final response
"""

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from backend.agent.state import AgentState
from backend.agent.tools import ALL_TOOLS
from backend.config import GROQ_API_KEY, LLM_MODEL


SYSTEM_PROMPT = """You are an AI CRM Agent for a pharmaceutical company, helping field sales representatives manage their interactions with Healthcare Professionals (HCPs).

Your capabilities (via tools):
1. **log_interaction** – Record new interactions with doctors. Capture meeting notes, call summaries, etc. After logging, provide an AI-generated summary, sentiment analysis, key topics, and extracted entities.
2. **edit_interaction** – Modify previously logged interactions. Update notes, status, follow-up actions, etc.
3. **search_hcp** – Find doctors in the database by name, specialty, territory, or institution.
4. **get_interaction_history** – View past interactions with a specific HCP or recent interactions across all HCPs.
5. **suggest_talking_points** – Generate personalized talking points for upcoming meetings based on HCP profile and past interactions.
6. **recommend_product** – Recommend the best product for a specific HCP based on their specialty, history, and product alignment.
7. **generate_followup_email** – Generate a professional follow-up email draft after an interaction.
8. **summarize_notes** – Extract entities (doctors, products, diseases, competitors, sentiment) from raw notes and generate structured summaries.

Guidelines:
- When the user wants to log an interaction, first identify the HCP (use search_hcp if needed to find their ID), then use log_interaction.
- After logging an interaction, ALWAYS provide a structured response with:
  * **AI Summary**: A concise summary of the interaction
  * **Sentiment**: positive/neutral/negative with reasoning
  * **Key Topics**: List of topics discussed
  * **Extracted Entities**: Doctors, products, diseases, competitors mentioned
  * **Follow-up Actions**: Recommended next steps
  * **Confidence Score**: Your confidence in the analysis (0-100%)
- When editing, confirm what was changed.
- Be proactive in suggesting follow-up actions.
- When recommending products, provide reasoning and a confidence percentage.
- When generating talking points, make them specific and actionable.
- For follow-up emails, be professional and reference specific discussion points.
- Always be professional and concise.
- Format responses clearly with bullet points or sections when appropriate.
- If the user provides free-text notes, extract structured data (products mentioned, key topics, sentiment) and include it in your response.

Important: When calling tools, use exact field names and formats. For product_ids, use comma-separated numbers like "1,3". For dates, use YYYY-MM-DD format.
"""


def build_agent():
    """Build and compile the LangGraph agent."""
    # Initialize Groq LLM
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model=LLM_MODEL,
        temperature=0.3,
        max_tokens=2048,
    )

    # Bind tools to the LLM
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    # Define the node that calls the LLM
    def call_model(state: AgentState):
        messages = state["messages"]
        # Prepend system message
        system_msg = SystemMessage(content=SYSTEM_PROMPT)
        response = llm_with_tools.invoke([system_msg] + list(messages))
        return {"messages": [response]}

    # Define the routing function
    def should_continue(state: AgentState):
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    # Build the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(ALL_TOOLS))

    # Set entry point
    workflow.set_entry_point("agent")

    # Add edges
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    workflow.add_edge("tools", "agent")

    # Compile
    return workflow.compile()


# Singleton agent instance
_agent = None


def get_agent():
    """Return the compiled agent (singleton)."""
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent
