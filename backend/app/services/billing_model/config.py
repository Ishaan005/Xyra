"""
Config creation and deletion helpers for billing models.
"""
from app.models.billing_model import (
    AgentBasedConfig, ActivityBasedConfig, OutcomeBasedConfig, HybridConfig, WorkflowBasedConfig, WorkflowType, CommitmentTier
)

def create_agent_config(db, billing_model, cfg_in):
    agent_cfg = AgentBasedConfig(
        billing_model_id=billing_model.id,
        base_agent_fee=cfg_in.agent_base_agent_fee,
        billing_frequency=cfg_in.agent_billing_frequency,
        setup_fee=cfg_in.agent_setup_fee or 0.0,
        volume_discount_enabled=cfg_in.agent_volume_discount_enabled or False,
        volume_discount_threshold=cfg_in.agent_volume_discount_threshold,
        volume_discount_percentage=cfg_in.agent_volume_discount_percentage,
        agent_tier=cfg_in.agent_tier or "professional",
    )
    db.add(agent_cfg)

def create_activity_config(db, billing_model, cfg_in):
    act_cfg = ActivityBasedConfig(
        billing_model_id=billing_model.id,
        price_per_unit=cfg_in.activity_price_per_unit,
        activity_type=cfg_in.activity_activity_type,
        unit_type=cfg_in.activity_unit_type or "action",
        base_agent_fee=cfg_in.activity_base_agent_fee or 0.0,
        volume_pricing_enabled=cfg_in.activity_volume_pricing_enabled or False,
        volume_tier_1_threshold=cfg_in.activity_volume_tier_1_threshold,
        volume_tier_1_price=cfg_in.activity_volume_tier_1_price,
        volume_tier_2_threshold=cfg_in.activity_volume_tier_2_threshold,
        volume_tier_2_price=cfg_in.activity_volume_tier_2_price,
        volume_tier_3_threshold=cfg_in.activity_volume_tier_3_threshold,
        volume_tier_3_price=cfg_in.activity_volume_tier_3_price,
        minimum_charge=cfg_in.activity_minimum_charge or 0.0,
        billing_frequency=cfg_in.activity_billing_frequency or "monthly",
        is_active=cfg_in.activity_is_active if cfg_in.activity_is_active is not None else True,
    )
    db.add(act_cfg)

def create_outcome_config(db, billing_model, cfg_in):
    out_cfg = OutcomeBasedConfig(
        billing_model_id=billing_model.id,
        outcome_type=cfg_in.outcome_outcome_type,
        percentage=cfg_in.outcome_percentage,
    )
    db.add(out_cfg)

def create_hybrid_config(db, billing_model, cfg_in):
    if cfg_in.hybrid_base_fee is not None:
        hybrid_cfg = HybridConfig(
            billing_model_id=billing_model.id,
            base_fee=cfg_in.hybrid_base_fee,
        )
        db.add(hybrid_cfg)
    if cfg_in.hybrid_agent_config:
        create_agent_config(db, billing_model, cfg_in.hybrid_agent_config)
    if cfg_in.hybrid_activity_configs:
        for ac in cfg_in.hybrid_activity_configs:
            create_activity_config(db, billing_model, ac)
    if cfg_in.hybrid_outcome_configs:
        for oc in cfg_in.hybrid_outcome_configs:
            create_outcome_config(db, billing_model, oc)

def create_workflow_config(db, billing_model, cfg_in):
    workflow_cfg = WorkflowBasedConfig(
        billing_model_id=billing_model.id,
        base_platform_fee=cfg_in.workflow_base_platform_fee or 0.0,
        platform_fee_frequency=cfg_in.workflow_platform_fee_frequency or "monthly",
        default_billing_frequency=cfg_in.workflow_default_billing_frequency or "monthly",
        volume_discount_enabled=cfg_in.workflow_volume_discount_enabled or False,
        volume_discount_threshold=cfg_in.workflow_volume_discount_threshold,
        volume_discount_percentage=cfg_in.workflow_volume_discount_percentage,
        overage_multiplier=cfg_in.workflow_overage_multiplier or 1.0,
        currency=cfg_in.workflow_currency or "USD",
        is_active=cfg_in.workflow_is_active if cfg_in.workflow_is_active is not None else True,
    )
    db.add(workflow_cfg)
    if cfg_in.workflow_types:
        for wt in cfg_in.workflow_types:
            workflow_type = WorkflowType(
                billing_model_id=billing_model.id,
                workflow_name=wt.workflow_name,
                workflow_type=wt.workflow_type,
                description=wt.description,
                price_per_workflow=wt.price_per_workflow,
                estimated_compute_cost=wt.estimated_compute_cost or 0.0,
                estimated_duration_minutes=wt.estimated_duration_minutes,
                complexity_level=wt.complexity_level or "medium",
                expected_roi_multiplier=wt.expected_roi_multiplier,
                business_value_category=wt.business_value_category,
                volume_tier_1_threshold=wt.volume_tier_1_threshold,
                volume_tier_1_price=wt.volume_tier_1_price,
                volume_tier_2_threshold=wt.volume_tier_2_threshold,
                volume_tier_2_price=wt.volume_tier_2_price,
                volume_tier_3_threshold=wt.volume_tier_3_threshold,
                volume_tier_3_price=wt.volume_tier_3_price,
                billing_frequency=wt.billing_frequency,
                minimum_charge=wt.minimum_charge or 0.0,
                is_active=wt.is_active if wt.is_active is not None else True,
            )
            db.add(workflow_type)
    if cfg_in.commitment_tiers:
        for ct in cfg_in.commitment_tiers:
            commitment_tier = CommitmentTier(
                billing_model_id=billing_model.id,
                tier_name=ct.tier_name,
                tier_level=ct.tier_level,
                description=ct.description,
                minimum_workflows_per_month=ct.minimum_workflows_per_month,
                minimum_monthly_revenue=ct.minimum_monthly_revenue,
                included_workflows=ct.included_workflows or 0,
                included_workflow_types=ct.included_workflow_types,
                discount_percentage=ct.discount_percentage or 0.0,
                platform_fee_discount=ct.platform_fee_discount or 0.0,
                commitment_period_months=ct.commitment_period_months or 12,
                overage_rate_multiplier=ct.overage_rate_multiplier or 1.0,
                is_active=ct.is_active if ct.is_active is not None else True,
                is_popular=ct.is_popular if ct.is_popular is not None else False,
            )
            db.add(commitment_tier)

def delete_all_configs(db, model_id, current_model_type, model_type_changing):
    if current_model_type in ("agent", "hybrid") or model_type_changing:
        db.query(AgentBasedConfig).filter(AgentBasedConfig.billing_model_id == model_id).delete()
    if current_model_type in ("activity", "hybrid") or model_type_changing:
        db.query(ActivityBasedConfig).filter(ActivityBasedConfig.billing_model_id == model_id).delete()
    if current_model_type in ("outcome", "hybrid") or model_type_changing:
        db.query(OutcomeBasedConfig).filter(OutcomeBasedConfig.billing_model_id == model_id).delete()
    if current_model_type == "hybrid" or model_type_changing:
        db.query(HybridConfig).filter(HybridConfig.billing_model_id == model_id).delete()
    if current_model_type == "workflow" or model_type_changing:
        db.query(WorkflowBasedConfig).filter(WorkflowBasedConfig.billing_model_id == model_id).delete()
        db.query(WorkflowType).filter(WorkflowType.billing_model_id == model_id).delete()
        db.query(CommitmentTier).filter(CommitmentTier.billing_model_id == model_id).delete()
    db.flush()
