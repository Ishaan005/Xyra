"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Plus, Trash2, Edit, Copy, Settings, DollarSign, Zap, BarChart3, Target } from "lucide-react"
import toast from "react-hot-toast"

interface WorkflowType {
  workflow_name: string
  workflow_type: string
  description: string
  price_per_workflow: number
  estimated_compute_cost: number
  estimated_duration_minutes: number
  complexity_level: string
  expected_roi_multiplier: number
  business_value_category: string
  volume_tier_1_threshold: number | null
  volume_tier_1_price: number | null
  volume_tier_2_threshold: number | null
  volume_tier_2_price: number | null
  volume_tier_3_threshold: number | null
  volume_tier_3_price: number | null
  billing_frequency: string
  minimum_charge: number
  is_active: boolean
}

interface CommitmentTier {
  tier_name: string
  tier_level: number
  description: string
  minimum_workflows_per_month: number
  minimum_monthly_revenue: number
  included_workflows: number
  included_workflow_types: string | null
  discount_percentage: number
  platform_fee_discount: number
  commitment_period_months: number
  overage_rate_multiplier: number
  is_active: boolean
  is_popular: boolean
}

interface WorkflowBillingFormProps {
  workflowTypes: WorkflowType[]
  commitmentTiers: CommitmentTier[]
  onWorkflowTypesChange: (types: WorkflowType[]) => void
  onCommitmentTiersChange: (tiers: CommitmentTier[]) => void
  baseModel: any
  onBaseModelChange: (model: any) => void
}

const getComplexityIcon = (level: string) => {
  switch (level) {
    case "simple": return <Zap className="h-4 w-4" />
    case "complex": return <Settings className="h-4 w-4" />
    default: return <BarChart3 className="h-4 w-4" />
  }
}

const getComplexityColor = (level: string) => {
  switch (level) {
    case "simple": return "bg-green/10 text-green border-green/20"
    case "complex": return "bg-red/10 text-red border-red/20"
    default: return "bg-blue/10 text-blue border-blue/20"
  }
}

const getBusinessValueIcon = (category: string) => {
  switch (category) {
    case "lead_generation": return <Target className="h-4 w-4" />
    case "revenue_growth": return <DollarSign className="h-4 w-4" />
    case "cost_savings": return <BarChart3 className="h-4 w-4" />
    default: return <Settings className="h-4 w-4" />
  }
}

export default function WorkflowBillingForm({ 
  workflowTypes, 
  commitmentTiers, 
  onWorkflowTypesChange, 
  onCommitmentTiersChange,
  baseModel,
  onBaseModelChange
}: WorkflowBillingFormProps) {
  const [showWorkflowForm, setShowWorkflowForm] = useState(false)
  const [showTierForm, setShowTierForm] = useState(false)
  const [editingWorkflow, setEditingWorkflow] = useState<WorkflowType | null>(null)
  const [editingTier, setEditingTier] = useState<CommitmentTier | null>(null)

  const defaultWorkflowType: WorkflowType = {
    workflow_name: "",
    workflow_type: "",
    description: "",
    price_per_workflow: 0,
    estimated_compute_cost: 0,
    estimated_duration_minutes: 10,
    complexity_level: "medium",
    expected_roi_multiplier: 5,
    business_value_category: "cost_savings",
    volume_tier_1_threshold: null,
    volume_tier_1_price: null,
    volume_tier_2_threshold: null,
    volume_tier_2_price: null,
    volume_tier_3_threshold: null,
    volume_tier_3_price: null,
    billing_frequency: "monthly",
    minimum_charge: 0,
    is_active: true
  }

  const defaultCommitmentTier: CommitmentTier = {
    tier_name: "",
    tier_level: 1,
    description: "",
    minimum_workflows_per_month: 0,
    minimum_monthly_revenue: 0,
    included_workflows: 0,
    included_workflow_types: null,
    discount_percentage: 0,
    platform_fee_discount: 0,
    commitment_period_months: 12,
    overage_rate_multiplier: 1.0,
    is_active: true,
    is_popular: false
  }

  const [newWorkflow, setNewWorkflow] = useState<WorkflowType>(defaultWorkflowType)
  const [newTier, setNewTier] = useState<CommitmentTier>(defaultCommitmentTier)

  const addWorkflowType = () => {
    if (!newWorkflow.workflow_name || !newWorkflow.workflow_type || newWorkflow.price_per_workflow <= 0) {
      toast.error("Please fill in required fields: name, type, and price")
      return
    }

    if (editingWorkflow) {
      // Update existing
      const updated = workflowTypes.map(wt => 
        wt.workflow_type === editingWorkflow.workflow_type ? newWorkflow : wt
      )
      onWorkflowTypesChange(updated)
      setEditingWorkflow(null)
      toast.success("Workflow type updated")
    } else {
      // Add new
      onWorkflowTypesChange([...workflowTypes, newWorkflow])
      toast.success("Workflow type added")
    }
    
    setNewWorkflow(defaultWorkflowType)
    setShowWorkflowForm(false)
  }

  const editWorkflowType = (workflow: WorkflowType) => {
    setNewWorkflow(workflow)
    setEditingWorkflow(workflow)
    setShowWorkflowForm(true)
  }

  const deleteWorkflowType = (workflowType: string) => {
    if (!confirm("Are you sure you want to delete this workflow type?")) return
    
    const updated = workflowTypes.filter(wt => wt.workflow_type !== workflowType)
    onWorkflowTypesChange(updated)
    toast.success("Workflow type deleted")
  }

  const duplicateWorkflowType = (workflow: WorkflowType) => {
    const duplicated = {
      ...workflow,
      workflow_name: `${workflow.workflow_name} (Copy)`,
      workflow_type: `${workflow.workflow_type}_copy_${Date.now()}`
    }
    onWorkflowTypesChange([...workflowTypes, duplicated])
    toast.success("Workflow type duplicated")
  }

  const addCommitmentTier = () => {
    if (!newTier.tier_name || newTier.minimum_workflows_per_month <= 0) {
      toast.error("Please fill in required fields: name and minimum workflows")
      return
    }

    if (editingTier) {
      // Update existing
      const updated = commitmentTiers.map(ct => 
        ct.tier_level === editingTier.tier_level ? newTier : ct
      )
      onCommitmentTiersChange(updated)
      setEditingTier(null)
      toast.success("Commitment tier updated")
    } else {
      // Add new
      const newLevel = Math.max(...commitmentTiers.map(ct => ct.tier_level), 0) + 1
      onCommitmentTiersChange([...commitmentTiers, { ...newTier, tier_level: newLevel }])
      toast.success("Commitment tier added")
    }
    
    setNewTier(defaultCommitmentTier)
    setShowTierForm(false)
  }

  const editCommitmentTier = (tier: CommitmentTier) => {
    setNewTier(tier)
    setEditingTier(tier)
    setShowTierForm(true)
  }

  const deleteCommitmentTier = (tierLevel: number) => {
    if (!confirm("Are you sure you want to delete this commitment tier?")) return
    
    const updated = commitmentTiers.filter(ct => ct.tier_level !== tierLevel)
    onCommitmentTiersChange(updated)
    toast.success("Commitment tier deleted")
  }

  const calculateWorkflowROI = (workflow: WorkflowType) => {
    if (!workflow.estimated_compute_cost || workflow.estimated_compute_cost === 0) return 0
    return ((workflow.price_per_workflow - workflow.estimated_compute_cost) / workflow.estimated_compute_cost * 100)
  }

  return (
    <div className="space-y-6">
      {/* Base Platform Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Platform Configuration
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">              <div className="space-y-2">
                <label className="text-sm font-medium">Base Platform Fee ($)</label>
                <Input
                  type="number"
                  step="0.01"
                  placeholder="3000.00"
                  value={baseModel.workflow_base_platform_fee?.toString() || ""}
                  onChange={(e) => onBaseModelChange({ ...baseModel, workflow_base_platform_fee: e.target.value || "" })}
                />
                <p className="text-xs text-muted-foreground">Monthly subscription fee for platform access</p>
              </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Platform Fee Frequency</label>
              <select
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={baseModel.workflow_platform_fee_frequency || "monthly"}
                onChange={(e) => onBaseModelChange({ ...baseModel, workflow_platform_fee_frequency: e.target.value })}
              >
                <option value="monthly">Monthly</option>
                <option value="yearly">Yearly</option>
              </select>
            </div>
          </div>
          
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="workflow-volume-discount"
                checked={baseModel.workflow_volume_discount_enabled || false}
                onChange={(e) => onBaseModelChange({ ...baseModel, workflow_volume_discount_enabled: e.target.checked })}
              />
              <label htmlFor="workflow-volume-discount" className="text-sm font-medium">Enable Global Volume Discount</label>
            </div>
            
            {baseModel.workflow_volume_discount_enabled && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pl-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Volume Threshold</label>
                  <Input
                    type="number"
                    placeholder="50"
                    value={baseModel.workflow_volume_discount_threshold?.toString() || ""}
                    onChange={(e) => onBaseModelChange({ ...baseModel, workflow_volume_discount_threshold: e.target.value || "" })}
                  />
                  <p className="text-xs text-muted-foreground">Total workflows/month to qualify</p>
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium">Discount Percentage (%)</label>
                  <Input
                    type="number"
                    step="0.1"
                    placeholder="20.0"
                    value={baseModel.workflow_volume_discount_percentage?.toString() || ""}
                    onChange={(e) => onBaseModelChange({ ...baseModel, workflow_volume_discount_percentage: e.target.value || "" })}
                  />
                  <p className="text-xs text-muted-foreground">Discount on total bill</p>
                </div>
              </div>
            )}
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Overage Multiplier</label>
              <Input
                type="number"
                step="0.1"
                placeholder="1.0"
                value={baseModel.workflow_overage_multiplier?.toString() || ""}
                onChange={(e) => onBaseModelChange({ ...baseModel, workflow_overage_multiplier: e.target.value || "" })}
              />
              <p className="text-xs text-muted-foreground">1.0 = normal price, 1.5 = 150% for overages</p>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Currency</label>
              <select
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={baseModel.workflow_currency || "USD"}
                onChange={(e) => onBaseModelChange({ ...baseModel, workflow_currency: e.target.value })}
              >
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
                <option value="GBP">GBP</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Workflow Types Management */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5" />
              Workflow Types ({workflowTypes.length})
            </CardTitle>
            <Button onClick={() => setShowWorkflowForm(true)} size="sm">
              <Plus className="h-4 w-4 mr-2" />
              Add Workflow Type
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {workflowTypes.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Zap className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p>No workflow types defined yet</p>
              <p className="text-sm">Add workflow types to define your pricing structure</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {workflowTypes.map((workflow, index) => (
                <Card key={workflow.workflow_type} className="border border-border/50">
                  <CardHeader className="pb-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-medium">{workflow.workflow_name}</h4>
                        <code className="text-xs text-muted-foreground">{workflow.workflow_type}</code>
                      </div>
                      <div className="flex gap-1">
                        <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => editWorkflowType(workflow)}>
                          <Edit className="h-3 w-3" />
                        </Button>
                        <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => duplicateWorkflowType(workflow)}>
                          <Copy className="h-3 w-3" />
                        </Button>
                        <Button size="icon" variant="ghost" className="h-7 w-7 text-red-500" onClick={() => deleteWorkflowType(workflow.workflow_type)}>
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0 space-y-3">
                    <p className="text-sm text-muted-foreground">{workflow.description}</p>
                    
                    <div className="flex gap-2">
                      <Badge className={getComplexityColor(workflow.complexity_level)}>
                        {getComplexityIcon(workflow.complexity_level)}
                        <span className="ml-1">{workflow.complexity_level}</span>
                      </Badge>
                      <Badge variant="outline">
                        {getBusinessValueIcon(workflow.business_value_category)}
                        <span className="ml-1">{workflow.business_value_category.replace('_', ' ')}</span>
                      </Badge>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Price:</span>
                        <div className="font-mono font-medium">${workflow.price_per_workflow.toFixed(2)}</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Min Charge:</span>
                        <div className="font-mono">${workflow.minimum_charge.toFixed(2)}</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Duration:</span>
                        <div>{workflow.estimated_duration_minutes}min</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">ROI:</span>
                        <div className="font-medium text-green-600">{calculateWorkflowROI(workflow).toFixed(0)}%</div>
                      </div>
                    </div>
                    
                    {(workflow.volume_tier_1_threshold && workflow.volume_tier_1_price) && (
                      <div className="text-xs text-muted-foreground bg-muted/30 p-2 rounded">
                        Volume pricing: {workflow.volume_tier_1_threshold}+ at ${workflow.volume_tier_1_price}
                        {workflow.volume_tier_2_threshold && `, ${workflow.volume_tier_2_threshold}+ at $${workflow.volume_tier_2_price}`}
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Commitment Tiers Management */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              Commitment Tiers ({commitmentTiers.length})
            </CardTitle>
            <Button onClick={() => setShowTierForm(true)} size="sm">
              <Plus className="h-4 w-4 mr-2" />
              Add Commitment Tier
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {commitmentTiers.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Target className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p>No commitment tiers defined yet</p>
              <p className="text-sm">Add tiers to offer volume commitments and discounts</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {commitmentTiers
                .sort((a, b) => a.tier_level - b.tier_level)
                .map((tier) => (
                <Card key={tier.tier_level} className={`border ${tier.is_popular ? 'border-orange-200 bg-orange-50/50' : 'border-border/50'}`}>
                  <CardHeader className="pb-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-medium flex items-center gap-2">
                          {tier.tier_name}
                          {tier.is_popular && <Badge className="bg-orange-100 text-orange-700 text-xs">Popular</Badge>}
                        </h4>
                        <p className="text-xs text-muted-foreground">Level {tier.tier_level}</p>
                      </div>
                      <div className="flex gap-1">
                        <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => editCommitmentTier(tier)}>
                          <Edit className="h-3 w-3" />
                        </Button>
                        <Button size="icon" variant="ghost" className="h-7 w-7 text-red-500" onClick={() => deleteCommitmentTier(tier.tier_level)}>
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0 space-y-3">
                    <p className="text-sm text-muted-foreground">{tier.description}</p>
                    
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Min Workflows/Month:</span>
                        <span className="font-medium">{tier.minimum_workflows_per_month.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Min Monthly Revenue:</span>
                        <span className="font-medium">${tier.minimum_monthly_revenue.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Included Workflows:</span>
                        <span className="font-medium">{tier.included_workflows.toLocaleString()}</span>
                      </div>
                      {tier.discount_percentage > 0 && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Discount:</span>
                          <span className="font-medium text-green-600">{tier.discount_percentage}%</span>
                        </div>
                      )}
                      {tier.platform_fee_discount > 0 && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Platform Discount:</span>
                          <span className="font-medium text-green-600">${tier.platform_fee_discount}</span>
                        </div>
                      )}
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Contract Period:</span>
                        <span className="font-medium">{tier.commitment_period_months}mo</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Workflow Type Form Modal */}
      {showWorkflowForm && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <Card className="max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <CardTitle>{editingWorkflow ? 'Edit' : 'Add'} Workflow Type</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Workflow Name *</label>
                  <Input
                    placeholder="Lead Research"
                    value={newWorkflow.workflow_name}
                    onChange={(e) => setNewWorkflow({ ...newWorkflow, workflow_name: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Workflow Type Key *</label>
                  <Input
                    placeholder="lead_research"
                    value={newWorkflow.workflow_type}
                    onChange={(e) => setNewWorkflow({ ...newWorkflow, workflow_type: e.target.value })}
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium">Description</label>
                <Input
                  placeholder="Comprehensive lead profiling and research"
                  value={newWorkflow.description}
                  onChange={(e) => setNewWorkflow({ ...newWorkflow, description: e.target.value })}
                />
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Price per Workflow *</label>
                  <Input
                    type="number"
                    step="0.01"
                    placeholder="2.00"
                    value={newWorkflow.price_per_workflow.toString()}
                    onChange={(e) => setNewWorkflow({ ...newWorkflow, price_per_workflow: parseFloat(e.target.value) || 0 })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Minimum Charge</label>
                  <Input
                    type="number"
                    step="0.01"
                    placeholder="0.00"
                    value={newWorkflow.minimum_charge.toString()}
                    onChange={(e) => setNewWorkflow({ ...newWorkflow, minimum_charge: parseFloat(e.target.value) || 0 })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Duration (minutes)</label>
                  <Input
                    type="number"
                    placeholder="10"
                    value={newWorkflow.estimated_duration_minutes.toString()}
                    onChange={(e) => setNewWorkflow({ ...newWorkflow, estimated_duration_minutes: parseInt(e.target.value) || 0 })}
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Complexity Level</label>
                  <select
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    value={newWorkflow.complexity_level}
                    onChange={(e) => setNewWorkflow({ ...newWorkflow, complexity_level: e.target.value })}
                  >
                    <option value="simple">Simple</option>
                    <option value="medium">Medium</option>
                    <option value="complex">Complex</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Business Value</label>
                  <select
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    value={newWorkflow.business_value_category}
                    onChange={(e) => setNewWorkflow({ ...newWorkflow, business_value_category: e.target.value })}
                  >
                    <option value="lead_generation">Lead Generation</option>
                    <option value="revenue_growth">Revenue Growth</option>
                    <option value="cost_savings">Cost Savings</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Expected ROI Multiplier</label>
                  <Input
                    type="number"
                    step="0.1"
                    placeholder="5.0"
                    value={newWorkflow.expected_roi_multiplier.toString()}
                    onChange={(e) => setNewWorkflow({ ...newWorkflow, expected_roi_multiplier: parseFloat(e.target.value) || 0 })}
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium">Estimated Compute Cost (for margin tracking)</label>
                <Input
                  type="number"
                  step="0.01"
                  placeholder="0.50"
                  value={newWorkflow.estimated_compute_cost.toString()}
                  onChange={(e) => setNewWorkflow({ ...newWorkflow, estimated_compute_cost: parseFloat(e.target.value) || 0 })}
                />
                {newWorkflow.estimated_compute_cost > 0 && (
                  <p className="text-xs text-muted-foreground">
                    Estimated margin: ${(newWorkflow.price_per_workflow - newWorkflow.estimated_compute_cost).toFixed(2)} 
                    ({((newWorkflow.price_per_workflow - newWorkflow.estimated_compute_cost) / newWorkflow.price_per_workflow * 100).toFixed(1)}%)
                  </p>
                )}
              </div>
              
              <div className="space-y-4">
                <h4 className="font-medium">Volume Pricing Tiers (Optional)</h4>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Tier 1 Threshold</label>
                    <Input
                      type="number"
                      placeholder="100"
                      value={newWorkflow.volume_tier_1_threshold?.toString() || ''}
                      onChange={(e) => setNewWorkflow({ ...newWorkflow, volume_tier_1_threshold: e.target.value ? parseInt(e.target.value) : null })}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Tier 1 Price</label>
                    <Input
                      type="number"
                      step="0.01"
                      placeholder="1.80"
                      value={newWorkflow.volume_tier_1_price?.toString() || ''}
                      onChange={(e) => setNewWorkflow({ ...newWorkflow, volume_tier_1_price: e.target.value ? parseFloat(e.target.value) : null })}
                    />
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Tier 2 Threshold</label>
                    <Input
                      type="number"
                      placeholder="500"
                      value={newWorkflow.volume_tier_2_threshold?.toString() || ''}
                      onChange={(e) => setNewWorkflow({ ...newWorkflow, volume_tier_2_threshold: e.target.value ? parseInt(e.target.value) : null })}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Tier 2 Price</label>
                    <Input
                      type="number"
                      step="0.01"
                      placeholder="1.50"
                      value={newWorkflow.volume_tier_2_price?.toString() || ''}
                      onChange={(e) => setNewWorkflow({ ...newWorkflow, volume_tier_2_price: e.target.value ? parseFloat(e.target.value) : null })}
                    />
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Tier 3 Threshold</label>
                    <Input
                      type="number"
                      placeholder="1000"
                      value={newWorkflow.volume_tier_3_threshold?.toString() || ''}
                      onChange={(e) => setNewWorkflow({ ...newWorkflow, volume_tier_3_threshold: e.target.value ? parseInt(e.target.value) : null })}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Tier 3 Price</label>
                    <Input
                      type="number"
                      step="0.01"
                      placeholder="1.20"
                      value={newWorkflow.volume_tier_3_price?.toString() || ''}
                      onChange={(e) => setNewWorkflow({ ...newWorkflow, volume_tier_3_price: e.target.value ? parseFloat(e.target.value) : null })}
                    />
                  </div>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="workflow-active"
                  checked={newWorkflow.is_active}
                  onChange={(e) => setNewWorkflow({ ...newWorkflow, is_active: e.target.checked })}
                />
                <label htmlFor="workflow-active" className="text-sm">Active</label>
              </div>
            </CardContent>
            <CardContent className="flex justify-between border-t pt-4">
              <Button variant="outline" onClick={() => {
                setShowWorkflowForm(false)
                setEditingWorkflow(null)
                setNewWorkflow(defaultWorkflowType)
              }}>
                Cancel
              </Button>
              <Button onClick={addWorkflowType}>
                {editingWorkflow ? 'Update' : 'Add'} Workflow Type
              </Button>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Commitment Tier Form Modal */}
      {showTierForm && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <Card className="max-w-xl w-full max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <CardTitle>{editingTier ? 'Edit' : 'Add'} Commitment Tier</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Tier Name *</label>
                  <Input
                    placeholder="Growth"
                    value={newTier.tier_name}
                    onChange={(e) => setNewTier({ ...newTier, tier_name: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Commitment Period (months)</label>
                  <Input
                    type="number"
                    placeholder="12"
                    value={newTier.commitment_period_months.toString()}
                    onChange={(e) => setNewTier({ ...newTier, commitment_period_months: parseInt(e.target.value) || 12 })}
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium">Description</label>
                <Input
                  placeholder="Best value for growing sales teams"
                  value={newTier.description}
                  onChange={(e) => setNewTier({ ...newTier, description: e.target.value })}
                />
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Min Workflows/Month *</label>
                  <Input
                    type="number"
                    placeholder="2000"
                    value={newTier.minimum_workflows_per_month.toString()}
                    onChange={(e) => setNewTier({ ...newTier, minimum_workflows_per_month: parseInt(e.target.value) || 0 })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Min Monthly Revenue</label>
                  <Input
                    type="number"
                    step="0.01"
                    placeholder="12500.00"
                    value={newTier.minimum_monthly_revenue?.toString() || ''}
                    onChange={(e) => setNewTier({ ...newTier, minimum_monthly_revenue: e.target.value ? parseFloat(e.target.value) : 0 })}
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Included Workflows</label>
                  <Input
                    type="number"
                    placeholder="100"
                    value={newTier.included_workflows?.toString() || ''}
                    onChange={(e) => setNewTier({ ...newTier, included_workflows: parseInt(e.target.value) || 0 })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Discount Percentage (%)</label>
                  <Input
                    type="number"
                    step="0.1"
                    placeholder="10.0"
                    value={newTier.discount_percentage?.toString() || ''}
                    onChange={(e) => setNewTier({ ...newTier, discount_percentage: parseFloat(e.target.value) || 0 })}
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Platform Fee Discount ($)</label>
                  <Input
                    type="number"
                    step="0.01"
                    placeholder="500.00"
                    value={newTier.platform_fee_discount?.toString() || ''}
                    onChange={(e) => setNewTier({ ...newTier, platform_fee_discount: parseFloat(e.target.value) || 0 })}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Overage Rate Multiplier</label>
                  <Input
                    type="number"
                    step="0.1"
                    placeholder="1.0"
                    value={newTier.overage_rate_multiplier?.toString() || ''}
                    onChange={(e) => setNewTier({ ...newTier, overage_rate_multiplier: parseFloat(e.target.value) || 1.0 })}
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium">Included Workflow Types (JSON array)</label>
                <Input
                  placeholder='["lead_research", "email_personalization"]'
                  value={newTier.included_workflow_types || ''}
                  onChange={(e) => setNewTier({ ...newTier, included_workflow_types: e.target.value || null })}
                />
                <p className="text-xs text-muted-foreground">JSON array of workflow type keys, or leave empty for all types</p>
              </div>
              
              <div className="flex gap-4">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="tier-active"
                    checked={newTier.is_active}
                    onChange={(e) => setNewTier({ ...newTier, is_active: e.target.checked })}
                  />
                  <label htmlFor="tier-active" className="text-sm">Active</label>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="tier-popular"
                    checked={newTier.is_popular}
                    onChange={(e) => setNewTier({ ...newTier, is_popular: e.target.checked })}
                  />
                  <label htmlFor="tier-popular" className="text-sm">Mark as Popular</label>
                </div>
              </div>
            </CardContent>
            <CardContent className="flex justify-between border-t pt-4">
              <Button variant="outline" onClick={() => {
                setShowTierForm(false)
                setEditingTier(null)
                setNewTier(defaultCommitmentTier)
              }}>
                Cancel
              </Button>
              <Button onClick={addCommitmentTier}>
                {editingTier ? 'Update' : 'Add'} Commitment Tier
              </Button>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
