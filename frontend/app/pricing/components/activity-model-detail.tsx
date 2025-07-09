"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { ArrowLeft, Edit, Activity, DollarSign, TrendingUp, Zap, BarChart, Settings, Calculator } from "lucide-react"
import toast from "react-hot-toast"
import api from "@/utils/api"
import ActivityBasedForm from "./ActivityBasedForm"

interface ActivityModelDetailProps {
  modelId: number
  onBack: () => void
}

export default function ActivityModelDetail({ modelId, onBack }: ActivityModelDetailProps) {
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
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading activity model...</p>
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

  const getActivityConfig = () => {
    return model.activity_config?.[0] || {}
  }

  const activityConfig = getActivityConfig()

  const calculateEstimatedCost = (units: number) => {
    if (!activityConfig.volume_pricing_enabled) {
      return units * (activityConfig.price_per_unit || 0)
    }

    let cost = 0
    let remainingUnits = units

    // Tier 1
    if (activityConfig.volume_tier_1_threshold && activityConfig.volume_tier_1_price && remainingUnits > 0) {
      const tier1Units = Math.min(remainingUnits, activityConfig.volume_tier_1_threshold)
      cost += tier1Units * activityConfig.volume_tier_1_price
      remainingUnits -= tier1Units
    }

    // Tier 2
    if (activityConfig.volume_tier_2_threshold && activityConfig.volume_tier_2_price && remainingUnits > 0) {
      const tier2Units = Math.min(remainingUnits, activityConfig.volume_tier_2_threshold - (activityConfig.volume_tier_1_threshold || 0))
      cost += tier2Units * activityConfig.volume_tier_2_price
      remainingUnits -= tier2Units
    }

    // Tier 3
    if (activityConfig.volume_tier_3_threshold && activityConfig.volume_tier_3_price && remainingUnits > 0) {
      const tier3Units = Math.min(remainingUnits, activityConfig.volume_tier_3_threshold - (activityConfig.volume_tier_2_threshold || 0))
      cost += tier3Units * activityConfig.volume_tier_3_price
      remainingUnits -= tier3Units
    }

    // Remaining units at base price
    if (remainingUnits > 0) {
      cost += remainingUnits * (activityConfig.price_per_unit || 0)
    }

    return Math.max(cost, activityConfig.minimum_charge || 0)
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
          <Badge className="bg-blue/10 text-blue border-blue/20">
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
            <CardTitle>Edit Activity Billing Model</CardTitle>
          </CardHeader>
          <CardContent>
            <ActivityBasedForm 
              model={{
                activity_price_per_unit: activityConfig.price_per_unit || '',
                activity_activity_type: activityConfig.activity_type || '',
                activity_unit_type: activityConfig.unit_type || 'action',
                activity_base_agent_fee: activityConfig.base_agent_fee || '',
                activity_volume_pricing_enabled: activityConfig.volume_pricing_enabled || false,
                activity_volume_tier_1_threshold: activityConfig.volume_tier_1_threshold || '',
                activity_volume_tier_1_price: activityConfig.volume_tier_1_price || '',
                activity_volume_tier_2_threshold: activityConfig.volume_tier_2_threshold || '',
                activity_volume_tier_2_price: activityConfig.volume_tier_2_price || '',
                activity_volume_tier_3_threshold: activityConfig.volume_tier_3_threshold || '',
                activity_volume_tier_3_price: activityConfig.volume_tier_3_price || '',
                activity_minimum_charge: activityConfig.minimum_charge || '',
                activity_billing_frequency: activityConfig.billing_frequency || 'monthly',
                activity_is_active: activityConfig.is_active !== false
              }}
              setModel={(updatedModel) => {
                setModel({
                  ...model,
                  activity_config: [{
                    ...activityConfig,
                    price_per_unit: parseFloat(updatedModel.activity_price_per_unit) || 0,
                    activity_type: updatedModel.activity_activity_type,
                    unit_type: updatedModel.activity_unit_type,
                    base_agent_fee: parseFloat(updatedModel.activity_base_agent_fee) || 0,
                    volume_pricing_enabled: updatedModel.activity_volume_pricing_enabled,
                    volume_tier_1_threshold: parseInt(updatedModel.activity_volume_tier_1_threshold) || null,
                    volume_tier_1_price: parseFloat(updatedModel.activity_volume_tier_1_price) || null,
                    volume_tier_2_threshold: parseInt(updatedModel.activity_volume_tier_2_threshold) || null,
                    volume_tier_2_price: parseFloat(updatedModel.activity_volume_tier_2_price) || null,
                    volume_tier_3_threshold: parseInt(updatedModel.activity_volume_tier_3_threshold) || null,
                    volume_tier_3_price: parseFloat(updatedModel.activity_volume_tier_3_price) || null,
                    minimum_charge: parseFloat(updatedModel.activity_minimum_charge) || 0,
                    billing_frequency: updatedModel.activity_billing_frequency,
                    is_active: updatedModel.activity_is_active
                  }]
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
                activity_price_per_unit: activityConfig.price_per_unit || 0,
                activity_activity_type: activityConfig.activity_type,
                activity_unit_type: activityConfig.unit_type || 'action',
                activity_base_agent_fee: activityConfig.base_agent_fee || 0,
                activity_volume_pricing_enabled: activityConfig.volume_pricing_enabled || false,
                activity_volume_tier_1_threshold: activityConfig.volume_tier_1_threshold,
                activity_volume_tier_1_price: activityConfig.volume_tier_1_price,
                activity_volume_tier_2_threshold: activityConfig.volume_tier_2_threshold,
                activity_volume_tier_2_price: activityConfig.volume_tier_2_price,
                activity_volume_tier_3_threshold: activityConfig.volume_tier_3_threshold,
                activity_volume_tier_3_price: activityConfig.volume_tier_3_price,
                activity_minimum_charge: activityConfig.minimum_charge || 0,
                activity_billing_frequency: activityConfig.billing_frequency || 'monthly',
                activity_is_active: activityConfig.is_active !== false
              })}>
                Save Changes
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        /* View Mode */
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="pricing">Pricing Details</TabsTrigger>
            <TabsTrigger value="calculator">Cost Calculator</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <DollarSign className="h-4 w-4 text-blue-600" />
                    <span className="text-sm font-medium">Base Price</span>
                  </div>
                  <div className="text-2xl font-bold">${activityConfig.price_per_unit || 0}</div>
                  <div className="text-xs text-muted-foreground">per {activityConfig.unit_type || 'action'}</div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <Activity className="h-4 w-4 text-green-600" />
                    <span className="text-sm font-medium">Activity Type</span>
                  </div>
                  <div className="text-2xl font-bold">{activityConfig.activity_type || 'N/A'}</div>
                  <div className="text-xs text-muted-foreground">billing activity</div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-purple-600" />
                    <span className="text-sm font-medium">Volume Pricing</span>
                  </div>
                  <div className="text-2xl font-bold">
                    {activityConfig.volume_pricing_enabled ? 'Enabled' : 'Disabled'}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {activityConfig.volume_pricing_enabled ? 'tiered pricing' : 'flat rate'}
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <BarChart className="h-4 w-4 text-orange-600" />
                    <span className="text-sm font-medium">Min. Charge</span>
                  </div>
                  <div className="text-2xl font-bold">${activityConfig.minimum_charge || 0}</div>
                  <div className="text-xs text-muted-foreground">minimum billing</div>
                </CardContent>
              </Card>
            </div>

            {/* Configuration Details */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5" />
                  Configuration Details
                </CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-3">
                  <div>
                    <span className="text-sm font-medium text-muted-foreground">Activity Type:</span>
                    <p className="font-medium">{activityConfig.activity_type || 'Not specified'}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-muted-foreground">Unit Type:</span>
                    <p className="font-medium">{activityConfig.unit_type || 'action'}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-muted-foreground">Base Agent Fee:</span>
                    <p className="font-medium">${activityConfig.base_agent_fee || 0}</p>
                  </div>
                </div>
                <div className="space-y-3">
                  <div>
                    <span className="text-sm font-medium text-muted-foreground">Billing Frequency:</span>
                    <p className="font-medium capitalize">{activityConfig.billing_frequency || 'monthly'}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-muted-foreground">Status:</span>
                    <Badge className={activityConfig.is_active !== false ? "bg-green/10 text-green" : "bg-red/10 text-red"}>
                      {activityConfig.is_active !== false ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="pricing" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Pricing Structure</CardTitle>
                <CardDescription>
                  {activityConfig.volume_pricing_enabled 
                    ? "Volume-based tiered pricing with discounts for higher usage"
                    : "Flat rate pricing per unit"
                  }
                </CardDescription>
              </CardHeader>
              <CardContent>
                {activityConfig.volume_pricing_enabled ? (
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {activityConfig.volume_tier_1_threshold && (
                        <Card>
                          <CardContent className="p-4">
                            <div className="text-sm font-medium text-blue-600 mb-2">Tier 1</div>
                            <div className="text-lg font-bold">${activityConfig.volume_tier_1_price}</div>
                            <div className="text-xs text-muted-foreground">
                              First {activityConfig.volume_tier_1_threshold} {activityConfig.unit_type}s
                            </div>
                          </CardContent>
                        </Card>
                      )}
                      
                      {activityConfig.volume_tier_2_threshold && (
                        <Card>
                          <CardContent className="p-4">
                            <div className="text-sm font-medium text-purple-600 mb-2">Tier 2</div>
                            <div className="text-lg font-bold">${activityConfig.volume_tier_2_price}</div>
                            <div className="text-xs text-muted-foreground">
                              Next {(activityConfig.volume_tier_2_threshold - activityConfig.volume_tier_1_threshold)} {activityConfig.unit_type}s
                            </div>
                          </CardContent>
                        </Card>
                      )}
                      
                      {activityConfig.volume_tier_3_threshold && (
                        <Card>
                          <CardContent className="p-4">
                            <div className="text-sm font-medium text-green-600 mb-2">Tier 3</div>
                            <div className="text-lg font-bold">${activityConfig.volume_tier_3_price}</div>
                            <div className="text-xs text-muted-foreground">
                              Next {(activityConfig.volume_tier_3_threshold - activityConfig.volume_tier_2_threshold)} {activityConfig.unit_type}s
                            </div>
                          </CardContent>
                        </Card>
                      )}
                    </div>
                    
                    <div className="text-sm text-muted-foreground">
                      <strong>Note:</strong> Units beyond the highest tier are charged at the base rate of ${activityConfig.price_per_unit} per {activityConfig.unit_type}.
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="text-4xl font-bold text-blue-600 mb-2">
                      ${activityConfig.price_per_unit || 0}
                    </div>
                    <div className="text-lg text-muted-foreground">
                      per {activityConfig.unit_type || 'action'}
                    </div>
                    <div className="text-sm text-muted-foreground mt-2">
                      Flat rate pricing - same price for all units
                    </div>
                  </div>
                )}
                
                {activityConfig.minimum_charge > 0 && (
                  <div className="mt-4 p-3 bg-orange/10 rounded-lg border border-orange/20">
                    <div className="text-sm font-medium text-orange-800">Minimum Charge</div>
                    <div className="text-xs text-orange-600">
                      A minimum charge of ${activityConfig.minimum_charge} applies regardless of usage.
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="calculator">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calculator className="h-5 w-5" />
                  Cost Calculator
                </CardTitle>
                <CardDescription>
                  Calculate costs based on your expected usage
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium">Number of {activityConfig.unit_type || 'action'}s</label>
                      <input
                        type="number"
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        placeholder="Enter quantity"
                        onChange={(e) => {
                          const units = parseInt(e.target.value) || 0
                          const cost = calculateEstimatedCost(units)
                          const resultEl = document.getElementById('cost-result')
                          if (resultEl) {
                            resultEl.textContent = `$${cost.toFixed(2)}`
                          }
                        }}
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium">Estimated Cost</label>
                      <div id="cost-result" className="mt-1 text-2xl font-bold text-blue-600">
                        $0.00
                      </div>
                    </div>
                  </div>
                  
                  {activityConfig.base_agent_fee > 0 && (
                    <div className="text-sm text-muted-foreground">
                      <strong>Note:</strong> Base agent fee of ${activityConfig.base_agent_fee} per agent applies in addition to usage costs.
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  )
}
