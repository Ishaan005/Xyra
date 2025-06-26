"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Settings, Zap, Target, Calculator, Edit, ArrowLeft } from "lucide-react"
import WorkflowBillingForm from "@/app/pricing/components/workflow-billing-form"
import WorkflowCostCalculator from "@/app/pricing/components/workflow-cost-calculator"
import api from "@/utils/api"
import toast from "react-hot-toast"

interface WorkflowModelDetailProps {
  modelId: number
  onBack: () => void
}

export default function WorkflowModelDetail({ modelId, onBack }: WorkflowModelDetailProps) {
  const [model, setModel] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [editMode, setEditMode] = useState(false)
  const [activeTab, setActiveTab] = useState("overview")

  useEffect(() => {
    fetchModel()
  }, [modelId])

  const fetchModel = async () => {
    try {
      const response = await api.get(`/billing-models/${modelId}`)
      setModel(response.data)
    } catch (error) {
      console.error("Failed to fetch model:", error)
      toast.error("Failed to load model details")
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateModel = async (updatedData: any) => {
    try {
      const response = await api.put(`/billing-models/${modelId}`, updatedData)
      setModel(response.data)
      setEditMode(false)
      toast.success("Model updated successfully")
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to update model")
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500 mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading workflow model...</p>
        </div>
      </div>
    )
  }

  if (!model) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Model not found</p>
        <Button onClick={onBack} className="mt-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Models
        </Button>
      </div>
    )
  }

  const getComplexityColor = (level: string) => {
    switch (level) {
      case "simple": return "bg-green/10 text-green border-green/20"
      case "complex": return "bg-red/10 text-red border-red/20"
      default: return "bg-blue/10 text-blue border-blue/20"
    }
  }

  const calculateTotalWorkflows = () => {
    return model.workflow_types?.length || 0
  }

  const calculateAverageWorkflowPrice = () => {
    if (!model.workflow_types || model.workflow_types.length === 0) return 0
    const total = model.workflow_types.reduce((sum: number, wt: any) => sum + wt.price_per_workflow, 0)
    return total / model.workflow_types.length
  }

  const calculateEstimatedMargin = () => {
    if (!model.workflow_types || model.workflow_types.length === 0) return 0
    const totalRevenue = model.workflow_types.reduce((sum: number, wt: any) => sum + wt.price_per_workflow, 0)
    const totalCost = model.workflow_types.reduce((sum: number, wt: any) => sum + (wt.estimated_compute_cost || 0), 0)
    if (totalRevenue === 0) return 0
    return ((totalRevenue - totalCost) / totalRevenue) * 100
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={onBack}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Models
          </Button>
          <div>
            <h1 className="text-2xl font-bold">{model.name}</h1>
            <p className="text-muted-foreground">{model.description}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge className="bg-orange/10 text-orange border-orange/20">
            {model.model_type}
          </Badge>
          <Button onClick={() => setEditMode(!editMode)}>
            <Edit className="h-4 w-4 mr-2" />
            {editMode ? 'Cancel Edit' : 'Edit Model'}
          </Button>
        </div>
      </div>

      {editMode ? (
        /* Edit Mode */
        <Card>
          <CardHeader>
            <CardTitle>Edit Workflow Billing Model</CardTitle>
          </CardHeader>
          <CardContent>
            <WorkflowBillingForm
              workflowTypes={model.workflow_types || []}
              commitmentTiers={model.commitment_tiers || []}
              onWorkflowTypesChange={(types) => setModel({ ...model, workflow_types: types })}
              onCommitmentTiersChange={(tiers) => setModel({ ...model, commitment_tiers: tiers })}
              baseModel={{
                workflow_base_platform_fee: model.workflow_config?.base_platform_fee || 0,
                workflow_platform_fee_frequency: model.workflow_config?.platform_fee_frequency || 'monthly',
                workflow_volume_discount_enabled: model.workflow_config?.volume_discount_enabled || false,
                workflow_volume_discount_threshold: model.workflow_config?.volume_discount_threshold || '',
                workflow_volume_discount_percentage: model.workflow_config?.volume_discount_percentage || '',
                workflow_overage_multiplier: model.workflow_config?.overage_multiplier || '1.0',
                workflow_currency: model.workflow_config?.currency || 'USD'
              }}
              onBaseModelChange={(baseModel) => {
                setModel({
                  ...model,
                  workflow_config: {
                    ...model.workflow_config,
                    base_platform_fee: parseFloat(baseModel.workflow_base_platform_fee) || 0,
                    platform_fee_frequency: baseModel.workflow_platform_fee_frequency,
                    volume_discount_enabled: baseModel.workflow_volume_discount_enabled,
                    volume_discount_threshold: parseInt(baseModel.workflow_volume_discount_threshold) || null,
                    volume_discount_percentage: parseFloat(baseModel.workflow_volume_discount_percentage) || null,
                    overage_multiplier: parseFloat(baseModel.workflow_overage_multiplier) || 1.0,
                    currency: baseModel.workflow_currency
                  }
                })
              }}
            />
            <div className="flex justify-between mt-6 pt-4 border-t">
              <Button variant="outline" onClick={() => setEditMode(false)}>
                Cancel
              </Button>
              <Button onClick={() => handleUpdateModel({
                name: model.name,
                description: model.description,
                workflow_base_platform_fee: model.workflow_config?.base_platform_fee || 0,
                workflow_platform_fee_frequency: model.workflow_config?.platform_fee_frequency || 'monthly',
                workflow_volume_discount_enabled: model.workflow_config?.volume_discount_enabled || false,
                workflow_volume_discount_threshold: model.workflow_config?.volume_discount_threshold,
                workflow_volume_discount_percentage: model.workflow_config?.volume_discount_percentage,
                workflow_overage_multiplier: model.workflow_config?.overage_multiplier || 1.0,
                workflow_currency: model.workflow_config?.currency || 'USD',
                workflow_types: model.workflow_types,
                commitment_tiers: model.commitment_tiers
              })}>
                Save Changes
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        /* View Mode */
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="workflows">Workflows ({model.workflow_types?.length || 0})</TabsTrigger>
            <TabsTrigger value="tiers">Commitment Tiers ({model.commitment_tiers?.length || 0})</TabsTrigger>
            <TabsTrigger value="calculator">Cost Calculator</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <Settings className="h-4 w-4 text-orange-500" />
                    <span className="text-sm font-medium">Platform Fee</span>
                  </div>
                  <div className="text-2xl font-bold mt-1">
                    ${model.workflow_config?.base_platform_fee?.toLocaleString() || 0}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    per {model.workflow_config?.platform_fee_frequency || 'month'}
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <Zap className="h-4 w-4 text-blue-500" />
                    <span className="text-sm font-medium">Workflow Types</span>
                  </div>
                  <div className="text-2xl font-bold mt-1">
                    {calculateTotalWorkflows()}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Avg: ${calculateAverageWorkflowPrice().toFixed(2)}
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <Target className="h-4 w-4 text-green-500" />
                    <span className="text-sm font-medium">Commitment Tiers</span>
                  </div>
                  <div className="text-2xl font-bold mt-1">
                    {model.commitment_tiers?.length || 0}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    subscription options
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <Calculator className="h-4 w-4 text-purple-500" />
                    <span className="text-sm font-medium">Est. Margin</span>
                  </div>
                  <div className="text-2xl font-bold mt-1">
                    {calculateEstimatedMargin().toFixed(1)}%
                  </div>
                  <div className="text-xs text-muted-foreground">
                    across workflows
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Platform Configuration Details */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5" />
                  Platform Configuration
                </CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-3">
                  <div>
                    <span className="text-sm text-muted-foreground">Base Platform Fee</span>
                    <div className="font-mono text-lg">${model.workflow_config?.base_platform_fee?.toLocaleString() || 0}</div>
                  </div>
                  <div>
                    <span className="text-sm text-muted-foreground">Billing Frequency</span>
                    <div className="font-medium">{model.workflow_config?.platform_fee_frequency || 'monthly'}</div>
                  </div>
                  <div>
                    <span className="text-sm text-muted-foreground">Currency</span>
                    <div className="font-medium">{model.workflow_config?.currency || 'USD'}</div>
                  </div>
                </div>
                <div className="space-y-3">
                  <div>
                    <span className="text-sm text-muted-foreground">Volume Discount</span>
                    <div className="font-medium">
                      {model.workflow_config?.volume_discount_enabled ? (
                        <span className="text-green-600">
                          {model.workflow_config.volume_discount_percentage}% off at {model.workflow_config.volume_discount_threshold}+ workflows
                        </span>
                      ) : (
                        <span className="text-muted-foreground">Disabled</span>
                      )}
                    </div>
                  </div>
                  <div>
                    <span className="text-sm text-muted-foreground">Overage Multiplier</span>
                    <div className="font-medium">{model.workflow_config?.overage_multiplier || 1.0}x</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="workflows" className="space-y-4">
            {model.workflow_types && model.workflow_types.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {model.workflow_types.map((workflow: any) => (
                  <Card key={workflow.workflow_type}>
                    <CardHeader className="pb-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle className="text-lg">{workflow.workflow_name}</CardTitle>
                          <code className="text-xs text-muted-foreground">{workflow.workflow_type}</code>
                        </div>
                        <Badge className={getComplexityColor(workflow.complexity_level)}>
                          {workflow.complexity_level}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <p className="text-sm text-muted-foreground">{workflow.description}</p>
                      
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-muted-foreground">Base Price</span>
                          <div className="font-mono font-medium">${workflow.price_per_workflow.toFixed(2)}</div>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Min Charge</span>
                          <div className="font-mono">${workflow.minimum_charge.toFixed(2)}</div>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Duration</span>
                          <div>{workflow.estimated_duration_minutes}min</div>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Compute Cost</span>
                          <div className="font-mono">${workflow.estimated_compute_cost?.toFixed(2) || '0.00'}</div>
                        </div>
                      </div>
                      
                      {workflow.volume_tier_1_threshold && (
                        <div className="space-y-1 text-xs">
                          <div className="text-muted-foreground">Volume Pricing:</div>
                          <div>Tier 1 ({workflow.volume_tier_1_threshold}+): ${workflow.volume_tier_1_price?.toFixed(2)}</div>
                          {workflow.volume_tier_2_threshold && (
                            <div>Tier 2 ({workflow.volume_tier_2_threshold}+): ${workflow.volume_tier_2_price?.toFixed(2)}</div>
                          )}
                          {workflow.volume_tier_3_threshold && (
                            <div>Tier 3 ({workflow.volume_tier_3_threshold}+): ${workflow.volume_tier_3_price?.toFixed(2)}</div>
                          )}
                        </div>
                      )}
                      
                      <div className="flex gap-2">
                        <Badge variant="outline" className="text-xs">
                          {workflow.business_value_category?.replace('_', ' ')}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          ROI: {workflow.expected_roi_multiplier}x
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <Zap className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
                <h3 className="text-lg font-medium mb-2">No Workflow Types</h3>
                <p className="text-muted-foreground mb-4">Add workflow types to define your pricing structure</p>
                <Button onClick={() => setEditMode(true)}>
                  <Edit className="h-4 w-4 mr-2" />
                  Add Workflow Types
                </Button>
              </div>
            )}
          </TabsContent>

          <TabsContent value="tiers" className="space-y-4">
            {model.commitment_tiers && model.commitment_tiers.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {model.commitment_tiers
                  .sort((a: any, b: any) => a.tier_level - b.tier_level)
                  .map((tier: any) => (
                  <Card key={tier.tier_level} className={tier.is_popular ? 'border-orange-200 bg-orange-50/50' : ''}>
                    <CardHeader>
                      <div className="flex justify-between items-center">
                        <CardTitle className="flex items-center gap-2">
                          {tier.tier_name}
                          {tier.is_popular && <Badge className="bg-orange-100 text-orange-700">Popular</Badge>}
                        </CardTitle>
                        <span className="text-sm text-muted-foreground">Level {tier.tier_level}</span>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <p className="text-sm text-muted-foreground">{tier.description}</p>
                      
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Min Workflows/Month</span>
                          <span className="font-medium">{tier.minimum_workflows_per_month.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Min Monthly Revenue</span>
                          <span className="font-medium">${tier.minimum_monthly_revenue.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Included Workflows</span>
                          <span className="font-medium">{tier.included_workflows.toLocaleString()}</span>
                        </div>
                        {tier.discount_percentage > 0 && (
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Discount</span>
                            <span className="font-medium text-green-600">{tier.discount_percentage}%</span>
                          </div>
                        )}
                        {tier.platform_fee_discount > 0 && (
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Platform Discount</span>
                            <span className="font-medium text-green-600">${tier.platform_fee_discount}</span>
                          </div>
                        )}
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Contract Period</span>
                          <span className="font-medium">{tier.commitment_period_months}mo</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <Target className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
                <h3 className="text-lg font-medium mb-2">No Commitment Tiers</h3>
                <p className="text-muted-foreground mb-4">Add commitment tiers to offer volume discounts and contracts</p>
                <Button onClick={() => setEditMode(true)}>
                  <Edit className="h-4 w-4 mr-2" />
                  Add Commitment Tiers
                </Button>
              </div>
            )}
          </TabsContent>

          <TabsContent value="calculator">
            <WorkflowCostCalculator model={{
              workflow_base_platform_fee: model.workflow_config?.base_platform_fee || 0,
              workflow_volume_discount_enabled: model.workflow_config?.volume_discount_enabled || false,
              workflow_volume_discount_threshold: model.workflow_config?.volume_discount_threshold,
              workflow_volume_discount_percentage: model.workflow_config?.volume_discount_percentage,
              workflow_overage_multiplier: model.workflow_config?.overage_multiplier || 1.0,
              workflow_currency: model.workflow_config?.currency || 'USD',
              workflow_types: model.workflow_types || []
            }} />
          </TabsContent>
        </Tabs>
      )}
    </div>
  )
}
