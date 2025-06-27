"""
API endpoints for outcome tracking and verification
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.billing_model import OutcomeMetricSchema, OutcomeMetricCreate, OutcomeMetricUpdate
from app.services.billing_model.outcome_tracking import (
    record_outcome, verify_outcome, get_outcomes_for_billing, mark_outcomes_billed,
    get_outcome_metrics, calculate_outcome_statistics
)

router = APIRouter()


@router.post("/outcomes/record", response_model=OutcomeMetricSchema)
def record_agent_outcome(
    outcome_data: OutcomeMetricCreate,
    db: Session = Depends(deps.get_db)
):
    """
    Record an outcome for an agent
    """
    try:
        outcome_metric = record_outcome(
            db=db,
            agent_id=outcome_data.agent_id,
            outcome_value=outcome_data.outcome_value,
            outcome_currency=outcome_data.outcome_currency,
            outcome_data=outcome_data.outcome_data
        )
        return outcome_metric
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/outcomes/{outcome_id}/verify", response_model=OutcomeMetricSchema)
def verify_agent_outcome(
    outcome_id: int,
    verified_by: str,
    verification_status: str = "verified",
    verification_notes: Optional[str] = None,
    db: Session = Depends(deps.get_db)
):
    """
    Verify an outcome metric
    """
    try:
        outcome_metric = verify_outcome(
            db=db,
            outcome_metric_id=outcome_id,
            verified_by=verified_by,
            verification_status=verification_status,
            verification_notes=verification_notes
        )
        return outcome_metric
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/outcomes", response_model=List[OutcomeMetricSchema])
def list_outcome_metrics(
    agent_id: Optional[int] = Query(None),
    verification_status: Optional[str] = Query(None),
    billing_status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(deps.get_db)
):
    """
    List outcome metrics with filtering
    """
    return get_outcome_metrics(
        db=db,
        agent_id=agent_id,
        verification_status=verification_status,
        billing_status=billing_status,
        skip=skip,
        limit=limit
    )


@router.get("/outcomes/billing-ready", response_model=List[OutcomeMetricSchema])
def get_outcomes_ready_for_billing(
    agent_id: Optional[int] = Query(None),
    billing_period: Optional[str] = Query(None),
    db: Session = Depends(deps.get_db)
):
    """
    Get outcomes ready for billing
    """
    return get_outcomes_for_billing(
        db=db,
        agent_id=agent_id,
        billing_period=billing_period,
        billing_status="ready"
    )


@router.post("/outcomes/mark-billed")
def mark_outcomes_as_billed(
    outcome_ids: List[int],
    billing_period: str,
    db: Session = Depends(deps.get_db)
):
    """
    Mark outcomes as billed
    """
    updated_count = mark_outcomes_billed(
        db=db,
        outcome_metric_ids=outcome_ids,
        billing_period=billing_period
    )
    return {"updated_count": updated_count, "billing_period": billing_period}


@router.get("/outcomes/statistics")
def get_outcome_stats(
    agent_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(deps.get_db)
):
    """
    Get outcome statistics for reporting
    """
    return calculate_outcome_statistics(
        db=db,
        agent_id=agent_id,
        start_date=start_date,
        end_date=end_date
    )
