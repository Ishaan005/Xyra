"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { 
  TrendingUp, 
  DollarSign, 
  Clock, 
  Shield, 
  Target, 
  Zap,
  Info,
  AlertTriangle,
  Award
} from "lucide-react"

interface OutcomeBasedFormProps {
  model: any
  setModel: (model: any) => void
}

export default function OutcomeBasedForm({ model, setModel }: OutcomeBasedFormProps) {
  const [showAdvanced, setShowAdvanced] = useState(false)
  
  const updateField = (field: string, value: any) => {
    setModel((prev: any) => ({ ...prev, [field]: value }))
  }

  const outcomeTypes = [
    { value: "revenue_uplift", label: "Revenue Uplift", description: "Increased revenue generated" },
    { value: "cost_savings", label: "Cost Savings", description: "Operational cost reductions" },
    { value: "lead_generation", label: "Lead Generation", description: "New leads generated" },
    { value: "conversion_rate", label: "Conversion Rate", description: "Improved conversion rates" },
    { value: "time_savings", label: "Time Savings", description: "Hours saved in operations" },
    { value: "customer_satisfaction", label: "Customer Satisfaction", description: "Improved CSAT scores" },
    { value: "custom", label: "Custom Outcome", description: "Define your own outcome type" }
  ]

  const billingFrequencies = [
    { value: "monthly", label: "Monthly" },
    { value: "quarterly", label: "Quarterly" },
    { value: "annually", label: "Annually" },
    { value: "per_outcome", label: "Per Outcome" }
  ]

  const currencies = [
    { value: "USD", label: "USD ($)" },
    { value: "EUR", label: "EUR (€)" },
    { value: "GBP", label: "GBP (£)" },
    { value: "CAD", label: "CAD (C$)" }
  ]

  return (
    <div className="space-y-6">
      {/* Basic Outcome Configuration */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Target className="h-5 w-5 text-blue-600" />
            <CardTitle>Outcome Definition</CardTitle>
          </div>
          <CardDescription>
            Define what success looks like and how you'll be compensated for it
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="outcome_name">Outcome Name</Label>
              <Input
                id="outcome_name"
                placeholder="e.g., Sales Lead Generation"
                value={model.outcome_outcome_name || ""}
                onChange={(e) => updateField("outcome_outcome_name", e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="outcome_type">Outcome Type</Label>
              <Select 
                value={model.outcome_outcome_type || ""} 
                onValueChange={(value) => updateField("outcome_outcome_type", value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select outcome type" />
                </SelectTrigger>
                <SelectContent>
                  {outcomeTypes.map((type) => (
                    <SelectItem key={type.value} value={type.value}>
                      <div className="flex flex-col">
                        <span>{type.label}</span>
                        <span className="text-xs text-muted-foreground">{type.description}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="outcome_description">Description</Label>
            <Input
              id="outcome_description"
              placeholder="Describe how this outcome is measured and attributed..."
              value={model.outcome_description || ""}
              onChange={(e) => updateField("outcome_description", e.target.value)}
            />
          </div>

          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              You can set a revenue share, a fixed charge, or both. If both are set, they will be combined.
            </AlertDescription>
          </Alert>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label htmlFor="outcome_percentage">Revenue Share %</Label>
              <div className="relative">
                <Input
                  id="outcome_percentage"
                  type="number"
                  placeholder="5.0"
                  min="0"
                  max="100"
                  step="0.1"
                  value={model.outcome_percentage || ""}
                  onChange={(e) => updateField("outcome_percentage", e.target.value)}
                />
                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">%</span>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="outcome_fixed_charge">Fixed Charge</Label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">$</span>
                <Input
                  id="outcome_fixed_charge"
                  type="number"
                  placeholder="10.00"
                  min="0"
                  step="0.01"
                  className="pl-7"
                  value={model.outcome_fixed_charge_per_outcome || ""}
                  onChange={(e) => updateField("outcome_fixed_charge_per_outcome", e.target.value)}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="outcome_currency">Currency</Label>
              <Select 
                value={model.outcome_currency || "USD"} 
                onValueChange={(value) => updateField("outcome_currency", value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {currencies.map((currency) => (
                    <SelectItem key={currency.value} value={currency.value}>
                      {currency.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="outcome_billing_frequency">Billing Frequency</Label>
              <Select 
                value={model.outcome_billing_frequency || "monthly"} 
                onValueChange={(value) => updateField("outcome_billing_frequency", value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {billingFrequencies.map((freq) => (
                    <SelectItem key={freq.value} value={freq.value}>
                      {freq.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Base Platform Fee */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <DollarSign className="h-5 w-5 text-green-600" />
            <CardTitle>Base Platform Fee</CardTitle>
          </div>
          <CardDescription>
            Optional fixed fee to ensure minimum revenue regardless of outcomes
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="outcome_base_platform_fee">Monthly Base Fee</Label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">$</span>
                <Input
                  id="outcome_base_platform_fee"
                  type="number"
                  placeholder="0.00"
                  min="0"
                  step="0.01"
                  className="pl-7"
                  value={model.outcome_base_platform_fee || ""}
                  onChange={(e) => updateField("outcome_base_platform_fee", e.target.value)}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="outcome_platform_fee_frequency">Base Fee Frequency</Label>
              <Select 
                value={model.outcome_platform_fee_frequency || "monthly"} 
                onValueChange={(value) => updateField("outcome_platform_fee_frequency", value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {billingFrequencies.filter(f => f.value !== "per_outcome").map((freq) => (
                    <SelectItem key={freq.value} value={freq.value}>
                      {freq.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Advanced Options Toggle */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Zap className="h-4 w-4 text-purple-600" />
          <span className="font-medium">Advanced Pricing Features</span>
        </div>
        <Button 
          variant="outline" 
          size="sm"
          onClick={() => setShowAdvanced(!showAdvanced)}
        >
          {showAdvanced ? "Hide Advanced" : "Show Advanced"}
        </Button>
      </div>

      {showAdvanced && (
        <>
          {/* Multi-Tier Pricing */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-purple-600" />
                <CardTitle>Multi-Tier Pricing</CardTitle>
              </div>
              <CardDescription>
                Set different percentages based on outcome value thresholds
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="bg-blue-50">Tier 1</Badge>
                    <span className="text-sm text-muted-foreground">Low Value</span>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="tier1_threshold">Threshold ($)</Label>
                    <Input
                      id="tier1_threshold"
                      type="number"
                      placeholder="1000"
                      min="0"
                      value={model.outcome_tier_1_threshold || ""}
                      onChange={(e) => updateField("outcome_tier_1_threshold", e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="tier1_percentage">Percentage (%)</Label>
                    <Input
                      id="tier1_percentage"
                      type="number"
                      placeholder="3.0"
                      min="0"
                      max="100"
                      step="0.1"
                      value={model.outcome_tier_1_percentage || ""}
                      onChange={(e) => updateField("outcome_tier_1_percentage", e.target.value)}
                    />
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="bg-purple-50">Tier 2</Badge>
                    <span className="text-sm text-muted-foreground">Medium Value</span>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="tier2_threshold">Threshold ($)</Label>
                    <Input
                      id="tier2_threshold"
                      type="number"
                      placeholder="5000"
                      min="0"
                      value={model.outcome_tier_2_threshold || ""}
                      onChange={(e) => updateField("outcome_tier_2_threshold", e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="tier2_percentage">Percentage (%)</Label>
                    <Input
                      id="tier2_percentage"
                      type="number"
                      placeholder="5.0"
                      min="0"
                      max="100"
                      step="0.1"
                      value={model.outcome_tier_2_percentage || ""}
                      onChange={(e) => updateField("outcome_tier_2_percentage", e.target.value)}
                    />
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="bg-gold-50">Tier 3</Badge>
                    <span className="text-sm text-muted-foreground">High Value</span>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="tier3_threshold">Threshold ($)</Label>
                    <Input
                      id="tier3_threshold"
                      type="number"
                      placeholder="10000"
                      min="0"
                      value={model.outcome_tier_3_threshold || ""}
                      onChange={(e) => updateField("outcome_tier_3_threshold", e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="tier3_percentage">Percentage (%)</Label>
                    <Input
                      id="tier3_percentage"
                      type="number"
                      placeholder="7.0"
                      min="0"
                      max="100"
                      step="0.1"
                      value={model.outcome_tier_3_percentage || ""}
                      onChange={(e) => updateField("outcome_tier_3_percentage", e.target.value)}
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Risk and Performance */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-orange-600" />
                <CardTitle>Risk & Performance Management</CardTitle>
              </div>
              <CardDescription>
                Configure risk premiums, caps, and performance bonuses
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="risk_premium">Risk Premium (%)</Label>
                  <div className="relative">
                    <Input
                      id="risk_premium"
                      type="number"
                      placeholder="1.5"
                      min="0"
                      max="100"
                      step="0.1"
                      value={model.outcome_risk_premium_percentage || ""}
                      onChange={(e) => updateField("outcome_risk_premium_percentage", e.target.value)}
                    />
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">%</span>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Additional percentage for higher-risk outcomes
                  </p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="success_rate">Expected Success Rate (%)</Label>
                  <div className="relative">
                    <Input
                      id="success_rate"
                      type="number"
                      placeholder="85"
                      min="0"
                      max="100"
                      step="0.1"
                      value={model.outcome_success_rate_assumption || ""}
                      onChange={(e) => updateField("outcome_success_rate_assumption", e.target.value)}
                    />
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">%</span>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Assumed success rate for pricing calculations
                  </p>
                </div>
              </div>

              <Separator />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="monthly_cap">Monthly Cap ($)</Label>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">$</span>
                    <Input
                      id="monthly_cap"
                      type="number"
                      placeholder="10000"
                      min="0"
                      className="pl-7"
                      value={model.outcome_monthly_cap_amount || ""}
                      onChange={(e) => updateField("outcome_monthly_cap_amount", e.target.value)}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Maximum amount to charge per month
                  </p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="min_attribution">Minimum Attribution Value ($)</Label>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">$</span>
                    <Input
                      id="min_attribution"
                      type="number"
                      placeholder="100"
                      min="0"
                      className="pl-7"
                      value={model.outcome_minimum_attribution_value || ""}
                      onChange={(e) => updateField("outcome_minimum_attribution_value", e.target.value)}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Minimum outcome value to count for billing
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Success Bonus */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Award className="h-5 w-5 text-gold" />
                <CardTitle>Success Bonus</CardTitle>
              </div>
              <CardDescription>
                Reward exceptional performance with bonus percentages
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="bonus_threshold">Bonus Threshold ($)</Label>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">$</span>
                    <Input
                      id="bonus_threshold"
                      type="number"
                      placeholder="25000"
                      min="0"
                      className="pl-7"
                      value={model.outcome_success_bonus_threshold || ""}
                      onChange={(e) => updateField("outcome_success_bonus_threshold", e.target.value)}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Outcome value that triggers bonus
                  </p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="bonus_percentage">Bonus Percentage (%)</Label>
                  <div className="relative">
                    <Input
                      id="bonus_percentage"
                      type="number"
                      placeholder="2.0"
                      min="0"
                      max="100"
                      step="0.1"
                      value={model.outcome_success_bonus_percentage || ""}
                      onChange={(e) => updateField("outcome_success_bonus_percentage", e.target.value)}
                    />
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">%</span>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Additional percentage for high-value outcomes
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Attribution & Verification */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Clock className="h-5 w-5 text-blue-600" />
                <CardTitle>Attribution & Verification</CardTitle>
              </div>
              <CardDescription>
                Configure how outcomes are tracked and verified
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="attribution_window">Attribution Window (days)</Label>
                  <Input
                    id="attribution_window"
                    type="number"
                    placeholder="30"
                    min="1"
                    max="365"
                    value={model.outcome_attribution_window_days || ""}
                    onChange={(e) => updateField("outcome_attribution_window_days", e.target.value)}
                  />
                  <p className="text-xs text-muted-foreground">
                    Days to track outcomes after AI interaction
                  </p>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="requires_verification">Requires Verification</Label>
                    <Switch
                      id="requires_verification"
                      checked={model.outcome_requires_verification || false}
                      onCheckedChange={(checked) => updateField("outcome_requires_verification", checked)}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Outcomes must be manually verified before billing
                  </p>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="auto_bill">Auto-bill Verified Outcomes</Label>
                  <Switch
                    id="auto_bill"
                    checked={model.outcome_auto_bill_verified_outcomes || false}
                    onCheckedChange={(checked) => updateField("outcome_auto_bill_verified_outcomes", checked)}
                  />
                </div>
                <p className="text-xs text-muted-foreground">
                  Automatically bill customers when outcomes are verified
                </p>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="outcome_is_active">Active</Label>
                  <Switch
                    id="outcome_is_active"
                    checked={model.outcome_is_active !== false}
                    onCheckedChange={(checked) => updateField("outcome_is_active", checked)}
                  />
                </div>
                <p className="text-xs text-muted-foreground">
                  Enable or disable this outcome-based pricing model
                </p>
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {/* Pricing Preview */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Info className="h-5 w-5 text-blue-600" />
            <CardTitle>Pricing Preview</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <OutcomePricingPreview model={model} />
        </CardContent>
      </Card>
    </div>
  )
}

function OutcomePricingPreview({ model }: { model: any }) {
  const examples = [
    { value: 1000, label: "Small Outcome" },
    { value: 5000, label: "Medium Outcome" },
    { value: 15000, label: "Large Outcome" },
    { value: 50000, label: "Enterprise Outcome" }
  ]

  const calculateFee = (outcomeValue: number) => {
    let fee = 0
    const basePercentage = parseFloat(model.outcome_percentage || "0")
    
    // Check tiers
    const tier1Threshold = parseFloat(model.outcome_tier_1_threshold || "0")
    const tier2Threshold = parseFloat(model.outcome_tier_2_threshold || "0")
    const tier3Threshold = parseFloat(model.outcome_tier_3_threshold || "0")
    
    let percentage = basePercentage
    
    if (tier3Threshold && outcomeValue >= tier3Threshold) {
      percentage = parseFloat(model.outcome_tier_3_percentage || basePercentage.toString())
    } else if (tier2Threshold && outcomeValue >= tier2Threshold) {
      percentage = parseFloat(model.outcome_tier_2_percentage || basePercentage.toString())
    } else if (tier1Threshold && outcomeValue >= tier1Threshold) {
      percentage = parseFloat(model.outcome_tier_1_percentage || basePercentage.toString())
    }
    
    fee = (outcomeValue * percentage) / 100
    
    // Add risk premium
    const riskPremium = parseFloat(model.outcome_risk_premium_percentage || "0")
    if (riskPremium > 0) {
      fee += (outcomeValue * riskPremium) / 100
    }
    
    // Add success bonus
    const bonusThreshold = parseFloat(model.outcome_success_bonus_threshold || "0")
    const bonusPercentage = parseFloat(model.outcome_success_bonus_percentage || "0")
    if (bonusThreshold && bonusPercentage && outcomeValue >= bonusThreshold) {
      fee += (outcomeValue * bonusPercentage) / 100
    }
    
    // Apply monthly cap
    const monthlyCap = parseFloat(model.outcome_monthly_cap_amount || "0")
    if (monthlyCap > 0) {
      fee = Math.min(fee, monthlyCap)
    }
    
    return fee
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {examples.map((example) => {
          const fee = calculateFee(example.value)
          const effectiveRate = ((fee / example.value) * 100).toFixed(2)
          
          return (
            <div key={example.value} className="p-4 bg-muted/50 rounded-lg">
              <div className="text-sm font-medium text-muted-foreground mb-1">
                {example.label}
              </div>
              <div className="text-lg font-bold">
                ${example.value.toLocaleString()}
              </div>
              <div className="text-sm text-green-600 font-medium">
                Fee: ${fee.toFixed(2)}
              </div>
              <div className="text-xs text-muted-foreground">
                ({effectiveRate}%)
              </div>
            </div>
          )
        })}
      </div>
      
      {model.outcome_base_platform_fee && parseFloat(model.outcome_base_platform_fee) > 0 && (
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>
            Plus ${parseFloat(model.outcome_base_platform_fee).toFixed(2)} base platform fee {model.outcome_platform_fee_frequency || "monthly"}
          </AlertDescription>
        </Alert>
      )}
      
      {model.outcome_monthly_cap_amount && parseFloat(model.outcome_monthly_cap_amount) > 0 && (
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Monthly cap: ${parseFloat(model.outcome_monthly_cap_amount).toFixed(2)}
          </AlertDescription>
        </Alert>
      )}
    </div>
  )
}
