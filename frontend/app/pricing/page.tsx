"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useSession } from "next-auth/react"
import api, { setAuthToken } from "../../utils/api"
import toast from "react-hot-toast"
import { Button } from "@/components/ui/button"
import {
  AlertCircle,
  Plus,
  Settings,
  DollarSign,
  Users,
  BarChart,
  Zap,
} from "lucide-react"
import { useOrganization } from "@/contexts/OrganizationContext"
import PricingHeader from "@/app/pricing/components/PricingHeader"
import PricingTabs from "@/app/pricing/components/PricingTabs"
import PricingCreateForm from "@/app/pricing/components/PricingCreateForm"
import ComprehensivePricingForm from "@/app/pricing/components/ComprehensivePricingForm"
import PricingEmptyState from "@/app/pricing/components/PricingEmptyState"
import PricingModelsGrid from "@/app/pricing/components/PricingModelsGrid"
import ActivityCostPreview from "@/app/pricing/components/ActivityCostPreview"
import WorkflowModelDetail from "@/app/pricing/components/workflow-model-detail"
import PricingLoadingSkeleton from "@/app/pricing/components/PricingLoadingSkeleton"

export default function PricingPage() {
  const router = useRouter()
  const { data: session, status } = useSession({
    required: true,
    onUnauthenticated() {
      router.push('/login')
    }
  })
  const { currentOrgId } = useOrganization()
  const [models, setModels] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState("all")
  const [searchQuery, setSearchQuery] = useState("")
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newModel, setNewModel] = useState({
    name: "",
    description: "",
    model_type: "activity",
    // Enhanced Activity/Usage
    price_per_unit: "",
    activity_type: "",
    unit_type: "action",
    base_agent_fee: "",
    volume_pricing_enabled: false,
    volume_tier_1_threshold: "",
    volume_tier_1_price: "",
    volume_tier_2_threshold: "",
    volume_tier_2_price: "",
    volume_tier_3_threshold: "",
    volume_tier_3_price: "",
    minimum_charge: "",
    billing_frequency: "monthly",
    is_active: true,
    // Agent
    agent_base_agent_fee: "",
    agent_billing_frequency: "monthly",
    agent_setup_fee: "",
    agent_volume_discount_enabled: false,
    agent_volume_discount_threshold: "",
    agent_volume_discount_percentage: "",
    agent_tier: "professional",
    // Enhanced Outcome-based Pricing
    outcome_type: "",
    percentage: "",
    // Basic outcome fields
    outcome_outcome_name: "",
    outcome_outcome_type: "",
    outcome_description: "",
    outcome_percentage: "",
    outcome_fixed_charge_per_outcome: "",
    outcome_currency: "USD",
    outcome_billing_frequency: "monthly",
    // Base platform fee
    outcome_base_platform_fee: "",
    outcome_platform_fee_frequency: "monthly",
    // Multi-tier pricing
    outcome_tier_1_threshold: "",
    outcome_tier_1_percentage: "",
    outcome_tier_2_threshold: "",
    outcome_tier_2_percentage: "",
    outcome_tier_3_threshold: "",
    outcome_tier_3_percentage: "",
    // Risk and performance
    outcome_risk_premium_percentage: "",
    outcome_success_rate_assumption: "",
    outcome_monthly_cap_amount: "",
    outcome_minimum_attribution_value: "",
    // Success bonus
    outcome_success_bonus_threshold: "",
    outcome_success_bonus_percentage: "",
    // Attribution and verification
    outcome_attribution_window_days: "",
    outcome_requires_verification: false,
    outcome_auto_bill_verified_outcomes: false,
    outcome_is_active: true,
    // Hybrid
    hybrid_base_fee: "",
    include_agent: false,
    include_activity: false,
    include_outcome: false,
    // Workflow
    workflow_base_platform_fee: "",
    workflow_platform_fee_frequency: "monthly",
    workflow_volume_discount_enabled: false,
    workflow_volume_discount_threshold: "",
    workflow_volume_discount_percentage: "",
    workflow_overage_multiplier: "1.0",
    workflow_currency: "USD",
    workflow_types: [] as any[],
    commitment_tiers: [] as any[],
  })
  const [editingModel, setEditingModel] = useState<any | null>(null)

  useEffect(() => {
    if (status !== 'authenticated' || !currentOrgId) return
    const token = session.user.accessToken ?? ""
    setAuthToken(token)
    // fetch models for the current organization
    api.get(`/billing-models?org_id=${currentOrgId}`)
      .then(res => setModels(res.data))
      .catch(err => setError(err.response?.data?.detail || err.message))
      .finally(() => setLoading(false))
  }, [status, session, currentOrgId])

  const handleCreateModel = async () => {
    if (!currentOrgId || !newModel.name || !newModel.model_type) return
    
    // Build payload with dedicated fields instead of config object
    const payload: any = {
      name: newModel.name,
      description: newModel.description,
      model_type: newModel.model_type,
      is_active: true,
      organization_id: currentOrgId,
    }

    switch (newModel.model_type) {
      case "activity":
        payload.activity_price_per_unit = Number.parseFloat(newModel.price_per_unit) || 0
        payload.activity_activity_type = newModel.activity_type
        payload.activity_unit_type = newModel.unit_type
        payload.activity_base_agent_fee = Number.parseFloat(newModel.base_agent_fee) || 0
        payload.activity_volume_pricing_enabled = newModel.volume_pricing_enabled
        if (newModel.volume_pricing_enabled) {
          payload.activity_volume_tier_1_threshold = Number.parseInt(newModel.volume_tier_1_threshold) || null
          payload.activity_volume_tier_1_price = Number.parseFloat(newModel.volume_tier_1_price) || null
          payload.activity_volume_tier_2_threshold = Number.parseInt(newModel.volume_tier_2_threshold) || null
          payload.activity_volume_tier_2_price = Number.parseFloat(newModel.volume_tier_2_price) || null
          payload.activity_volume_tier_3_threshold = Number.parseInt(newModel.volume_tier_3_threshold) || null
          payload.activity_volume_tier_3_price = Number.parseFloat(newModel.volume_tier_3_price) || null
        }
        payload.activity_minimum_charge = Number.parseFloat(newModel.minimum_charge) || 0
        payload.activity_billing_frequency = newModel.billing_frequency
        payload.activity_is_active = newModel.is_active
        break
      case "agent":
        payload.agent_base_agent_fee = Number.parseFloat(newModel.agent_base_agent_fee) || 0
        payload.agent_billing_frequency = newModel.agent_billing_frequency
        payload.agent_setup_fee = Number.parseFloat(newModel.agent_setup_fee) || 0
        payload.agent_volume_discount_enabled = newModel.agent_volume_discount_enabled
        if (newModel.agent_volume_discount_enabled) {
          payload.agent_volume_discount_threshold = Number.parseInt(newModel.agent_volume_discount_threshold) || 0
          payload.agent_volume_discount_percentage = Number.parseFloat(newModel.agent_volume_discount_percentage) || 0
        }
        payload.agent_tier = newModel.agent_tier
        break
      case "outcome":
        // Basic outcome fields
        payload.outcome_outcome_name = newModel.outcome_outcome_name || ""
        payload.outcome_outcome_type = newModel.outcome_outcome_type || newModel.outcome_type
        payload.outcome_description = newModel.outcome_description || ""
        payload.outcome_percentage = Number.parseFloat(newModel.outcome_percentage || newModel.percentage) || null
        payload.outcome_fixed_charge_per_outcome = Number.parseFloat(newModel.outcome_fixed_charge_per_outcome) || null
        payload.outcome_currency = newModel.outcome_currency || "USD"
        payload.outcome_billing_frequency = newModel.outcome_billing_frequency || "monthly"
        
        // Base platform fee
        payload.outcome_base_platform_fee = Number.parseFloat(newModel.outcome_base_platform_fee) || 0
        payload.outcome_platform_fee_frequency = newModel.outcome_platform_fee_frequency || "monthly"
        
        // Multi-tier pricing
        payload.outcome_tier_1_threshold = Number.parseFloat(newModel.outcome_tier_1_threshold) || null
        payload.outcome_tier_1_percentage = Number.parseFloat(newModel.outcome_tier_1_percentage) || null
        payload.outcome_tier_2_threshold = Number.parseFloat(newModel.outcome_tier_2_threshold) || null
        payload.outcome_tier_2_percentage = Number.parseFloat(newModel.outcome_tier_2_percentage) || null
        payload.outcome_tier_3_threshold = Number.parseFloat(newModel.outcome_tier_3_threshold) || null
        payload.outcome_tier_3_percentage = Number.parseFloat(newModel.outcome_tier_3_percentage) || null
        
        // Risk and performance
        payload.outcome_risk_premium_percentage = Number.parseFloat(newModel.outcome_risk_premium_percentage) || null
        payload.outcome_success_rate_assumption = Number.parseFloat(newModel.outcome_success_rate_assumption) || null
        payload.outcome_monthly_cap_amount = Number.parseFloat(newModel.outcome_monthly_cap_amount) || null
        payload.outcome_minimum_attribution_value = Number.parseFloat(newModel.outcome_minimum_attribution_value) || null
        
        // Success bonus
        payload.outcome_success_bonus_threshold = Number.parseFloat(newModel.outcome_success_bonus_threshold) || null
        payload.outcome_success_bonus_percentage = Number.parseFloat(newModel.outcome_success_bonus_percentage) || null
        
        // Attribution and verification
        payload.outcome_attribution_window_days = Number.parseInt(newModel.outcome_attribution_window_days) || null
        payload.outcome_requires_verification = newModel.outcome_requires_verification || false
        payload.outcome_auto_bill_verified_outcomes = newModel.outcome_auto_bill_verified_outcomes || false
        payload.outcome_is_active = newModel.outcome_is_active !== false
        break
      case "hybrid":
        payload.hybrid_base_fee = Number.parseFloat(newModel.hybrid_base_fee) || 0
        if (newModel.include_agent) {
          payload.hybrid_agent_config = {
            base_agent_fee: Number.parseFloat(newModel.agent_base_agent_fee) || 0,
            billing_frequency: newModel.agent_billing_frequency,
            setup_fee: Number.parseFloat(newModel.agent_setup_fee) || 0,
            volume_discount_enabled: newModel.agent_volume_discount_enabled,
            volume_discount_threshold: newModel.agent_volume_discount_enabled ? Number.parseInt(newModel.agent_volume_discount_threshold) || 0 : null,
            volume_discount_percentage: newModel.agent_volume_discount_enabled ? Number.parseFloat(newModel.agent_volume_discount_percentage) || 0 : null,
            agent_tier: newModel.agent_tier,
          }
        }
        if (newModel.include_activity) {
          payload.hybrid_activity_configs = [
            {
              activity_type: newModel.activity_type,
              price_per_unit: Number.parseFloat(newModel.price_per_unit) || 0,
              unit_type: newModel.unit_type,
              base_agent_fee: Number.parseFloat(newModel.base_agent_fee) || 0,
              volume_pricing_enabled: newModel.volume_pricing_enabled,
              volume_tier_1_threshold: newModel.volume_pricing_enabled ? Number.parseInt(newModel.volume_tier_1_threshold) || null : null,
              volume_tier_1_price: newModel.volume_pricing_enabled ? Number.parseFloat(newModel.volume_tier_1_price) || null : null,
              volume_tier_2_threshold: newModel.volume_pricing_enabled ? Number.parseInt(newModel.volume_tier_2_threshold) || null : null,
              volume_tier_2_price: newModel.volume_pricing_enabled ? Number.parseFloat(newModel.volume_tier_2_price) || null : null,
              volume_tier_3_threshold: newModel.volume_pricing_enabled ? Number.parseInt(newModel.volume_tier_3_threshold) || null : null,
              volume_tier_3_price: newModel.volume_pricing_enabled ? Number.parseFloat(newModel.volume_tier_3_price) || null : null,
              minimum_charge: Number.parseFloat(newModel.minimum_charge) || 0,
              billing_frequency: newModel.billing_frequency,
              is_active: newModel.is_active,
            },
          ]
        }
        if (newModel.include_outcome) {
          payload.hybrid_outcome_configs = [
            {
              outcome_type: newModel.outcome_type,
              percentage: Number.parseFloat(newModel.percentage) || 0,
            },
          ]
        }
        break
      case "workflow":
        payload.workflow_base_platform_fee = Number.parseFloat(newModel.workflow_base_platform_fee) || 0
        payload.workflow_platform_fee_frequency = newModel.workflow_platform_fee_frequency
        payload.workflow_default_billing_frequency = "monthly"
        payload.workflow_volume_discount_enabled = newModel.workflow_volume_discount_enabled
        if (newModel.workflow_volume_discount_enabled) {
          payload.workflow_volume_discount_threshold = Number.parseInt(newModel.workflow_volume_discount_threshold) || null
          payload.workflow_volume_discount_percentage = Number.parseFloat(newModel.workflow_volume_discount_percentage) || null
        }
        payload.workflow_overage_multiplier = Number.parseFloat(newModel.workflow_overage_multiplier) || 1.0
        payload.workflow_currency = newModel.workflow_currency
        payload.workflow_is_active = true
        payload.workflow_types = newModel.workflow_types
        payload.commitment_tiers = newModel.commitment_tiers
        break
    }

    try {
      const res = await api.post("/billing-models", payload)
      setModels((prev) => [...prev, res.data])
      setShowCreateForm(false)
      // reset form
      setNewModel({
        name: "",
        description: "",
        model_type: "activity",
        // Enhanced Activity/Usage
        price_per_unit: "",
        activity_type: "",
        unit_type: "action",
        base_agent_fee: "",
        volume_pricing_enabled: false,
        volume_tier_1_threshold: "",
        volume_tier_1_price: "",
        volume_tier_2_threshold: "",
        volume_tier_2_price: "",
        volume_tier_3_threshold: "",
        volume_tier_3_price: "",
        minimum_charge: "",
        billing_frequency: "monthly",
        is_active: true,
        // Agent
        agent_base_agent_fee: "",
        agent_billing_frequency: "monthly",
        agent_setup_fee: "",
        agent_volume_discount_enabled: false,
        agent_volume_discount_threshold: "",
        agent_volume_discount_percentage: "",
        agent_tier: "professional",
        // Enhanced Outcome-based Pricing
        outcome_type: "",
        percentage: "",
        // Basic outcome fields
        outcome_outcome_name: "",
        outcome_outcome_type: "",
        outcome_description: "",
        outcome_percentage: "",
        outcome_fixed_charge_per_outcome: "",
        outcome_currency: "USD",
        outcome_billing_frequency: "monthly",
        // Base platform fee
        outcome_base_platform_fee: "",
        outcome_platform_fee_frequency: "monthly",
        // Multi-tier pricing
        outcome_tier_1_threshold: "",
        outcome_tier_1_percentage: "",
        outcome_tier_2_threshold: "",
        outcome_tier_2_percentage: "",
        outcome_tier_3_threshold: "",
        outcome_tier_3_percentage: "",
        // Risk and performance
        outcome_risk_premium_percentage: "",
        outcome_success_rate_assumption: "",
        outcome_monthly_cap_amount: "",
        outcome_minimum_attribution_value: "",
        // Success bonus
        outcome_success_bonus_threshold: "",
        outcome_success_bonus_percentage: "",
        // Attribution and verification
        outcome_attribution_window_days: "",
        outcome_requires_verification: false,
        outcome_auto_bill_verified_outcomes: false,
        outcome_is_active: true,
        // Hybrid
        hybrid_base_fee: "",
        include_agent: false,
        include_activity: false,
        include_outcome: false,
        // Workflow
        workflow_base_platform_fee: "",
        workflow_platform_fee_frequency: "monthly",
        workflow_volume_discount_enabled: false,
        workflow_volume_discount_threshold: "",
        workflow_volume_discount_percentage: "",
        workflow_overage_multiplier: "1.0",
        workflow_currency: "USD",
        workflow_types: [] as any[],
        commitment_tiers: [] as any[],
      })
      toast.success("Pricing model created successfully")
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message
      setError(msg)
      toast.error(msg)
    }
  }

  const handleComprehensiveFormSubmit = async (formData: any) => {
    console.log('=== COMPREHENSIVE FORM SUBMIT DEBUG ===');
    console.log('Received formData:', formData);
    console.log('Form data keys:', Object.keys(formData));
    console.log('Current org ID:', currentOrgId);
    console.log('=== END SUBMIT DEBUG ===');
    
    if (!currentOrgId || !formData.name || !formData.model_type) {
      console.error('Missing required fields:', { currentOrgId, name: formData.name, model_type: formData.model_type });
      return;
    }

    // Build payload based on form data structure
    const payload: any = {
      name: formData.name,
      description: formData.description,
      model_type: formData.model_type,
      is_active: true,
      organization_id: currentOrgId,
    }

    // Map form data to backend payload format
    switch (formData.model_type) {
      case "agent":
        payload.agent_base_agent_fee = parseFloat(formData.agent_base_agent_fee) || 0
        payload.agent_billing_frequency = formData.agent_billing_frequency || "monthly"
        payload.agent_setup_fee = parseFloat(formData.agent_setup_fee) || 0
        payload.agent_volume_discount_enabled = formData.agent_volume_discount_enabled || false
        if (formData.agent_volume_discount_enabled) {
          payload.agent_volume_discount_threshold = parseInt(formData.agent_volume_discount_threshold) || null
          payload.agent_volume_discount_percentage = parseFloat(formData.agent_volume_discount_percentage) || null
        }
        payload.agent_tier = formData.agent_tier || "professional"
        break
      case "activity":
        payload.activity_price_per_unit = parseFloat(formData.activity_price_per_unit) || 0
        payload.activity_activity_type = formData.activity_activity_type || "api_call"
        payload.activity_unit_type = formData.activity_unit_type || "action"
        payload.activity_base_agent_fee = parseFloat(formData.activity_base_agent_fee) || 0
        payload.activity_volume_pricing_enabled = formData.activity_volume_pricing_enabled || false
        if (formData.activity_volume_pricing_enabled) {
          payload.activity_volume_tier_1_threshold = parseInt(formData.activity_volume_tier_1_threshold) || null
          payload.activity_volume_tier_1_price = parseFloat(formData.activity_volume_tier_1_price) || null
          payload.activity_volume_tier_2_threshold = parseInt(formData.activity_volume_tier_2_threshold) || null
          payload.activity_volume_tier_2_price = parseFloat(formData.activity_volume_tier_2_price) || null
          payload.activity_volume_tier_3_threshold = parseInt(formData.activity_volume_tier_3_threshold) || null
          payload.activity_volume_tier_3_price = parseFloat(formData.activity_volume_tier_3_price) || null
        }
        payload.activity_minimum_charge = parseFloat(formData.activity_minimum_charge) || 0
        payload.activity_billing_frequency = formData.activity_billing_frequency || "monthly"
        payload.activity_is_active = true
        break
      case "outcome":
        // Map basic and advanced outcome form data to payload
        payload.outcome_outcome_name = formData.outcome_outcome_name || ""
        payload.outcome_outcome_type = formData.outcome_outcome_type || "custom"
        payload.outcome_description = formData.outcome_description || ""
        payload.outcome_percentage = parseFloat(formData.outcome_percentage) || 0
        payload.outcome_fixed_charge_per_outcome = parseFloat(formData.outcome_fixed_charge_per_outcome) || null
        payload.outcome_currency = formData.outcome_currency || "USD"
        payload.outcome_billing_frequency = formData.outcome_billing_frequency || "monthly"
        payload.outcome_base_platform_fee = parseFloat(formData.outcome_base_platform_fee) || 0
        payload.outcome_platform_fee_frequency = formData.outcome_platform_fee_frequency || "monthly"
        payload.outcome_is_active = formData.outcome_is_active === undefined ? true : formData.outcome_is_active

        // Multi-Tier Pricing
        payload.outcome_tier_1_threshold = parseInt(formData.outcome_tier_1_threshold) || null
        payload.outcome_tier_1_percentage = parseFloat(formData.outcome_tier_1_percentage) || null
        payload.outcome_tier_2_threshold = parseInt(formData.outcome_tier_2_threshold) || null
        payload.outcome_tier_2_percentage = parseFloat(formData.outcome_tier_2_percentage) || null
        payload.outcome_tier_3_threshold = parseInt(formData.outcome_tier_3_threshold) || null
        payload.outcome_tier_3_percentage = parseFloat(formData.outcome_tier_3_percentage) || null

        // Risk, Caps, and Bonuses
        payload.outcome_risk_premium_percentage = parseFloat(formData.outcome_risk_premium_percentage) || null
        payload.outcome_monthly_cap_amount = parseFloat(formData.outcome_monthly_cap_amount) || null
        payload.outcome_success_bonus_threshold = parseInt(formData.outcome_success_bonus_threshold) || null
        payload.outcome_success_bonus_percentage = parseFloat(formData.outcome_success_bonus_percentage) || null

        // Attribution and Verification
        payload.outcome_attribution_window_days = parseInt(formData.outcome_attribution_window_days) || null
        payload.outcome_verification_method = formData.outcome_verification_method || "automatic"
        payload.outcome_requires_verification = formData.outcome_requires_verification || false
        payload.outcome_auto_bill_verified_outcomes = formData.outcome_auto_bill_verified_outcomes || false
        payload.outcome_success_rate_assumption = parseFloat(formData.outcome_success_rate_assumption) || null
        payload.outcome_minimum_attribution_value = parseFloat(formData.outcome_minimum_attribution_value) || null
        break
      case "workflow":
        payload.workflow_base_platform_fee = parseFloat(formData.workflow_base_platform_fee) || 0
        payload.workflow_platform_fee_frequency = formData.workflow_platform_fee_frequency || "monthly"
        payload.workflow_default_billing_frequency = "monthly"
        payload.workflow_volume_discount_enabled = formData.workflow_volume_discount_enabled || false
        if (formData.workflow_volume_discount_enabled) {
          payload.workflow_volume_discount_threshold = parseInt(formData.workflow_volume_discount_threshold) || null
          payload.workflow_volume_discount_percentage = parseFloat(formData.workflow_volume_discount_percentage) || null
        }
        payload.workflow_overage_multiplier = parseFloat(formData.workflow_overage_multiplier) || 1.0
        payload.workflow_currency = formData.workflow_currency || "USD"
        payload.workflow_is_active = true
        payload.workflow_types = formData.workflow_types || []
        payload.commitment_tiers = formData.commitment_tiers || []
        break
      case "hybrid":
        payload.hybrid_base_fee = formData.hybrid_base_fee || 0
        break
    }

    try {
      const res = await api.post("/billing-models", payload)
      setModels((prev) => [...prev, res.data])
      setShowCreateForm(false)
      toast.success("Pricing model created successfully")
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message
      setError(msg)
      toast.error(msg)
    }
  }

  const handleDuplicate = async (model: any) => {
    if (!currentOrgId) return
    try {
      const payload = {
        ...model,
        name: `${model.name} (Copy)`,
        organization_id: currentOrgId,
        id: undefined,
      }
      delete payload.id

      const res = await api.post("/billing-models", payload)
      setModels((prev) => [...prev, res.data])
      toast.success("Pricing model duplicated")
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message
      setError(msg)
      toast.error(msg)
    }
  }

  // Delete billing model
  const handleDeleteModel = async (modelId: number) => {
    if (!currentOrgId) return
    if (!confirm("Are you sure you want to delete this pricing model?")) return
    try {
      await api.delete(`/billing-models/${modelId}`)
      setModels((prev) => prev.filter((m) => m.id !== modelId))
      toast.success("Pricing model deleted")
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message
      setError(msg)
      toast.error(msg)
    }
  }

  const getModelIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case "activity":
        return <BarChart className="h-5 w-5" />
      case "agent":
        return <Users className="h-5 w-5" />
      case "hybrid":
        return <Zap className="h-5 w-5" />
      case "outcome":
        return <DollarSign className="h-5 w-5" />
      case "workflow":
        return <Settings className="h-5 w-5" />
      default:
        return <DollarSign className="h-5 w-5" />
    }
  }

  const getModelTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case "activity":
        return "bg-blue/10 text-blue border-blue/8"
      case "agent":
        return "bg-purple/10 text-purple border-purple/8"
      case "hybrid":
        return "bg-gold/10 text-gold-dark border-gold/8"
      case "outcome":
        return "bg-green/10 text-green border-green/8"
      case "workflow":
        return "bg-orange/10 text-orange border-orange/8"
      default:
        return "bg-teal/10 text-teal border-teal/8"
    }
  }

  const filteredModels = models.filter((model) => {
    const matchesTab = activeTab === "all" || model.model_type.toLowerCase() === activeTab
    const matchesSearch =
      searchQuery === "" ||
      model.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (model.description && model.description.toLowerCase().includes(searchQuery.toLowerCase()))
    return matchesTab && matchesSearch
  })

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <PricingHeader
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        onReload={() => window.location.reload()}
      />

      {error && (
        <div className="bg-destructive/10 text-destructive rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
          <div>
            <h3 className="font-medium">Error</h3>
            <p>{error}</p>
          </div>
        </div>
      )}

      {/* Tabs and Create Button */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <PricingTabs activeTab={activeTab} setActiveTab={setActiveTab} />
        <Button className="gap-2 w-full sm:w-auto" onClick={() => setShowCreateForm(!showCreateForm)}>
          <Plus className="h-4 w-4" />
          Create New Model
        </Button>
      </div>

      {/* Create Form */}
      <ComprehensivePricingForm
        show={showCreateForm}
        onCancel={() => setShowCreateForm(false)}
        onSubmit={handleComprehensiveFormSubmit}
        isLoading={false}
      />

      {/* Cost Calculator Preview */}
      {newModel.model_type === "activity" && newModel.price_per_unit && (
        <ActivityCostPreview
          pricePerUnit={newModel.price_per_unit}
          baseAgentFee={newModel.base_agent_fee}
          minimumCharge={newModel.minimum_charge}
          unitType={newModel.unit_type}
          volumePricingEnabled={newModel.volume_pricing_enabled}
          volumeTier1Threshold={newModel.volume_tier_1_threshold}
          volumeTier1Price={newModel.volume_tier_1_price}
          volumeTier2Threshold={newModel.volume_tier_2_threshold}
          volumeTier2Price={newModel.volume_tier_2_price}
          volumeTier3Threshold={newModel.volume_tier_3_threshold}
          volumeTier3Price={newModel.volume_tier_3_price}
        />
      )}

      {/* Workflow Cost Preview */}
      {newModel.model_type === "workflow" && newModel.workflow_types.length > 0 && (
        <div className="mt-4 p-4 bg-orange-50 border border-orange-200 rounded-lg">
          <h4 className="font-medium text-sm mb-3 text-orange-800">💡 Workflow Cost Preview</h4>
          <p className="text-xs text-orange-600 mb-3">
            Base platform fee: ${parseFloat(newModel.workflow_base_platform_fee) || 0}/month + per-workflow charges
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {newModel.workflow_types.slice(0, 4).map((workflow: any, index: number) => (
              <div key={index} className="bg-white rounded p-2 border border-orange-200">
                <div className="text-xs font-medium text-orange-700">{workflow.workflow_name}</div>
                <div className="text-xs text-orange-600 mt-1">
                  ${workflow.price_per_workflow?.toFixed(2) || '0.00'} per execution
                  {workflow.volume_tier_1_threshold && (
                    <div>Volume: {workflow.volume_tier_1_threshold}+ at ${workflow.volume_tier_1_price?.toFixed(2) || '0.00'}</div>
                  )}
                </div>
              </div>
            ))}
          </div>
          <p className="text-xs text-orange-600 mt-2">
            * {newModel.workflow_volume_discount_enabled ? 
              `Global ${newModel.workflow_volume_discount_percentage}% discount when total workflows exceed ${newModel.workflow_volume_discount_threshold}/month` :
              "Configure volume discounts for additional savings"
            }
          </p>
        </div>
      )}

      {/* Models Grid */}
      {loading ? (
        <PricingLoadingSkeleton />
      ) : filteredModels.length === 0 ? (
        <PricingEmptyState searchQuery={searchQuery} onCreate={() => setShowCreateForm(true)} />
      ) : (
        <>
          <PricingModelsGrid
            models={filteredModels}
            onEdit={setEditingModel}
            onDelete={handleDeleteModel}
            onDuplicate={handleDuplicate}
            getModelIcon={getModelIcon}
            getModelTypeColor={getModelTypeColor}
          />
          {editingModel && (
            <WorkflowModelDetail
              modelId={editingModel.id}
              onBack={() => setEditingModel(null)}
            />
          )}
        </>
      )}
    </div>
  )
}
