from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from collections import Counter
import datetime
from database import get_db
from models import Interaction, HCP, Product, interaction_products
from schemas import (
    InteractionCreate, InteractionUpdate, InteractionResponse, ProductResponse,
    DashboardStats
)

router = APIRouter(prefix="/api/interactions", tags=["Interactions"])


def _build_response(ix: Interaction) -> InteractionResponse:
    """Build interaction response with HCP name and products."""
    hcp_name = f"Dr. {ix.hcp.first_name} {ix.hcp.last_name}" if ix.hcp else None
    products = [ProductResponse.model_validate(p) for p in ix.products]
    resp = InteractionResponse.model_validate(ix)
    resp.hcp_name = hcp_name
    resp.products = products
    return resp


@router.get("/stats", response_model=DashboardStats)
def get_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics and AI insights."""
    hcps = db.query(HCP).all()
    interactions = db.query(Interaction).order_by(Interaction.interaction_date.desc()).all()

    # Basic counts
    total_hcps = len(hcps)
    total_interactions = len(interactions)
    positive_count = sum(1 for ix in interactions if ix.sentiment == "positive")
    sentiment_rate = round((positive_count / total_interactions * 100)) if total_interactions else 0
    followups = [ix for ix in interactions if ix.status == "follow_up_required"]

    # Interactions this week
    week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    interactions_this_week = sum(
        1 for ix in interactions
        if ix.interaction_date and ix.interaction_date >= week_ago
    )

    # Most discussed product
    product_counter = Counter()
    for ix in interactions:
        for p in ix.products:
            product_counter[p.name] += 1
    most_discussed = product_counter.most_common(1)[0][0] if product_counter else None

    # Most successful product (most positive sentiment)
    product_positive = Counter()
    for ix in interactions:
        if ix.sentiment == "positive":
            for p in ix.products:
                product_positive[p.name] += 1
    most_successful = product_positive.most_common(1)[0][0] if product_positive else None

    # Highest priority HCP (most interactions + tier A)
    hcp_priority = {}
    for ix in interactions:
        hcp_priority[ix.hcp_id] = hcp_priority.get(ix.hcp_id, 0) + 1
    highest_priority_hcp = None
    if hcp_priority:
        # Prefer tier A HCPs
        tier_a_hcps = {h.id for h in hcps if h.tier == "A"}
        priority_list = sorted(
            hcp_priority.items(),
            key=lambda x: (x[0] in tier_a_hcps, x[1]),
            reverse=True
        )
        top_hcp_id = priority_list[0][0]
        top_hcp = next((h for h in hcps if h.id == top_hcp_id), None)
        if top_hcp:
            highest_priority_hcp = f"Dr. {top_hcp.first_name} {top_hcp.last_name}"

    # Negative sentiment HCP
    negative_sentiment_hcp = None
    for ix in interactions:
        if ix.sentiment == "negative":
            hcp = next((h for h in hcps if h.id == ix.hcp_id), None)
            if hcp:
                negative_sentiment_hcp = f"Dr. {hcp.first_name} {hcp.last_name}"
                break

    # Sentiment trend
    recent = [ix for ix in interactions[:5] if ix.sentiment]
    older = [ix for ix in interactions[5:10] if ix.sentiment]
    recent_positive = sum(1 for ix in recent if ix.sentiment == "positive") / max(len(recent), 1)
    older_positive = sum(1 for ix in older if ix.sentiment == "positive") / max(len(older), 1)
    if recent_positive > older_positive + 0.1:
        sentiment_trend = "up"
    elif recent_positive < older_positive - 0.1:
        sentiment_trend = "down"
    else:
        sentiment_trend = "stable"

    # Recent AI activity
    recent_activity = []
    for ix in interactions[:6]:
        hcp = next((h for h in hcps if h.id == ix.hcp_id), None)
        hcp_name = f"Dr. {hcp.first_name} {hcp.last_name}" if hcp else "Unknown"
        activity_type = "Logged"
        if ix.ai_summary:
            activity_type = "Summarized"
        if ix.follow_up_actions:
            activity_type = "Follow-up Set"
        recent_activity.append({
            "type": activity_type,
            "hcp_name": hcp_name,
            "date": ix.interaction_date.isoformat() if ix.interaction_date else None,
            "interaction_type": ix.interaction_type,
            "sentiment": ix.sentiment,
        })

    return DashboardStats(
        total_hcps=total_hcps,
        total_interactions=total_interactions,
        positive_sentiment_rate=sentiment_rate,
        pending_followups=len(followups),
        most_discussed_product=most_discussed,
        highest_priority_hcp=highest_priority_hcp,
        negative_sentiment_hcp=negative_sentiment_hcp,
        doctors_needing_followup=len(followups),
        most_successful_product=most_successful,
        recent_ai_activity=recent_activity,
        interactions_this_week=interactions_this_week,
        sentiment_trend=sentiment_trend,
    )


@router.get("/", response_model=list[InteractionResponse])
def list_interactions(
    hcp_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    interaction_type: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(Interaction)
    if hcp_id:
        query = query.filter(Interaction.hcp_id == hcp_id)
    if status:
        query = query.filter(Interaction.status == status)
    if interaction_type:
        query = query.filter(Interaction.interaction_type == interaction_type)
    interactions = query.order_by(Interaction.interaction_date.desc()).limit(limit).all()
    return [_build_response(ix) for ix in interactions]


@router.get("/{interaction_id}", response_model=InteractionResponse)
def get_interaction(interaction_id: int, db: Session = Depends(get_db)):
    ix = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not ix:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return _build_response(ix)


@router.post("/", response_model=InteractionResponse, status_code=201)
def create_interaction(payload: InteractionCreate, db: Session = Depends(get_db)):
    # Verify HCP exists
    hcp = db.query(HCP).filter(HCP.id == payload.hcp_id).first()
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")

    data = payload.model_dump(exclude={"product_ids"})
    ix = Interaction(**data)
    db.add(ix)
    db.flush()

    # Associate products
    if payload.product_ids:
        for pid in payload.product_ids:
            product = db.query(Product).filter(Product.id == pid).first()
            if product:
                db.execute(
                    interaction_products.insert().values(
                        interaction_id=ix.id, product_id=pid
                    )
                )
    db.commit()
    db.refresh(ix)
    return _build_response(ix)


@router.put("/{interaction_id}", response_model=InteractionResponse)
def update_interaction(
    interaction_id: int, payload: InteractionUpdate, db: Session = Depends(get_db)
):
    ix = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not ix:
        raise HTTPException(status_code=404, detail="Interaction not found")

    update_data = payload.model_dump(exclude_unset=True, exclude={"product_ids"})
    for field, value in update_data.items():
        setattr(ix, field, value)

    # Update products if provided
    if payload.product_ids is not None:
        db.execute(
            interaction_products.delete().where(
                interaction_products.c.interaction_id == interaction_id
            )
        )
        for pid in payload.product_ids:
            db.execute(
                interaction_products.insert().values(
                    interaction_id=interaction_id, product_id=pid
                )
            )

    db.commit()
    db.refresh(ix)
    return _build_response(ix)


@router.delete("/{interaction_id}", status_code=204)
def delete_interaction(interaction_id: int, db: Session = Depends(get_db)):
    ix = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not ix:
        raise HTTPException(status_code=404, detail="Interaction not found")
    db.execute(
        interaction_products.delete().where(
            interaction_products.c.interaction_id == interaction_id
        )
    )
    db.delete(ix)
    db.commit()
