"""
Outcome tracking and verification service for sophisticated outcome-based pricing
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.billing_model import BillingModel, OutcomeBasedConfig, OutcomeMetric, OutcomeVerificationRule
from app.models.agent import Agent
from app.schemas.billing_model import OutcomeMetricCreate, OutcomeMetricUpdate
from .calculation import calculate_cost
import logging
import json

logger = logging.getLogger(__name__)


def record_outcome(
    db: Session, 
    agent_id: int, 
    outcome_value: float, 
    outcome_currency: str = "USD",
    outcome_data: Optional[Dict[str, Any]] = None,
    verification_required: Optional[bool] = None
) -> OutcomeMetric:
    """
    Record an outcome for an agent and calculate billing
    """
    # Get agent and billing model
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise ValueError(f"Agent with ID {agent_id} not found")
    
    if agent.billing_model_id is None:
        raise ValueError(f"Agent {agent_id} has no billing model assigned")
    
    billing_model = db.query(BillingModel).filter(BillingModel.id == agent.billing_model_id).first()
    if not billing_model:
        raise ValueError(f"Billing model not found for agent {agent_id}")
    
    # Find the outcome config
    outcome_configs = billing_model.outcome_config
    if not outcome_configs:
        raise ValueError(f"No outcome configuration found for billing model {billing_model.id}")
    
    # Use the first active outcome config (could be enhanced to select by outcome type)
    outcome_config = next((cfg for cfg in outcome_configs if cfg.is_active), None)
    if not outcome_config:
        raise ValueError(f"No active outcome configuration found for billing model {billing_model.id}")
    
    # Set attribution window
    attribution_start = datetime.utcnow() - timedelta(days=outcome_config.attribution_window_days)
    attribution_end = datetime.utcnow()
    
    # Calculate fee using the enhanced calculation logic
    usage_data = {"outcome_value": outcome_value}
    calculated_fee = calculate_cost(billing_model, usage_data)
    
    # Determine tier applied
    tier_applied = _determine_tier_applied(outcome_config, outcome_value)
    
    # Calculate bonus if applicable
    bonus_applied = 0.0
    if (outcome_config.success_bonus_threshold and outcome_config.success_bonus_percentage and 
        outcome_value >= outcome_config.success_bonus_threshold):
        bonus_applied = outcome_value * (outcome_config.success_bonus_percentage / 100.0)
    
    # Determine verification requirement
    requires_verification = verification_required
    if requires_verification is None:
        requires_verification = outcome_config.requires_verification
    
    # Create outcome metric record
    outcome_metric = OutcomeMetric(
        outcome_config_id=outcome_config.id,
        agent_id=agent_id,
        outcome_value=outcome_value,
        outcome_currency=outcome_currency,
        attribution_start_date=attribution_start,
        attribution_end_date=attribution_end,
        verification_status="verified" if not requires_verification else "pending",
        calculated_fee=calculated_fee,
        tier_applied=tier_applied,
        bonus_applied=bonus_applied,
        billing_status="ready" if not requires_verification else "pending",
        outcome_data=json.dumps(outcome_data) if outcome_data else None,
    )
    
    db.add(outcome_metric)
    db.commit()
    db.refresh(outcome_metric)
    
    logger.info(f"Recorded outcome for agent {agent_id}: value={outcome_value}, fee={calculated_fee}, status={outcome_metric.verification_status}")
    
    return outcome_metric


def verify_outcome(
    db: Session,
    outcome_metric_id: int,
    verified_by: str,
    verification_status: str = "verified",
    verification_notes: Optional[str] = None
) -> OutcomeMetric:
    """
    Verify an outcome metric and update billing status with rule validation
    """
    outcome_metric = db.query(OutcomeMetric).filter(OutcomeMetric.id == outcome_metric_id).first()
    if not outcome_metric:
        raise ValueError(f"Outcome metric with ID {outcome_metric_id} not found")
    
    # Get the billing model for validation rules
    agent = db.query(Agent).filter(Agent.id == outcome_metric.agent_id).first()
    if agent and getattr(agent, 'billing_model_id', None) is not None:
        billing_model_id = getattr(agent, 'billing_model_id')
        # Validate against verification rules
        validation_results = validate_outcome_against_rules(
            db, outcome_metric, billing_model_id
        )
        
        # If validation fails and status is being set to verified, override to rejected
        if not validation_results["is_valid"] and verification_status == "verified":
            verification_status = "rejected"
            if not verification_notes:
                failed_rules = "; ".join([rule["message"] for rule in validation_results["failed_rules"]])
                verification_notes = f"Failed validation rules: {failed_rules}"
    
    # Update outcome metric attributes using setattr to avoid SQLAlchemy Column issues
    setattr(outcome_metric, 'verification_status', verification_status)
    setattr(outcome_metric, 'verification_notes', verification_notes)
    setattr(outcome_metric, 'verified_by', verified_by)
    setattr(outcome_metric, 'verified_at', datetime.utcnow())
    
    # Update billing status based on verification
    if verification_status == "verified":
        setattr(outcome_metric, 'billing_status', "ready")
    elif verification_status == "rejected":
        setattr(outcome_metric, 'billing_status', "rejected")
        setattr(outcome_metric, 'calculated_fee', 0.0)  # No fee for rejected outcomes
    
    db.commit()
    db.refresh(outcome_metric)
    
    logger.info(f"Verified outcome {outcome_metric_id}: status={verification_status}, billing_status={outcome_metric.billing_status}")
    
    return outcome_metric


def get_outcomes_for_billing(
    db: Session,
    agent_id: Optional[int] = None,
    billing_period: Optional[str] = None,
    billing_status: str = "ready"
) -> List[OutcomeMetric]:
    """
    Get outcome metrics ready for billing
    """
    query = db.query(OutcomeMetric).filter(OutcomeMetric.billing_status == billing_status)
    
    if agent_id:
        query = query.filter(OutcomeMetric.agent_id == agent_id)
    
    if billing_period:
        query = query.filter(OutcomeMetric.billing_period == billing_period)
    
    return query.all()


def mark_outcomes_billed(
    db: Session,
    outcome_metric_ids: List[int],
    billing_period: str
) -> int:
    """
    Mark outcome metrics as billed
    """
    updated_count = (
        db.query(OutcomeMetric)
        .filter(OutcomeMetric.id.in_(outcome_metric_ids))
        .update({
            "billing_status": "billed",
            "billed_at": datetime.utcnow(),
            "billing_period": billing_period
        }, synchronize_session=False)
    )
    
    db.commit()
    logger.info(f"Marked {updated_count} outcomes as billed for period {billing_period}")
    return updated_count


def get_outcome_metrics(
    db: Session,
    agent_id: Optional[int] = None,
    verification_status: Optional[str] = None,
    billing_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[OutcomeMetric]:
    """
    Get outcome metrics with filtering
    """
    query = db.query(OutcomeMetric)
    
    if agent_id:
        query = query.filter(OutcomeMetric.agent_id == agent_id)
    
    if verification_status:
        query = query.filter(OutcomeMetric.verification_status == verification_status)
    
    if billing_status:
        query = query.filter(OutcomeMetric.billing_status == billing_status)
    
    return query.offset(skip).limit(limit).all()


def create_outcome_metric(db: Session, outcome_metric_in: OutcomeMetricCreate) -> OutcomeMetric:
    """
    Create an outcome metric using schema validation
    """
    # Validate agent exists
    agent = db.query(Agent).filter(Agent.id == outcome_metric_in.agent_id).first()
    if not agent:
        raise ValueError(f"Agent with ID {outcome_metric_in.agent_id} not found")
    
    # Create outcome metric with schema data
    outcome_metric_data = outcome_metric_in.model_dump()
    
    # Handle JSON serialization for metadata if present
    if 'outcome_data' in outcome_metric_data and outcome_metric_data['outcome_data']:
        outcome_metric_data['outcome_data'] = json.dumps(outcome_metric_data['outcome_data'])
    
    outcome_metric = OutcomeMetric(**outcome_metric_data)
    
    db.add(outcome_metric)
    db.commit()
    db.refresh(outcome_metric)
    
    logger.info(f"Created outcome metric {outcome_metric.id} for agent {outcome_metric_in.agent_id}")
    return outcome_metric


def update_outcome_metric(
    db: Session, 
    outcome_metric_id: int, 
    outcome_metric_in: OutcomeMetricUpdate
) -> OutcomeMetric:
    """
    Update an outcome metric using schema validation
    """
    outcome_metric = db.query(OutcomeMetric).filter(OutcomeMetric.id == outcome_metric_id).first()
    if not outcome_metric:
        raise ValueError(f"Outcome metric with ID {outcome_metric_id} not found")
    
    # Get update data from schema, excluding unset fields
    update_data = outcome_metric_in.model_dump(exclude_unset=True)
    
    # Handle JSON serialization for metadata if present
    if 'outcome_data' in update_data and update_data['outcome_data']:
        update_data['outcome_data'] = json.dumps(update_data['outcome_data'])
    
    # Update fields
    for field, value in update_data.items():
        if hasattr(outcome_metric, field):
            setattr(outcome_metric, field, value)
    
    db.commit()
    db.refresh(outcome_metric)
    
    logger.info(f"Updated outcome metric {outcome_metric_id}")
    return outcome_metric


def get_verification_rules(
    db: Session, 
    billing_model_id: Optional[int] = None,
    outcome_type: Optional[str] = None
) -> List[OutcomeVerificationRule]:
    """
    Get verification rules for outcome validation
    """
    query = db.query(OutcomeVerificationRule)
    
    if billing_model_id:
        query = query.filter(OutcomeVerificationRule.billing_model_id == billing_model_id)
    
    if outcome_type:
        query = query.filter(OutcomeVerificationRule.outcome_type == outcome_type)
    
    return query.all()


def validate_outcome_against_rules(
    db: Session,
    outcome_metric: OutcomeMetric,
    billing_model_id: int
) -> Dict[str, Any]:
    """
    Validate an outcome against verification rules
    """
    rules = get_verification_rules(
        db, 
        billing_model_id=billing_model_id,
        outcome_type=outcome_metric.outcome_type
    )
    
    validation_results = {
        "is_valid": True,
        "failed_rules": [],
        "warnings": [],
        "required_verification": any(rule.verification_required for rule in rules)
    }
    
    for rule in rules:
        # Check minimum value requirement
        if rule.minimum_value and outcome_metric.outcome_value < rule.minimum_value:
            validation_results["is_valid"] = False
            validation_results["failed_rules"].append({
                "rule_type": "minimum_value",
                "expected": rule.minimum_value,
                "actual": outcome_metric.outcome_value,
                "message": f"Outcome value {outcome_metric.outcome_value} is below minimum required value {rule.minimum_value}"
            })
        
        # Check maximum value requirement
        if rule.maximum_value and outcome_metric.outcome_value > rule.maximum_value:
            validation_results["warnings"].append({
                "rule_type": "maximum_value",
                "expected": rule.maximum_value,
                "actual": outcome_metric.outcome_value,
                "message": f"Outcome value {outcome_metric.outcome_value} exceeds typical maximum value {rule.maximum_value}"
            })
        
        # Parse and validate additional rule criteria if present
        if hasattr(rule, 'rule_criteria') and rule.rule_criteria:
            try:
                criteria = json.loads(rule.rule_criteria) if isinstance(rule.rule_criteria, str) else rule.rule_criteria
                # Add custom validation logic based on criteria
                # This can be extended based on specific business requirements
            except (json.JSONDecodeError, TypeError):
                logger.warning(f"Invalid rule criteria format for rule {rule.id}")
    
    return validation_results


def _determine_tier_applied(outcome_config: OutcomeBasedConfig, outcome_value: float) -> Optional[str]:
    """
    Determine which pricing tier was applied for an outcome value
    """
    tier_1_threshold = getattr(outcome_config, 'tier_1_threshold', None)
    if not tier_1_threshold:
        return None
    
    if outcome_value <= tier_1_threshold:
        return "tier_1"
    
    tier_2_threshold = getattr(outcome_config, 'tier_2_threshold', None)
    if tier_2_threshold and outcome_value <= tier_2_threshold:
        return "tier_2"
    
    tier_3_threshold = getattr(outcome_config, 'tier_3_threshold', None)
    if tier_3_threshold and outcome_value <= tier_3_threshold:
        return "tier_3"
    else:
        return "tier_3_plus"


def calculate_outcome_statistics(
    db: Session,
    agent_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Calculate outcome statistics for reporting
    """
    query = db.query(OutcomeMetric)
    
    if agent_id:
        query = query.filter(OutcomeMetric.agent_id == agent_id)
    
    if start_date:
        query = query.filter(OutcomeMetric.attribution_end_date >= start_date)
    
    if end_date:
        query = query.filter(OutcomeMetric.attribution_end_date <= end_date)
    
    outcomes = query.all()
    
    if not outcomes:
        return {
            "total_outcomes": 0,
            "total_value": 0.0,
            "total_fees": 0.0,
            "verified_outcomes": 0,
            "pending_outcomes": 0,
            "rejected_outcomes": 0,
            "average_outcome_value": 0.0,
            "success_rate": 0.0
        }
    
    total_outcomes = len(outcomes)
    total_value = sum(getattr(o, 'outcome_value', 0) for o in outcomes)
    total_fees = sum(getattr(o, 'calculated_fee', 0) for o in outcomes if getattr(o, 'verification_status') != "rejected")
    verified_outcomes = len([o for o in outcomes if getattr(o, 'verification_status') == "verified"])
    pending_outcomes = len([o for o in outcomes if getattr(o, 'verification_status') == "pending"])
    rejected_outcomes = len([o for o in outcomes if getattr(o, 'verification_status') == "rejected"])
    
    return {
        "total_outcomes": total_outcomes,
        "total_value": total_value,
        "total_fees": total_fees,
        "verified_outcomes": verified_outcomes,
        "pending_outcomes": pending_outcomes,
        "rejected_outcomes": rejected_outcomes,
        "average_outcome_value": total_value / total_outcomes if total_outcomes > 0 else 0.0,
        "success_rate": verified_outcomes / total_outcomes if total_outcomes > 0 else 0.0
    }
