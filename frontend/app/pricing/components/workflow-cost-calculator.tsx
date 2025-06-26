"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Calculator, Zap, Target, DollarSign } from "lucide-react"

interface WorkflowType {
  workflow_name: string
  workflow_type: string
  price_per_workflow: number
  volume_tier_1_threshold?: number | null
  volume_tier_1_price?: number | null
  volume_tier_2_threshold?: number | null
  volume_tier_2_price?: number | null
  volume_tier_3_threshold?: number | null
  volume_tier_3_price?: number | null
  minimum_charge: number
  is_active: boolean
}

interface WorkflowBillingModel {
  workflow_base_platform_fee: number
  workflow_volume_discount_enabled: boolean
  workflow_volume_discount_threshold?: number
  workflow_volume_discount_percentage?: number
  workflow_overage_multiplier: number
  workflow_currency: string
  workflow_types: WorkflowType[]
}

interface WorkflowCostCalculatorProps {
  model: WorkflowBillingModel
}

export default function WorkflowCostCalculator({ model }: WorkflowCostCalculatorProps) {
  const [workflowUsage, setWorkflowUsage] = useState<Record<string, number>>({})
  const [costBreakdown, setCostBreakdown] = useState<any>(null)

  useEffect(() => {
    calculateCost()
  }, [workflowUsage, model])

  const calculateWorkflowCost = (workflowType: WorkflowType, count: number) => {
    if (count <= 0) return 0

    let cost = 0
    let remaining = count

    // Apply volume pricing if configured
    if (workflowType.volume_tier_1_threshold && workflowType.volume_tier_1_price !== null && workflowType.volume_tier_1_price !== undefined) {
      // Tier 1
      const tier1Count = Math.min(remaining, workflowType.volume_tier_1_threshold)
      cost += tier1Count * workflowType.volume_tier_1_price
      remaining -= tier1Count

      // Tier 2
      if (workflowType.volume_tier_2_threshold && workflowType.volume_tier_2_price !== null && workflowType.volume_tier_2_price !== undefined && remaining > 0) {
        const tier2Count = Math.min(remaining, workflowType.volume_tier_2_threshold - workflowType.volume_tier_1_threshold)
        cost += tier2Count * workflowType.volume_tier_2_price
        remaining -= tier2Count

        // Tier 3
        if (workflowType.volume_tier_3_threshold && workflowType.volume_tier_3_price !== null && workflowType.volume_tier_3_price !== undefined && remaining > 0) {
          const tier3Count = Math.min(remaining, workflowType.volume_tier_3_threshold - workflowType.volume_tier_2_threshold)
          cost += tier3Count * workflowType.volume_tier_3_price
          remaining -= tier3Count
        }

        // Remaining at highest tier or base price
        if (remaining > 0) {
          const finalPrice = (workflowType.volume_tier_3_price !== null && workflowType.volume_tier_3_price !== undefined) ? workflowType.volume_tier_3_price : workflowType.price_per_workflow
          cost += remaining * finalPrice
        }
      } else if (remaining > 0) {
        // No tier 2, use base price for remaining
        cost += remaining * workflowType.price_per_workflow
      }
    } else {
      // No volume pricing, use base price
      cost = count * workflowType.price_per_workflow
    }

    // Apply minimum charge
    return Math.max(cost, workflowType.minimum_charge)
  }

  const calculateCost = () => {
    let totalCost = model.workflow_base_platform_fee || 0
    const workflowCosts: Record<string, number> = {}
    let totalWorkflows = 0

    // Calculate cost for each workflow type
    model.workflow_types.forEach(workflowType => {
      if (!workflowType.is_active) return
      
      const count = workflowUsage[workflowType.workflow_type] || 0
      if (count > 0) {
        workflowCosts[workflowType.workflow_type] = calculateWorkflowCost(workflowType, count)
        totalWorkflows += count
      }
    })

    const workflowSubtotal = Object.values(workflowCosts).reduce((sum, cost) => sum + cost, 0)
    let subtotal = totalCost + workflowSubtotal

    // Apply global volume discount
    let globalDiscount = 0
    if (model.workflow_volume_discount_enabled && 
        model.workflow_volume_discount_threshold && 
        model.workflow_volume_discount_percentage &&
        totalWorkflows >= model.workflow_volume_discount_threshold) {
      globalDiscount = subtotal * (model.workflow_volume_discount_percentage / 100)
      subtotal -= globalDiscount
    }

    setCostBreakdown({
      platformFee: model.workflow_base_platform_fee || 0,
      workflowCosts,
      workflowSubtotal,
      totalWorkflows,
      globalDiscount,
      totalCost: subtotal,
      currency: model.workflow_currency || 'USD'
    })
  }

  const updateWorkflowUsage = (workflowType: string, count: number) => {
    setWorkflowUsage(prev => ({
      ...prev,
      [workflowType]: Math.max(0, count)
    }))
  }

  const presetExamples = [
    {
      name: "Small Business",
      usage: {
        lead_research: 25,
        email_personalization: 50,
        linkedin_outreach: 10,
        meeting_booking: 3
      }
    },
    {
      name: "Growing Team",
      usage: {
        lead_research: 150,
        email_personalization: 300,
        linkedin_outreach: 75,
        meeting_booking: 15
      }
    },
    {
      name: "Enterprise",
      usage: {
        lead_research: 800,
        email_personalization: 1200,
        linkedin_outreach: 400,
        meeting_booking: 50
      }
    }
  ]

  const loadPreset = (preset: any) => {
    setWorkflowUsage(preset.usage)
  }

  if (!model.workflow_types || model.workflow_types.length === 0) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <div className="text-center text-muted-foreground">
            <Calculator className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>Add workflow types to see cost calculations</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Cost Calculator */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calculator className="h-5 w-5" />
            Workflow Cost Calculator
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Preset Examples */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Quick Examples:</label>
            <div className="flex gap-2 flex-wrap">
              {presetExamples.map((preset) => (
                <Button
                  key={preset.name}
                  variant="outline"
                  size="sm"
                  onClick={() => loadPreset(preset)}
                >
                  {preset.name}
                </Button>
              ))}
              <Button
                variant="outline"
                size="sm"
                onClick={() => setWorkflowUsage({})}
              >
                Clear All
              </Button>
            </div>
          </div>

          {/* Workflow Usage Inputs */}
          <div className="space-y-4">
            <h4 className="font-medium">Monthly Workflow Usage</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {model.workflow_types
                .filter(wt => wt.is_active)
                .map((workflowType) => (
                <div key={workflowType.workflow_type} className="space-y-2">
                  <label className="text-sm font-medium flex items-center gap-2">
                    <Zap className="h-4 w-4" />
                    {workflowType.workflow_name}
                  </label>
                  <Input
                    type="number"
                    placeholder="0"
                    min="0"
                    value={workflowUsage[workflowType.workflow_type] || ''}
                    onChange={(e) => updateWorkflowUsage(
                      workflowType.workflow_type, 
                      parseInt(e.target.value) || 0
                    )}
                  />
                  <div className="text-xs text-muted-foreground">
                    Base: ${workflowType.price_per_workflow.toFixed(2)} per workflow
                    {workflowType.volume_tier_1_threshold && (
                      <div>Volume: {workflowType.volume_tier_1_threshold}+ at ${workflowType.volume_tier_1_price?.toFixed(2)}</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Cost Breakdown */}
          {costBreakdown && (
            <div className="space-y-4 bg-muted/30 p-4 rounded-lg">
              <h4 className="font-medium flex items-center gap-2">
                <DollarSign className="h-4 w-4" />
                Cost Breakdown
              </h4>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Base Platform Fee</span>
                  <span className="font-mono">${costBreakdown.platformFee.toFixed(2)}</span>
                </div>
                
                {Object.entries(costBreakdown.workflowCosts).map(([workflowType, cost]) => {
                  const workflow = model.workflow_types.find(wt => wt.workflow_type === workflowType)
                  const count = workflowUsage[workflowType] || 0
                  return (
                    <div key={workflowType} className="flex justify-between pl-4">
                      <span>
                        {workflow?.workflow_name} ({count.toLocaleString()})
                      </span>
                      <span className="font-mono">${(cost as number).toFixed(2)}</span>
                    </div>
                  )
                })}
                
                {costBreakdown.workflowSubtotal > 0 && (
                  <div className="flex justify-between border-t pt-2">
                    <span>Workflow Subtotal</span>
                    <span className="font-mono">${costBreakdown.workflowSubtotal.toFixed(2)}</span>
                  </div>
                )}
                
                {costBreakdown.globalDiscount > 0 && (
                  <>
                    <div className="flex justify-between text-green-600">
                      <span>
                        Global Volume Discount ({costBreakdown.totalWorkflows.toLocaleString()} workflows)
                      </span>
                      <span className="font-mono">-${costBreakdown.globalDiscount.toFixed(2)}</span>
                    </div>
                  </>
                )}
                
                <div className="flex justify-between font-medium text-lg border-t pt-2">
                  <span>Total Monthly Cost</span>
                  <span className="font-mono">${costBreakdown.totalCost.toFixed(2)} {costBreakdown.currency}</span>
                </div>
                
                {costBreakdown.totalWorkflows > 0 && (
                  <div className="flex justify-between text-muted-foreground text-xs">
                    <span>Cost per workflow</span>
                    <span className="font-mono">
                      ${(costBreakdown.totalCost / costBreakdown.totalWorkflows).toFixed(3)}
                    </span>
                  </div>
                )}
              </div>
              
              {/* Volume Discount Info */}
              {model.workflow_volume_discount_enabled && model.workflow_volume_discount_threshold && (
                <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded text-sm">
                  <Target className="h-4 w-4 inline mr-2 text-blue-600" />
                  <span className="text-blue-700">
                    {costBreakdown.totalWorkflows >= model.workflow_volume_discount_threshold ? (
                      <span className="font-medium">✅ Volume discount applied! </span>
                    ) : (
                      <span>
                        Use {(model.workflow_volume_discount_threshold - costBreakdown.totalWorkflows).toLocaleString()} more workflows for {model.workflow_volume_discount_percentage}% discount
                      </span>
                    )}
                  </span>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
