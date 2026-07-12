"""Seed the database with sample HCPs, products, and interactions for demo."""
import json
import datetime
from sqlalchemy.orm import Session
from backend.models import HCP, Product, Interaction, interaction_products


SAMPLE_HCPS = [
    {
        "first_name": "Sarah",
        "last_name": "Chen",
        "specialty": "Cardiology",
        "institution": "Metro Heart Institute",
        "email": "s.chen@metroheart.com",
        "phone": "+1-555-0101",
        "npi_number": "NPI1234567890",
        "territory": "Northeast",
        "city": "Boston",
        "state": "Massachusetts",
        "tier": "A",
    },
    {
        "first_name": "James",
        "last_name": "Rodriguez",
        "specialty": "Oncology",
        "institution": "Pacific Cancer Center",
        "email": "j.rodriguez@pacificcancer.org",
        "phone": "+1-555-0102",
        "npi_number": "NPI2345678901",
        "territory": "West",
        "city": "San Francisco",
        "state": "California",
        "tier": "A",
    },
    {
        "first_name": "Emily",
        "last_name": "Patel",
        "specialty": "Endocrinology",
        "institution": "Sunrise Medical Group",
        "email": "e.patel@sunrisemed.com",
        "phone": "+1-555-0103",
        "npi_number": "NPI3456789012",
        "territory": "South",
        "city": "Houston",
        "state": "Texas",
        "tier": "B",
    },
    {
        "first_name": "Michael",
        "last_name": "Okonkwo",
        "specialty": "Neurology",
        "institution": "Lakeside Neuro Clinic",
        "email": "m.okonkwo@lakesideneuro.com",
        "phone": "+1-555-0104",
        "npi_number": "NPI4567890123",
        "territory": "Midwest",
        "city": "Chicago",
        "state": "Illinois",
        "tier": "B",
    },
    {
        "first_name": "Aisha",
        "last_name": "Khan",
        "specialty": "Rheumatology",
        "institution": "Valley Health System",
        "email": "a.khan@valleyhealth.org",
        "phone": "+1-555-0105",
        "npi_number": "NPI5678901234",
        "territory": "Northeast",
        "city": "New York",
        "state": "New York",
        "tier": "A",
    },
    {
        "first_name": "David",
        "last_name": "Thompson",
        "specialty": "Pulmonology",
        "institution": "Central Lung Center",
        "email": "d.thompson@centrallc.com",
        "phone": "+1-555-0106",
        "npi_number": "NPI6789012345",
        "territory": "South",
        "city": "Atlanta",
        "state": "Georgia",
        "tier": "C",
    },
]

SAMPLE_PRODUCTS = [
    {
        "name": "CardioGuard XR",
        "category": "Cardiovascular",
        "description": "Extended-release cardiovascular medication for chronic heart failure management.",
        "key_messages": json.dumps([
            "35% reduction in hospitalization rates",
            "Once-daily dosing for improved compliance",
            "Favorable safety profile in elderly patients",
        ]),
        "therapeutic_area": "Cardiology",
    },
    {
        "name": "OncoVita Plus",
        "category": "Oncology",
        "description": "Targeted therapy for advanced non-small cell lung cancer.",
        "key_messages": json.dumps([
            "Improved PFS by 8.2 months vs standard of care",
            "Oral administration — no infusion required",
            "Companion diagnostic available",
        ]),
        "therapeutic_area": "Oncology",
    },
    {
        "name": "NeuroCalm SR",
        "category": "Neurology",
        "description": "Sustained-release treatment for epilepsy and neuropathic pain.",
        "key_messages": json.dumps([
            "Dual mechanism of action",
            "Reduced seizure frequency by 52%",
            "Minimal cognitive side effects",
        ]),
        "therapeutic_area": "Neurology",
    },
    {
        "name": "GlucoBalance Pro",
        "category": "Endocrinology",
        "description": "Next-generation GLP-1 receptor agonist for Type 2 diabetes.",
        "key_messages": json.dumps([
            "A1C reduction of 1.8% in clinical trials",
            "Weekly injection for patient convenience",
            "Cardiovascular risk reduction benefit",
        ]),
        "therapeutic_area": "Endocrinology",
    },
    {
        "name": "ImmunoFlex RA",
        "category": "Immunology",
        "description": "Biologic therapy for moderate-to-severe rheumatoid arthritis.",
        "key_messages": json.dumps([
            "Rapid symptom relief within 2 weeks",
            "Self-injectable pen for home use",
            "Long-term joint protection demonstrated",
        ]),
        "therapeutic_area": "Rheumatology",
    },
]

SAMPLE_INTERACTIONS = [
    {
        "hcp_idx": 0,
        "rep_name": "Alex Morgan",
        "interaction_type": "face_to_face",
        "channel": "in_clinic",
        "duration_minutes": 25,
        "raw_notes": "Met with Dr. Chen at her clinic. Discussed CardioGuard XR efficacy data from the HEART-3 trial. She expressed strong interest in the hospitalization reduction data. She has 3 patients she is considering switching. Needs more info on drug-drug interactions with warfarin. Follow up next week with clinical paper.",
        "ai_summary": "Productive in-clinic meeting with Dr. Chen regarding CardioGuard XR. High interest in HEART-3 trial hospitalization data. Considering switching 3 patients. Requested drug-drug interaction data with warfarin.",
        "sentiment": "positive",
        "key_topics": json.dumps(["CardioGuard XR", "HEART-3 trial", "hospitalization reduction", "warfarin interactions"]),
        "follow_up_actions": "Send HEART-3 reprint and warfarin interaction study",
        "follow_up_date_offset": 7,
        "status": "follow_up_required",
        "product_idxs": [0],
        "days_ago": 2,
    },
    {
        "hcp_idx": 1,
        "rep_name": "Alex Morgan",
        "interaction_type": "virtual",
        "channel": "virtual_meeting",
        "duration_minutes": 30,
        "raw_notes": "Virtual meeting with Dr. Rodriguez about OncoVita Plus. Reviewed updated PFS data and the companion diagnostic process. He is already prescribing for 5 patients and reported good tolerance. Asked about expanded access for a rare mutation subgroup.",
        "ai_summary": "Virtual meeting with Dr. Rodriguez. Already prescribing OncoVita Plus for 5 patients with good outcomes. Interested in expanded access for rare mutation subgroup patients.",
        "sentiment": "positive",
        "key_topics": json.dumps(["OncoVita Plus", "PFS data", "companion diagnostic", "expanded access"]),
        "follow_up_actions": "Check with medical affairs about expanded access program",
        "follow_up_date_offset": 5,
        "status": "follow_up_required",
        "product_idxs": [1],
        "days_ago": 5,
    },
    {
        "hcp_idx": 2,
        "rep_name": "Alex Morgan",
        "interaction_type": "phone",
        "channel": "phone_call",
        "duration_minutes": 15,
        "raw_notes": "Quick phone call with Dr. Patel about GlucoBalance Pro samples. She mentioned her patients like the weekly dosing but some experienced mild GI side effects in the first week. Wants to know if titration helps.",
        "ai_summary": "Phone check-in with Dr. Patel regarding GlucoBalance Pro. Patients positive about weekly dosing. Some mild GI side effects reported. Inquiry about titration protocol.",
        "sentiment": "neutral",
        "key_topics": json.dumps(["GlucoBalance Pro", "GI side effects", "weekly dosing", "titration"]),
        "follow_up_actions": "Send titration guide and GI management tips",
        "follow_up_date_offset": 3,
        "status": "completed",
        "product_idxs": [3],
        "days_ago": 1,
    },
    {
        "hcp_idx": 4,
        "rep_name": "Alex Morgan",
        "interaction_type": "face_to_face",
        "channel": "hospital",
        "duration_minutes": 20,
        "raw_notes": "Visited Dr. Khan at Valley Health. Presented ImmunoFlex RA data. She was concerned about infection risk in her immunocompromised patients. Not ready to switch from current biologic. Needs to see more long-term safety data.",
        "ai_summary": "Meeting with Dr. Khan about ImmunoFlex RA. Concerns about infection risk in immunocompromised patients. Not ready to switch. Requires long-term safety data before consideration.",
        "sentiment": "negative",
        "key_topics": json.dumps(["ImmunoFlex RA", "infection risk", "immunocompromised patients", "long-term safety"]),
        "follow_up_actions": "Prepare long-term safety data compilation",
        "follow_up_date_offset": 10,
        "status": "follow_up_required",
        "product_idxs": [4],
        "days_ago": 4,
    },
    {
        "hcp_idx": 3,
        "rep_name": "Alex Morgan",
        "interaction_type": "conference",
        "channel": "conference",
        "duration_minutes": 45,
        "raw_notes": "Met Dr. Okonkwo at the American Neurology Conference. He attended our NeuroCalm SR symposium and was impressed by the seizure frequency reduction data. Discussed potential for his epilepsy patients who are not well-controlled on current medication. He wants to review the Phase 3 data in detail. Also mentioned competitor drug BrainShield from NeuroPharm is being promoted heavily in his territory.",
        "ai_summary": "Conference meeting with Dr. Okonkwo at ANC. Impressed by NeuroCalm SR seizure data. Potential for uncontrolled epilepsy patients. Competitor awareness: BrainShield (NeuroPharm) being promoted in Midwest.",
        "sentiment": "positive",
        "key_topics": json.dumps(["NeuroCalm SR", "seizure frequency", "epilepsy", "Phase 3 data", "BrainShield competitor"]),
        "follow_up_actions": "Send Phase 3 trial publication and competitive positioning deck",
        "follow_up_date_offset": 14,
        "status": "follow_up_required",
        "product_idxs": [2],
        "days_ago": 6,
    },
    {
        "hcp_idx": 0,
        "rep_name": "Alex Morgan",
        "interaction_type": "email",
        "channel": "email",
        "duration_minutes": 5,
        "raw_notes": "Sent follow-up email to Dr. Chen with the HEART-3 reprint as discussed. She replied thanking us and mentioned she already started one patient on CardioGuard XR. She wants to schedule a lunch meeting to discuss the remaining patients.",
        "ai_summary": "Email follow-up with Dr. Chen. She has started 1 patient on CardioGuard XR. Wants to schedule lunch meeting for further discussion. Very positive engagement.",
        "sentiment": "positive",
        "key_topics": json.dumps(["CardioGuard XR", "HEART-3 reprint", "patient started", "lunch meeting"]),
        "follow_up_actions": "Schedule lunch meeting with Dr. Chen next week",
        "follow_up_date_offset": 5,
        "status": "follow_up_required",
        "product_idxs": [0],
        "days_ago": 1,
    },
    {
        "hcp_idx": 5,
        "rep_name": "Alex Morgan",
        "interaction_type": "phone",
        "channel": "phone_call",
        "duration_minutes": 10,
        "raw_notes": "Called Dr. Thompson at Central Lung Center. He was busy and only had 10 minutes. Briefly discussed CardioGuard XR's cardiovascular benefits for his COPD patients with heart failure comorbidity. He seemed skeptical about off-label use. Suggested he attend the upcoming webinar on cardio-pulmonary benefits.",
        "ai_summary": "Brief phone call with Dr. Thompson. Discussed CardioGuard XR for COPD+HF comorbidity. Skeptical about approach. Recommended upcoming webinar attendance.",
        "sentiment": "neutral",
        "key_topics": json.dumps(["CardioGuard XR", "COPD", "heart failure comorbidity", "webinar"]),
        "follow_up_actions": "Send webinar invitation for cardio-pulmonary benefits session",
        "follow_up_date_offset": 3,
        "status": "completed",
        "product_idxs": [0],
        "days_ago": 3,
    },
    {
        "hcp_idx": 2,
        "rep_name": "Alex Morgan",
        "interaction_type": "lunch_meeting",
        "channel": "dinner_event",
        "duration_minutes": 60,
        "raw_notes": "Lunch meeting with Dr. Patel. She shared positive feedback from patients on GlucoBalance Pro — one patient achieved A1C of 6.5% after 3 months. She's now her go-to for new T2D patients. Discussed potential to combine with CardioGuard XR for patients with T2D and HF. She's interested in the cardiovascular risk reduction data.",
        "ai_summary": "Excellent lunch meeting with Dr. Patel. Strong advocate for GlucoBalance Pro — patient achieved A1C 6.5%. Interested in combination with CardioGuard XR for T2D+HF patients. High conversion.",
        "sentiment": "positive",
        "key_topics": json.dumps(["GlucoBalance Pro", "A1C results", "Type 2 Diabetes", "CardioGuard XR combination", "cardiovascular risk"]),
        "follow_up_actions": "Send cardiovascular risk reduction study for GlucoBalance Pro",
        "follow_up_date_offset": 7,
        "status": "completed",
        "product_idxs": [3, 0],
        "days_ago": 0,
    },
]


def seed_database(db: Session):
    """Populate the database with sample data if tables are empty."""
    if db.query(HCP).count() > 0:
        return  # Already seeded

    # Seed HCPs
    hcp_objects = []
    for hcp_data in SAMPLE_HCPS:
        hcp = HCP(**hcp_data)
        db.add(hcp)
        hcp_objects.append(hcp)
    db.flush()

    # Seed Products
    product_objects = []
    for prod_data in SAMPLE_PRODUCTS:
        product = Product(**prod_data)
        db.add(product)
        product_objects.append(product)
    db.flush()

    # Seed Interactions
    for ix_data in SAMPLE_INTERACTIONS:
        hcp = hcp_objects[ix_data["hcp_idx"]]

        follow_up_dt = None
        if ix_data.get("follow_up_date_offset"):
            follow_up_dt = datetime.datetime.utcnow() + datetime.timedelta(days=ix_data["follow_up_date_offset"])

        ix = Interaction(
            hcp_id=hcp.id,
            rep_name=ix_data["rep_name"],
            interaction_type=ix_data["interaction_type"],
            channel=ix_data["channel"],
            duration_minutes=ix_data["duration_minutes"],
            raw_notes=ix_data["raw_notes"],
            ai_summary=ix_data["ai_summary"],
            sentiment=ix_data["sentiment"],
            key_topics=ix_data["key_topics"],
            follow_up_actions=ix_data["follow_up_actions"],
            follow_up_date=follow_up_dt,
            status=ix_data["status"],
            interaction_date=datetime.datetime.utcnow() - datetime.timedelta(days=ix_data["days_ago"]),
        )
        db.add(ix)
        db.flush()
        # Associate products
        for pidx in ix_data["product_idxs"]:
            db.execute(
                interaction_products.insert().values(
                    interaction_id=ix.id, product_id=product_objects[pidx].id
                )
            )

    db.commit()
