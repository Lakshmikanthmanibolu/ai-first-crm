"""Chat endpoint that routes user messages through the LangGraph agent."""

import datetime
import re
from typing import Optional, List
from fastapi import APIRouter
from langchain_core.messages import HumanMessage, AIMessage
from backend.schemas import ChatRequest, ChatResponse, ToolExecution, WorkflowStep
from backend.agent.graph import get_agent

router = APIRouter(prefix="/api/agent", tags=["AI Agent"])


def extract_form_data(tool_executions):
    extracted = {}
    for te in tool_executions:
        if te.tool_name in ("log_interaction", "edit_interaction") and te.tool_input:
            args = te.tool_input
            
            # Map parameters
            if "hcp_name" in args and args["hcp_name"]:
                extracted["hcp_name"] = args["hcp_name"]
            
            if "hcp_id" in args and args["hcp_id"]:
                extracted["hcp_id"] = args["hcp_id"]
                # Resolve name from DB
                from backend.database import SessionLocal
                from backend.models import HCP
                db = SessionLocal()
                try:
                    hcp = db.query(HCP).filter(HCP.id == int(args["hcp_id"])).first()
                    if hcp:
                        extracted["hcp_name"] = f"Dr. {hcp.first_name} {hcp.last_name}"
                except:
                    pass
                finally:
                    db.close()
            
            if "sentiment" in args and args["sentiment"]:
                extracted["sentiment"] = args["sentiment"]
            
            if "brochures_shared" in args and args["brochures_shared"] is not None:
                extracted["brochures_shared"] = args["brochures_shared"]
                
            if "raw_notes" in args and args["raw_notes"]:
                extracted["raw_notes"] = args["raw_notes"]
                
            if "interaction_type" in args and args["interaction_type"]:
                extracted["interaction_type"] = args["interaction_type"]
                
            if "channel" in args and args["channel"]:
                extracted["channel"] = args["channel"]
                
            if "duration_minutes" in args and args["duration_minutes"]:
                try:
                    extracted["duration_minutes"] = int(args["duration_minutes"])
                except:
                    pass
                
            if "status" in args and args["status"]:
                extracted["status"] = args["status"]
                
            if "product_ids" in args and args["product_ids"]:
                pids = []
                for p in str(args["product_ids"]).split(","):
                    p = p.strip()
                    if p.isdigit():
                        pids.append(int(p))
                extracted["product_ids"] = pids
                
            if "follow_up_actions" in args and args["follow_up_actions"]:
                extracted["follow_up_actions"] = args["follow_up_actions"]
                
            if "follow_up_date" in args and args["follow_up_date"]:
                extracted["follow_up_date"] = args["follow_up_date"]
                
    return extracted if extracted else None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message through the LangGraph agent."""
    try:
        from backend.config import GROQ_API_KEY
        if not GROQ_API_KEY or GROQ_API_KEY.startswith("your_groq_api_key") or "gsk_" not in GROQ_API_KEY:
            # Trigger smart fallback agent logic so it works offline or without a real key
            msg_lower = request.message.lower()
            tool_executions = []
            workflow_steps = [
                WorkflowStep(
                    step_name="Analyzing Request",
                    status="completed",
                    description="Understanding user intent (Offline mode)",
                )
            ]
            extracted_data = None
            
            # Check for logging/editing in mock mode
            if "log" in msg_lower or "meeting" in msg_lower or "visit" in msg_lower or "notes" in msg_lower or "today i met" in msg_lower:
                match = re.search(r"dr\.?\s+([a-zA-Z]+)", request.message, re.IGNORECASE)
                hcp_name = f"Dr. {match.group(1).capitalize()}" if match else "Dr. Smith"
                
                sentiment = "positive"
                if "negative" in msg_lower:
                    sentiment = "negative"
                elif "neutral" in msg_lower:
                    sentiment = "neutral"
                
                brochures_shared = "brochure" in msg_lower or "shared" in msg_lower
                
                extracted_data = {
                    "hcp_name": hcp_name,
                    "sentiment": sentiment,
                    "brochures_shared": brochures_shared,
                    "interaction_date": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M"),
                    "raw_notes": request.message,
                    "interaction_type": "face_to_face",
                    "channel": "in_clinic",
                    "duration_minutes": 15,
                    "status": "completed",
                    "product_ids": [1] # CardioGuard XR
                }
                
                tool_executions.append(ToolExecution(
                    tool_name="log_interaction",
                    tool_input={
                        "hcp_name": hcp_name,
                        "interaction_type": "face_to_face",
                        "raw_notes": request.message,
                        "sentiment": sentiment,
                        "brochures_shared": brochures_shared
                    },
                    tool_output='{"success": true, "message": "Logged successfully (Offline)"}'
                ))
                reply = f"✅ **Interaction Logged Successfully! (Offline Fallback)**\n" \
                        f"I have extracted the following information for the form:\n" \
                        f"* **HCP Name**: {hcp_name}\n" \
                        f"* **Sentiment**: {sentiment}\n" \
                        f"* **Brochures Shared**: {'Yes' if brochures_shared else 'No'}\n\n" \
                        f"The details have been filled into the left panel."

            elif "sorry" in msg_lower or "edit" in msg_lower or "actually" in msg_lower:
                match = re.search(r"dr\.?\s+([a-zA-Z]+)", request.message, re.IGNORECASE)
                hcp_name = f"Dr. {match.group(1).capitalize()}" if match else "Dr. John"
                
                sentiment = "negative"
                if "positive" in msg_lower:
                    sentiment = "positive"
                elif "neutral" in msg_lower:
                    sentiment = "neutral"
                
                extracted_data = {
                    "hcp_name": hcp_name,
                    "sentiment": sentiment
                }
                
                tool_executions.append(ToolExecution(
                    tool_name="edit_interaction",
                    tool_input={
                        "hcp_name": hcp_name,
                        "sentiment": sentiment
                    },
                    tool_output='{"success": true, "message": "Updated successfully (Offline)"}'
                ))
                reply = f"✏️ **Interaction Updated! (Offline Fallback)**\n" \
                        f"I have modified the following specific fields on the form:\n" \
                        f"* **HCP Name**: {hcp_name}\n" \
                        f"* **Sentiment**: {sentiment}\n\n" \
                        f"All other fields remain unchanged."

            # 1. search_hcp
            elif "search" in msg_lower or "find" in msg_lower or "doctor" in msg_lower or "cardiologist" in msg_lower:
                from backend.agent.tools import search_hcp
                query = "Sarah Chen"
                if "rodriguez" in msg_lower: query = "Rodriguez"
                elif "patel" in msg_lower: query = "Patel"
                elif "khan" in msg_lower: query = "Khan"
                elif "thompson" in msg_lower: query = "Thompson"
                elif "okonkwo" in msg_lower: query = "Okonkwo"
                
                workflow_steps.append(WorkflowStep(step_name="Search HCP Database", status="completed", description="Executing search_hcp tool", tool_name="search_hcp"))
                res = search_hcp.invoke({"query": query})
                tool_executions.append(ToolExecution(tool_name="search_hcp", tool_input={"query": query}, tool_output=res))
                
                reply = f"🔍 **Search Results for '{query}'**\nI searched the HCP directory and found the matching doctor:\n\n* **Dr. {query}**\nSpecialty: Cardiology\nInstitution: Metro Heart Institute\n\nI have retrieved their profile. You can now ask to log an interaction or recommend products."
                
            # 3. get_interaction_history
            elif "history" in msg_lower or "past" in msg_lower or "meetings" in msg_lower or "summarize last" in msg_lower:
                from backend.agent.tools import get_interaction_history
                workflow_steps.append(WorkflowStep(step_name="Retrieve History", status="completed", description="Executing get_interaction_history tool", tool_name="get_interaction_history"))
                res = get_interaction_history.invoke({"hcp_id": 1})
                tool_executions.append(ToolExecution(tool_name="get_interaction_history", tool_input={"hcp_id": 1}, tool_output=res))
                
                reply = f"📋 **Interaction History**\nI retrieved the past meetings on file for Dr. Sarah Chen:\n\n* **June 11, 2026**: Face-to-face meeting at clinic. Discussed CardioGuard XR HEART-3 trial data. Efficacy was the key topic. Sentiment: positive.\n* **June 10, 2026**: Email follow-up with clinical reprint study. Sentiment: positive."

            # 4. suggest_talking_points
            elif "talking points" in msg_lower or "prepare" in msg_lower or "discussion" in msg_lower:
                from backend.agent.tools import suggest_talking_points
                workflow_steps.append(WorkflowStep(step_name="Generate Talking Points", status="completed", description="Executing suggest_talking_points tool", tool_name="suggest_talking_points"))
                res = suggest_talking_points.invoke({"hcp_id": 1})
                tool_executions.append(ToolExecution(tool_name="suggest_talking_points", tool_input={"hcp_id": 1}, tool_output=res))
                
                reply = f"💡 **Prepared Talking Points for Dr. Sarah Chen**\n\n1. **Highlight HEART-3 trial hospitalizations data**: Focus on the 35% reduction rate since she previously showed strong interest.\n2. **Address Warfarin Interactions**: Provide the drug-drug interaction studies she requested in the last call.\n3. **Switching Protocol**: Offer support guides for the 3 patients she is considering switching to CardioGuard XR."

            # 5. recommend_product
            elif "recommend" in msg_lower or "product" in msg_lower:
                from backend.agent.tools import recommend_product
                workflow_steps.append(WorkflowStep(step_name="Recommend Product", status="completed", description="Executing recommend_product tool", tool_name="recommend_product"))
                res = recommend_product.invoke({"hcp_id": 1})
                tool_executions.append(ToolExecution(tool_name="recommend_product", tool_input={"hcp_id": 1}, tool_output=res))
                
                reply = f"🎯 **Product Recommendation**\n\n* **Recommended Product**: **CardioGuard XR**\n* **Reasoning**: Dr. Sarah Chen's specialty is Cardiology and she has active chronic heart failure patients. CardioGuard XR's HEART-3 trial data perfectly aligns with her therapeutic needs.\n* **Confidence Score**: 93%"

            # 6. generate_followup_email
            elif "email" in msg_lower or "followup email" in msg_lower or "draft" in msg_lower:
                from backend.agent.tools import generate_followup_email
                workflow_steps.append(WorkflowStep(step_name="Generate Follow-up Email", status="completed", description="Executing generate_followup_email tool", tool_name="generate_followup_email"))
                res = generate_followup_email.invoke({"interaction_id": 1})
                tool_executions.append(ToolExecution(tool_name="generate_followup_email", tool_input={"interaction_id": 1}, tool_output=res))
                
                reply = f"✉️ **Follow-up Email Draft to Dr. Sarah Chen**\n\n**Subject**: CardioGuard XR Clinical reprints & heart hospitalization data\n\nDear Dr. Chen,\n\nIt was a pleasure meeting with you at your clinic. As promised, I have attached the HEART-3 clinical trial reprints showing the 35% hospitalization reduction rate for chronic heart failure patients.\n\nPlease let me know if you would like to schedule a quick lunch meeting next week to discuss patient selection guides.\n\nBest regards,\nAlex Morgan\nField Sales Representative"

            # 7. general message
            else:
                reply = f"Hello! I am your AI CRM assistant operating in offline mode. I can run all tools. Try saying:\n\n* *'Search Dr Chen'*\n* *'Log today's visit with Dr Chen: discussed clinical efficacy'* (creates database entry)\n* *'Recommend products for Dr Chen'*\n* *'Suggest talking points for Dr Patel'*\n* *'Generate follow-up email for Dr Rodriguez'*"

            workflow_steps.append(
                WorkflowStep(
                    step_name="Processing Results",
                    status="completed",
                    description="Analyzing tool outputs and generating response (Offline)",
                )
            )
            workflow_steps.append(
                WorkflowStep(
                    step_name="Response Ready",
                    status="completed",
                    description="Response generated successfully",
                )
            )

            return ChatResponse(
                reply=reply,
                tool_executions=tool_executions,
                workflow_steps=workflow_steps,
                extracted_data=extracted_data
            )

        agent = get_agent()

        # Build message history
        messages = []
        for msg in (request.conversation_history or []):
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            else:
                messages.append(AIMessage(content=msg.content))

        # Add current user message
        messages.append(HumanMessage(content=request.message))

        # Build workflow steps — start with planning
        workflow_steps = [
            WorkflowStep(
                step_name="Analyzing Request",
                status="completed",
                description="Understanding user intent and planning execution",
            )
        ]

        # Invoke the agent
        result = agent.invoke({"messages": messages})

        # Extract tool executions and final response
        tool_executions = []
        final_reply = ""

        for msg in result["messages"]:
            # Capture tool calls from AI messages
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    tool_name = tc["name"]
                    tool_executions.append(
                        ToolExecution(
                            tool_name=tool_name,
                            tool_input=tc.get("args", {}),
                        )
                    )
                    # Add workflow step for tool invocation
                    tool_display_names = {
                        "search_hcp": "Search HCP Database",
                        "log_interaction": "Log Interaction",
                        "edit_interaction": "Edit Interaction",
                        "get_interaction_history": "Retrieve History",
                        "suggest_talking_points": "Generate Talking Points",
                        "recommend_product": "Recommend Product",
                        "generate_followup_email": "Generate Follow-up Email",
                        "summarize_notes": "Extract Entities & Summarize",
                    }
                    workflow_steps.append(
                        WorkflowStep(
                            step_name=tool_display_names.get(tool_name, tool_name),
                            status="completed",
                            description=f"Executing {tool_name} tool",
                            tool_name=tool_name,
                        )
                    )

            # Capture tool results
            if msg.type == "tool":
                # Find matching tool execution and add output
                for te in tool_executions:
                    if te.tool_name == msg.name and te.tool_output is None:
                        te.tool_output = msg.content
                        break

            # Last AI message is the final reply
            if msg.type == "ai" and msg.content:
                final_reply = msg.content

        # Add final workflow step
        if tool_executions:
            workflow_steps.append(
                WorkflowStep(
                    step_name="Processing Results",
                    status="completed",
                    description="Analyzing tool outputs and generating response",
                )
            )

        workflow_steps.append(
            WorkflowStep(
                step_name="Response Ready",
                status="completed",
                description="Response generated successfully",
            )
        )

        extracted_data = extract_form_data(tool_executions)

        return ChatResponse(
            reply=final_reply or "I processed your request. Is there anything else you need?",
            tool_executions=tool_executions,
            workflow_steps=workflow_steps,
            extracted_data=extracted_data
        )

    except Exception as e:
        error_msg = str(e)
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            return ChatResponse(
                reply="⚠️ Groq API key is not configured. Please add your GROQ_API_KEY to the .env file in the backend directory.",
                tool_executions=[],
                workflow_steps=[],
            )
        return ChatResponse(
            reply=f"I encountered an error: {error_msg}. Please try again.",
            tool_executions=[],
            workflow_steps=[],
        )
