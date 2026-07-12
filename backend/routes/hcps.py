from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from collections import Counter
from database import get_db
from models import HCP, Interaction, Product
from schemas import HCPCreate, HCPUpdate, HCPResponse, HCPInsights

router = APIRouter(prefix="/api/hcps", tags=["HCPs"])


@router.get("/", response_model=list[HCPResponse])
def list_hcps(
    search: Optional[str] = Query(None),
    specialty: Optional[str] = Query(None),
    territory: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(HCP)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (HCP.first_name.ilike(pattern))
            | (HCP.last_name.ilike(pattern))
            | (HCP.institution.ilike(pattern))
        )
    if specialty:
        query = query.filter(HCP.specialty.ilike(f"%{specialty}%"))
    if territory:
        query = query.filter(HCP.territory.ilike(f"%{territory}%"))

    hcps = query.all()
    results = []
    for hcp in hcps:
        resp = HCPResponse.model_validate(hcp)
        resp.interaction_count = len(hcp.interactions)
        results.append(resp)
    return results


@router.get("/{hcp_id}", response_model=HCPResponse)
def get_hcp(hcp_id: int, db: Session = Depends(get_db)):
    hcp = db.query(HCP).filter(HCP.id == hcp_id).first()
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")
    resp = HCPResponse.model_validate(hcp)
    resp.interaction_count = len(hcp.interactions)
    return resp


@router.get("/{hcp_id}/insights", response_model=HCPInsights)
def get_hcp_insights(hcp_id: int, db: Session = Depends(get_db)):
    """Get AI-generated insights for a specific HCP."""
    hcp = db.query(HCP).filter(HCP.id == hcp_id).first()
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")

    hcp_name = f"Dr. {hcp.first_name} {hcp.last_name}"
    interactions = (
        db.query(Interaction)
        .filter(Interaction.hcp_id == hcp_id)
        .order_by(Interaction.interaction_date.desc())
        .all()
    )

    # Interested products
    product_counter = Counter()
    for ix in interactions:
        for p in ix.products:
            product_counter[p.name] += 1
    interested_products = [name for name, _ in product_counter.most_common(5)]

    # Communication style based on interaction types
    type_counter = Counter(ix.interaction_type for ix in interactions)
    preferred_type = type_counter.most_common(1)[0][0] if type_counter else None
    style_map = {
        "face_to_face": "Prefers in-person meetings",
        "virtual": "Comfortable with virtual meetings",
        "phone": "Prefers quick phone calls",
        "email": "Prefers email communication",
        "conference": "Engages at conferences",
        "lunch_meeting": "Appreciates informal settings",
    }
    communication_style = style_map.get(preferred_type, "No preference detected")
    preferred_meeting = preferred_type.replace("_", " ").title() if preferred_type else None

    # Last meeting summary
    last_meeting_summary = None
    if interactions:
        last_ix = interactions[0]
        last_meeting_summary = last_ix.ai_summary or (last_ix.raw_notes[:200] if last_ix.raw_notes else None)

    # Sentiment analysis
    sentiments = [ix.sentiment for ix in interactions if ix.sentiment]
    positive = sentiments.count("positive")
    negative = sentiments.count("negative")
    total_s = len(sentiments) or 1
    avg_sentiment = "positive" if positive / total_s > 0.5 else ("negative" if negative / total_s > 0.5 else "neutral")

    # Conversion probability (based on tier, sentiment, interaction count)
    base_prob = {"A": 75, "B": 50, "C": 25}.get(hcp.tier, 40)
    sentiment_bonus = (positive - negative) * 5
    interaction_bonus = min(len(interactions) * 3, 15)
    conversion_probability = max(0, min(100, base_prob + sentiment_bonus + interaction_bonus))

    # Recommended product (best match for specialty)
    all_products = db.query(Product).all()
    specialty_map = {
        "Cardiology": "CardioGuard XR",
        "Oncology": "OncoVita Plus",
        "Neurology": "NeuroCalm SR",
        "Endocrinology": "GlucoBalance Pro",
        "Rheumatology": "ImmunoFlex RA",
    }
    recommended = specialty_map.get(hcp.specialty)
    reason = f"Aligns with {hcp.specialty} specialty"
    if interested_products:
        recommended = interested_products[0]
        reason = f"Most discussed in past {len(interactions)} interactions"

    # Pending actions
    pending_actions = []
    for ix in interactions:
        if ix.status == "follow_up_required" and ix.follow_up_actions:
            pending_actions.append(ix.follow_up_actions)

    return HCPInsights(
        hcp_id=hcp.id,
        hcp_name=hcp_name,
        interested_products=interested_products,
        communication_style=communication_style,
        last_meeting_summary=last_meeting_summary,
        preferred_meeting_type=preferred_meeting,
        conversion_probability=conversion_probability,
        recommended_product=recommended,
        recommended_product_reason=reason,
        pending_actions=pending_actions[:3],
        total_interactions=len(interactions),
        avg_sentiment=avg_sentiment,
    )


@router.post("/", response_model=HCPResponse, status_code=201)
def create_hcp(payload: HCPCreate, db: Session = Depends(get_db)):
    hcp = HCP(**payload.model_dump())
    db.add(hcp)
    db.commit()
    db.refresh(hcp)
    return HCPResponse.model_validate(hcp)


@router.put("/{hcp_id}", response_model=HCPResponse)
def update_hcp(hcp_id: int, payload: HCPUpdate, db: Session = Depends(get_db)):
    hcp = db.query(HCP).filter(HCP.id == hcp_id).first()
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(hcp, field, value)
    db.commit()
    db.refresh(hcp)
    resp = HCPResponse.model_validate(hcp)
    resp.interaction_count = len(hcp.interactions)
    return resp


@router.delete("/{hcp_id}", status_code=204)
def delete_hcp(hcp_id: int, db: Session = Depends(get_db)):
    hcp = db.query(HCP).filter(HCP.id == hcp_id).first()
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")
    db.delete(hcp)
    db.commit()
