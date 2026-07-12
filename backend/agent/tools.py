"""Eight LangGraph tools for the HCP CRM AI agent.

Tools:
1. log_interaction     – Capture new interaction data with LLM summarization
2. edit_interaction    – Modify existing logged interactions
3. search_hcp          – Search HCP database by name/specialty/territory
4. get_interaction_history – Retrieve interaction timeline for an HCP
5. suggest_talking_points  – AI-generated personalized talking points
6. recommend_product   – AI-powered product recommendation for an HCP
7. generate_followup_email – Generate a follow-up email draft
8. summarize_notes     – Extract entities and generate structured summary
"""

import json
import datetime
from typing import Optional
from langchain_core.tools import tool
from sqlalchemy.orm import Session
from database import SessionLocal
from models import HCP, Interaction, Product, interaction_products


def _get_db() -> Session:
    return SessionLocal()


# ── Tool 1: Log Interaction ────────────────────────────────────────────────

@tool
def log_interaction(
    hcp_id: Optional[int] = None,
    hcp_name: Optional[str] = "",
    interaction_type: str = "face_to_face",
    raw_notes: str = "",
    channel: Optional[str] = "in_clinic",
    duration_minutes: Optional[int] = 15,
    rep_name: Optional[str] = "Field Rep",
    product_ids: Optional[str] = "",
    follow_up_actions: Optional[str] = "",
    follow_up_date: Optional[str] = "",
    status: Optional[str] = "completed",
    sentiment: Optional[str] = "neutral",
    brochures_shared: Optional[bool] = False,
) -> str:
    """Log a new interaction with a Healthcare Professional (HCP).

    Use this tool when the user wants to record a meeting, call, or any
    interaction with a doctor. Provide the hcp_id or hcp_name, interaction_type
    (face_to_face, virtual, phone, email, conference, lunch_meeting),
    and raw_notes describing what happened. The system will automatically
    generate an AI summary, extract key topics, and analyze sentiment.

    Args:
        hcp_id: The database ID of the HCP.
        hcp_name: The name of the HCP (e.g. Dr. John Smith). Used if hcp_id is not known.
        interaction_type: Type of interaction (face_to_face, virtual, phone, email, conference, lunch_meeting).
        raw_notes: Detailed free-text notes about the interaction.
        channel: Channel used (in_clinic, hospital, virtual_meeting, phone_call, email, conference, dinner_event).
        duration_minutes: Duration of the interaction in minutes.
        rep_name: Name of the sales representative.
        product_ids: Comma-separated product IDs discussed (e.g. "1,3").
        follow_up_actions: Actions to take after the interaction.
        follow_up_date: Follow-up date in YYYY-MM-DD format.
        status: Status (completed, scheduled, follow_up_required).
        sentiment: Sentiment of the interaction (positive, neutral, negative).
        brochures_shared: Whether brochures or promotional materials were shared.
    """
    db = _get_db()
    try:
        hcp = None
        if hcp_id:
            hcp = db.query(HCP).filter(HCP.id == hcp_id).first()
        
        if not hcp and hcp_name:
            # Look up by name
            clean_name = hcp_name.replace("Dr.", "").replace("Dr", "").replace("M.D.", "").strip()
            name_parts = clean_name.split()
            if len(name_parts) >= 2:
                first, last = name_parts[0], name_parts[-1]
                hcp = db.query(HCP).filter(
                    (HCP.first_name.ilike(f"%{first}%")) & (HCP.last_name.ilike(f"%{last}%"))
                ).first()
            if not hcp and len(name_parts) > 0:
                hcp = db.query(HCP).filter(HCP.last_name.ilike(f"%{name_parts[-1]}%")).first()
            
            # If still not found, create HCP dynamically
            if not hcp:
                first = name_parts[0] if len(name_parts) > 0 else "Unknown"
                last = " ".join(name_parts[1:]) if len(name_parts) > 1 else "Smith"
                hcp = HCP(
                    first_name=first,
                    last_name=last,
                    specialty="Cardiology",
                    institution="General Hospital",
                    tier="B"
                )
                db.add(hcp)
                db.flush()

        if not hcp:
            return json.dumps({"error": "HCP not found or could not be created. Please specify a name or ID."})

        # Set final hcp_id
        hcp_id = hcp.id

        follow_up_dt = None
        if follow_up_date:
            try:
                follow_up_dt = datetime.datetime.strptime(follow_up_date, "%Y-%m-%d")
            except ValueError:
                pass

        # Handle brochures shared in notes
        final_notes = raw_notes
        if brochures_shared:
            if not final_notes:
                final_notes = "Brochures were shared with the doctor."
            elif "brochure" not in final_notes.lower():
                final_notes += "\nNote: Brochures were shared."

        ix = Interaction(
            hcp_id=hcp_id,
            rep_name=rep_name or "Field Rep",
            interaction_type=interaction_type,
            channel=channel or "in_clinic",
            interaction_date=datetime.datetime.utcnow(),
            duration_minutes=duration_minutes or 15,
            raw_notes=final_notes,
            ai_summary="",  # Will be populated by the LLM in the agent response
            sentiment=sentiment or "neutral",
            key_topics="",
            follow_up_actions=follow_up_actions or "",
            follow_up_date=follow_up_dt,
            status=status or "completed",
        )
        db.add(ix)
        db.flush()

        # Associate products
        if product_ids:
            for pid_str in product_ids.split(","):
                pid_str = pid_str.strip()
                if pid_str.isdigit():
                    pid = int(pid_str)
                    prod = db.query(Product).filter(Product.id == pid).first()
                    if prod:
                        db.execute(
                            interaction_products.insert().values(
                                interaction_id=ix.id, product_id=pid
                            )
                        )

        db.commit()
        db.refresh(ix)

        return json.dumps({
            "success": True,
            "interaction_id": ix.id,
            "hcp_name": f"Dr. {hcp.first_name} {hcp.last_name}",
            "hcp_id": hcp.id,
            "interaction_type": interaction_type,
            "channel": channel,
            "duration_minutes": duration_minutes,
            "notes_preview": final_notes[:200],
            "status": status,
            "sentiment": sentiment,
            "brochures_shared": brochures_shared,
            "message": f"Interaction #{ix.id} logged successfully for Dr. {hcp.first_name} {hcp.last_name}.",
        })
    except Exception as e:
        db.rollback()
        return json.dumps({"error": str(e)})
    finally:
        db.close()


# ── Tool 2: Edit Interaction ────────────────────────────────────────────────

@tool
def edit_interaction(
    interaction_id: int,
    raw_notes: Optional[str] = "",
    interaction_type: Optional[str] = "",
    channel: Optional[str] = "",
    duration_minutes: Optional[int] = 0,
    follow_up_actions: Optional[str] = "",
    follow_up_date: Optional[str] = "",
    status: Optional[str] = "",
    product_ids: Optional[str] = "",
    hcp_name: Optional[str] = "",
    sentiment: Optional[str] = "",
    brochures_shared: Optional[bool] = None,
) -> str:
    """Edit / update an existing logged interaction.

    Use this tool when the user wants to modify a previously logged
    interaction. You need the interaction_id, and then provide whichever
    fields need to change. Only non-empty fields will be updated.

    Args:
        interaction_id: The ID of the interaction to edit.
        raw_notes: Updated notes (if changed).
        interaction_type: Updated type (if changed).
        channel: Updated channel (if changed).
        duration_minutes: Updated duration (if changed, 0 means no change).
        follow_up_actions: Updated follow-up actions (if changed).
        follow_up_date: Updated follow-up date in YYYY-MM-DD format (if changed).
        status: Updated status (if changed).
        product_ids: Updated comma-separated product IDs (if changed).
        hcp_name: Updated HCP name (if changed).
        sentiment: Updated sentiment (positive, neutral, negative).
        brochures_shared: Updated brochures shared status (true/false).
    """
    db = _get_db()
    try:
        ix = db.query(Interaction).filter(Interaction.id == interaction_id).first()
        if not ix:
            return json.dumps({"error": f"Interaction #{interaction_id} not found."})

        changes = []
        if raw_notes:
            ix.raw_notes = raw_notes
            ix.ai_summary = ""  # Clear for re-generation
            changes.append("notes")
        if interaction_type:
            ix.interaction_type = interaction_type
            changes.append("interaction_type")
        if channel:
            ix.channel = channel
            changes.append("channel")
        if duration_minutes and duration_minutes > 0:
            ix.duration_minutes = duration_minutes
            changes.append("duration")
        if follow_up_actions:
            ix.follow_up_actions = follow_up_actions
            changes.append("follow_up_actions")
        if follow_up_date:
            try:
                ix.follow_up_date = datetime.datetime.strptime(follow_up_date, "%Y-%m-%d")
                changes.append("follow_up_date")
            except ValueError:
                pass
        if status:
            ix.status = status
            changes.append("status")
        if sentiment:
            ix.sentiment = sentiment
            changes.append("sentiment")

        # Update associated HCP name if requested
        hcp = db.query(HCP).filter(HCP.id == ix.hcp_id).first()
        if hcp_name and hcp:
            clean_name = hcp_name.replace("Dr.", "").replace("Dr", "").replace("M.D.", "").strip()
            name_parts = clean_name.split()
            if len(name_parts) >= 2:
                hcp.first_name = name_parts[0]
                hcp.last_name = " ".join(name_parts[1:])
            elif len(name_parts) == 1:
                hcp.last_name = name_parts[0]
            changes.append("hcp_name")

        # Update brochures shared in notes/actions if requested
        if brochures_shared is not None:
            if brochures_shared:
                if not ix.raw_notes:
                    ix.raw_notes = "Brochures were shared."
                elif "brochure" not in ix.raw_notes.lower():
                    ix.raw_notes += "\nNote: Brochures were shared."
            changes.append("brochures_shared")

        # Update products if provided
        if product_ids:
            db.execute(
                interaction_products.delete().where(
                    interaction_products.c.interaction_id == interaction_id
                )
            )
            for pid_str in product_ids.split(","):
                pid_str = pid_str.strip()
                if pid_str.isdigit():
                    db.execute(
                        interaction_products.insert().values(
                            interaction_id=interaction_id, product_id=int(pid_str)
                        )
                    )
            changes.append("products")

        ix.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(ix)

        hcp_name_final = f"Dr. {hcp.first_name} {hcp.last_name}" if hcp else "Unknown"

        return json.dumps({
            "success": True,
            "interaction_id": ix.id,
            "hcp_name": hcp_name_final,
            "hcp_id": ix.hcp_id,
            "fields_updated": changes,
            "sentiment": ix.sentiment,
            "brochures_shared": brochures_shared if brochures_shared is not None else ("brochure" in ix.raw_notes.lower() if ix.raw_notes else False),
            "message": f"Interaction #{ix.id} updated successfully. Changed: {', '.join(changes)}.",
        })
    except Exception as e:
        db.rollback()
        return json.dumps({"error": str(e)})
    finally:
        db.close()


# ── Tool 3: Search HCP ─────────────────────────────────────────────────────

@tool
def search_hcp(
    query: str,
    specialty: Optional[str] = "",
    territory: Optional[str] = "",
) -> str:
    """Search the HCP (Healthcare Professional) database.

    Use this tool when the user mentions a doctor's name, asks to find
    an HCP, or needs to look up a healthcare professional before logging
    an interaction.

    Args:
        query: Search term — can be name, institution, or partial match.
        specialty: Filter by medical specialty (e.g. Cardiology, Oncology).
        territory: Filter by territory (e.g. Northeast, West).
    """
    db = _get_db()
    try:
        q = db.query(HCP)
        if query:
            pattern = f"%{query}%"
            q = q.filter(
                (HCP.first_name.ilike(pattern))
                | (HCP.last_name.ilike(pattern))
                | (HCP.institution.ilike(pattern))
                | (HCP.npi_number.ilike(pattern))
            )
        if specialty:
            q = q.filter(HCP.specialty.ilike(f"%{specialty}%"))
        if territory:
            q = q.filter(HCP.territory.ilike(f"%{territory}%"))

        hcps = q.limit(10).all()
        if not hcps:
            return json.dumps({"results": [], "message": "No HCPs found matching your search criteria."})

        results = []
        for hcp in hcps:
            results.append({
                "id": hcp.id,
                "name": f"Dr. {hcp.first_name} {hcp.last_name}",
                "specialty": hcp.specialty,
                "institution": hcp.institution,
                "territory": hcp.territory,
                "city": hcp.city,
                "state": hcp.state,
                "tier": hcp.tier,
                "interaction_count": len(hcp.interactions),
            })

        return json.dumps({
            "results": results,
            "count": len(results),
            "message": f"Found {len(results)} HCP(s) matching '{query}'.",
        })
    finally:
        db.close()


# ── Tool 4: Get Interaction History ─────────────────────────────────────────

@tool
def get_interaction_history(
    hcp_id: Optional[int] = 0,
    limit: Optional[int] = 10,
    interaction_type: Optional[str] = "",
) -> str:
    """Retrieve the interaction history for a specific HCP or all recent interactions.

    Use this tool when the user asks about past interactions, meeting
    history, or wants to review previous conversations with a doctor.

    Args:
        hcp_id: The HCP's database ID. Use 0 or omit for all HCPs.
        limit: Maximum number of interactions to return (default 10).
        interaction_type: Filter by type (face_to_face, virtual, phone, email).
    """
    db = _get_db()
    try:
        q = db.query(Interaction)
        if hcp_id and hcp_id > 0:
            q = q.filter(Interaction.hcp_id == hcp_id)
        if interaction_type:
            q = q.filter(Interaction.interaction_type == interaction_type)

        interactions = q.order_by(Interaction.interaction_date.desc()).limit(limit or 10).all()

        if not interactions:
            return json.dumps({"interactions": [], "message": "No interactions found."})

        results = []
        for ix in interactions:
            hcp = db.query(HCP).filter(HCP.id == ix.hcp_id).first()
            hcp_name = f"Dr. {hcp.first_name} {hcp.last_name}" if hcp else "Unknown"
            products = [p.name for p in ix.products]
            results.append({
                "id": ix.id,
                "hcp_name": hcp_name,
                "hcp_id": ix.hcp_id,
                "type": ix.interaction_type,
                "channel": ix.channel,
                "date": ix.interaction_date.isoformat() if ix.interaction_date else None,
                "duration_minutes": ix.duration_minutes,
                "summary": ix.ai_summary or ix.raw_notes[:150] if ix.raw_notes else "",
                "sentiment": ix.sentiment,
                "key_topics": ix.key_topics,
                "products_discussed": products,
                "follow_up": ix.follow_up_actions,
                "status": ix.status,
            })

        return json.dumps({
            "interactions": results,
            "count": len(results),
            "message": f"Found {len(results)} interaction(s).",
        })
    finally:
        db.close()


# ── Tool 5: Suggest Talking Points ──────────────────────────────────────────

@tool
def suggest_talking_points(
    hcp_id: int,
    product_id: Optional[int] = 0,
) -> str:
    """Generate personalized talking points for an upcoming meeting with an HCP.

    Use this tool when the user wants preparation tips, discussion
    points, or suggestions for what to talk about with a specific
    doctor. It considers the HCP's specialty, past interactions, and
    product information.

    Args:
        hcp_id: The HCP's database ID.
        product_id: Optional product ID to focus talking points on (0 for general).
    """
    db = _get_db()
    try:
        hcp = db.query(HCP).filter(HCP.id == hcp_id).first()
        if not hcp:
            return json.dumps({"error": f"HCP with id {hcp_id} not found."})

        # Gather context
        recent_interactions = (
            db.query(Interaction)
            .filter(Interaction.hcp_id == hcp_id)
            .order_by(Interaction.interaction_date.desc())
            .limit(5)
            .all()
        )

        interaction_context = []
        for ix in recent_interactions:
            interaction_context.append({
                "date": ix.interaction_date.isoformat() if ix.interaction_date else "N/A",
                "type": ix.interaction_type,
                "summary": ix.ai_summary or (ix.raw_notes[:200] if ix.raw_notes else ""),
                "sentiment": ix.sentiment,
                "follow_up": ix.follow_up_actions,
                "products": [p.name for p in ix.products],
            })

        product_context = None
        if product_id and product_id > 0:
            product = db.query(Product).filter(Product.id == product_id).first()
            if product:
                product_context = {
                    "name": product.name,
                    "category": product.category,
                    "description": product.description,
                    "key_messages": product.key_messages,
                    "therapeutic_area": product.therapeutic_area,
                }

        # Build context for LLM to use in its response
        context = {
            "hcp": {
                "name": f"Dr. {hcp.first_name} {hcp.last_name}",
                "specialty": hcp.specialty,
                "institution": hcp.institution,
                "territory": hcp.territory,
                "tier": hcp.tier,
                "city": hcp.city,
            },
            "recent_interactions": interaction_context,
            "product_focus": product_context,
            "total_past_interactions": len(recent_interactions),
        }

        return json.dumps({
            "context": context,
            "message": (
                f"Here is the context for preparing talking points for "
                f"Dr. {hcp.first_name} {hcp.last_name} ({hcp.specialty}). "
                f"They have {len(recent_interactions)} recent interaction(s) on record. "
                f"Use this context to generate personalized talking points."
            ),
        })
    finally:
        db.close()


# ── Tool 6: Recommend Product ──────────────────────────────────────────────

@tool
def recommend_product(
    hcp_id: int,
) -> str:
    """Recommend the best product to discuss with a specific HCP.

    Use this tool when the user asks for product recommendations for a
    doctor. It analyzes the HCP's specialty, past interactions, previously
    discussed products, and sentiment to suggest the most relevant product
    with a reasoning explanation.

    Args:
        hcp_id: The HCP's database ID.
    """
    db = _get_db()
    try:
        hcp = db.query(HCP).filter(HCP.id == hcp_id).first()
        if not hcp:
            return json.dumps({"error": f"HCP with id {hcp_id} not found."})

        # Get all products
        all_products = db.query(Product).all()

        # Get past interactions
        past_interactions = (
            db.query(Interaction)
            .filter(Interaction.hcp_id == hcp_id)
            .order_by(Interaction.interaction_date.desc())
            .limit(10)
            .all()
        )

        # Analyze previously discussed products
        discussed_products = {}
        sentiments = {}
        for ix in past_interactions:
            for p in ix.products:
                discussed_products[p.id] = discussed_products.get(p.id, 0) + 1
                if ix.sentiment:
                    if p.id not in sentiments:
                        sentiments[p.id] = []
                    sentiments[p.id].append(ix.sentiment)

        # Build product catalog context
        product_catalog = []
        for p in all_products:
            product_catalog.append({
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "therapeutic_area": p.therapeutic_area,
                "description": p.description,
                "key_messages": p.key_messages,
                "times_discussed": discussed_products.get(p.id, 0),
                "past_sentiments": sentiments.get(p.id, []),
            })

        context = {
            "hcp": {
                "name": f"Dr. {hcp.first_name} {hcp.last_name}",
                "specialty": hcp.specialty,
                "institution": hcp.institution,
                "tier": hcp.tier,
                "territory": hcp.territory,
            },
            "product_catalog": product_catalog,
            "total_past_interactions": len(past_interactions),
        }

        return json.dumps({
            "context": context,
            "message": (
                f"Here is the HCP profile and full product catalog for "
                f"Dr. {hcp.first_name} {hcp.last_name} ({hcp.specialty}). "
                f"Based on their specialty, interaction history, and product alignment, "
                f"recommend the best product with reasoning and a confidence score."
            ),
        })
    finally:
        db.close()


# ── Tool 7: Generate Follow-up Email ───────────────────────────────────────

@tool
def generate_followup_email(
    interaction_id: int,
    rep_name: Optional[str] = "Alex Morgan",
) -> str:
    """Generate a professional follow-up email after an HCP interaction.

    Use this tool when the user wants to create a follow-up email for
    a doctor after a meeting. It uses the interaction details, discussed
    topics, products, and follow-up actions to craft a personalized email.

    Args:
        interaction_id: The ID of the interaction to generate follow-up for.
        rep_name: Name of the sales representative sending the email.
    """
    db = _get_db()
    try:
        ix = db.query(Interaction).filter(Interaction.id == interaction_id).first()
        if not ix:
            return json.dumps({"error": f"Interaction #{interaction_id} not found."})

        hcp = db.query(HCP).filter(HCP.id == ix.hcp_id).first()
        hcp_name = f"Dr. {hcp.first_name} {hcp.last_name}" if hcp else "Doctor"

        products = [{"name": p.name, "description": p.description, "key_messages": p.key_messages} for p in ix.products]

        context = {
            "hcp_name": hcp_name,
            "hcp_specialty": hcp.specialty if hcp else "",
            "hcp_institution": hcp.institution if hcp else "",
            "interaction_type": ix.interaction_type,
            "interaction_date": ix.interaction_date.strftime("%B %d, %Y") if ix.interaction_date else "recently",
            "raw_notes": ix.raw_notes,
            "ai_summary": ix.ai_summary,
            "products_discussed": products,
            "follow_up_actions": ix.follow_up_actions,
            "sentiment": ix.sentiment,
            "rep_name": rep_name,
        }

        return json.dumps({
            "context": context,
            "message": (
                f"Here is the interaction context for generating a follow-up email to "
                f"{hcp_name}. The meeting was {ix.interaction_type.replace('_', ' ')} "
                f"on {context['interaction_date']}. Use this to write a professional, "
                f"personalized follow-up email."
            ),
        })
    finally:
        db.close()


# ── Tool 8: Summarize Notes ────────────────────────────────────────────────

@tool
def summarize_notes(
    raw_notes: str,
    hcp_id: Optional[int] = 0,
) -> str:
    """Extract entities and generate a structured summary from raw interaction notes.

    Use this tool when the user provides raw notes and wants them
    analyzed. It provides context for the LLM to extract entities
    (doctors, products, diseases, competitors, sentiment) and generate
    a structured summary with key topics and action items.

    Args:
        raw_notes: The raw text notes to analyze and summarize.
        hcp_id: Optional HCP ID for additional context (0 if unknown).
    """
    db = _get_db()
    try:
        hcp_context = None
        if hcp_id and hcp_id > 0:
            hcp = db.query(HCP).filter(HCP.id == hcp_id).first()
            if hcp:
                hcp_context = {
                    "name": f"Dr. {hcp.first_name} {hcp.last_name}",
                    "specialty": hcp.specialty,
                    "institution": hcp.institution,
                }

        # Get product names for entity matching
        all_products = db.query(Product).all()
        product_names = [p.name for p in all_products]

        context = {
            "raw_notes": raw_notes,
            "hcp_context": hcp_context,
            "known_products": product_names,
        }

        return json.dumps({
            "context": context,
            "message": (
                f"Analyze the following raw notes and extract structured information. "
                f"Known products in our catalog: {', '.join(product_names)}. "
                f"Extract: doctors mentioned, products discussed, diseases/conditions, "
                f"competitor mentions, overall sentiment (positive/neutral/negative), "
                f"key topics, action items, and generate a concise summary."
            ),
        })
    finally:
        db.close()


# Export all tools as a list
ALL_TOOLS = [
    log_interaction,
    edit_interaction,
    search_hcp,
    get_interaction_history,
    suggest_talking_points,
    recommend_product,
    generate_followup_email,
    summarize_notes,
]
