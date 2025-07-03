"use client";

import { useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, DollarSign, Calculator, Zap } from "lucide-react";

interface ActivityBasedFormProps {
  model: any;
  setModel: (model: any) => void;
}

export default function ActivityBasedForm({ model, setModel }: ActivityBasedFormProps) {
  // Initialize form with default values if model is empty or missing activity fields
  useEffect(() => {
    if (!model || !model.hasOwnProperty('activity_price_per_unit')) {
      setModel({
        ...model, // Preserve any existing data (like model_type)
        model_type: model?.model_type || 'activity',
        name: model?.name || '',
        description: model?.description || '',
        activity_price_per_unit: model?.activity_price_per_unit || 0,
        activity_activity_type: model?.activity_activity_type || 'api_call',
        activity_unit_type: model?.activity_unit_type || 'action',
        activity_base_agent_fee: model?.activity_base_agent_fee || 0,
        activity_minimum_charge: model?.activity_minimum_charge || 0,
        activity_billing_frequency: model?.activity_billing_frequency || 'monthly',
        activity_volume_pricing_enabled: model?.activity_volume_pricing_enabled || false,
        activity_volume_tier_1_threshold: model?.activity_volume_tier_1_threshold || 0,
        activity_volume_tier_1_price: model?.activity_volume_tier_1_price || 0,
        activity_volume_tier_2_threshold: model?.activity_volume_tier_2_threshold || 0,
        activity_volume_tier_2_price: model?.activity_volume_tier_2_price || 0,
        activity_volume_tier_3_threshold: model?.activity_volume_tier_3_threshold || 0,
        activity_volume_tier_3_price: model?.activity_volume_tier_3_price || 0,
      });
    }
  }, [model, setModel]);

  const handleInputChange = (field: string, value: any) => {
    setModel({ ...model, [field]: value });
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <Activity className="h-4 w-4 text-purple-500" />
        <h3 className="text-sm font-medium text-muted-foreground">Activity-Based Configuration</h3>
        <Badge variant="outline" className="text-xs">Pay Per Use</Badge>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {/* Basic Information */}
        <div className="space-y-4 p-4 border rounded-lg">
          <h4 className="text-sm font-medium text-muted-foreground">Basic Information</h4>
          
          <div className="space-y-2">
            <Label htmlFor="model-name" className="text-sm font-medium">
              Model Name *
            </Label>
            <Input
              id="model-name"
              type="text"
              placeholder="e.g., Activity-Based API Plan"
              value={model.name || ""}
              onChange={(e) => handleInputChange("name", e.target.value)}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="model-description" className="text-sm font-medium">
              Description
            </Label>
            <Input
              id="model-description"
              type="text"
              placeholder="Brief description of this pricing model"
              value={model.description || ""}
              onChange={(e) => handleInputChange("description", e.target.value)}
            />
          </div>
        </div>

        <Separator />

        {/* Price per Unit */}
        <div className="space-y-2">
          <Label htmlFor="activity-price-per-unit" className="text-sm font-medium flex items-center gap-2">
            <DollarSign className="h-3 w-3" />
            Price per Unit (USD)
          </Label>
          <Input
            id="activity-price-per-unit"
            type="number"
            step="0.001"
            min="0"
            placeholder="e.g., 0.05"
            value={model.activity_price_per_unit !== undefined ? model.activity_price_per_unit.toString() : ""}
            onChange={(e) => {
              const value = e.target.value;
              if (value === "") {
                handleInputChange("activity_price_per_unit", "");
              } else {
                const numValue = parseFloat(value);
                if (!isNaN(numValue)) {
                  handleInputChange("activity_price_per_unit", numValue);
                }
              }
            }}
          />
          <p className="text-xs text-muted-foreground">
            Cost per individual unit of activity
          </p>
        </div>

        {/* Activity Type */}
        <div className="space-y-2">
          <Label htmlFor="activity-type" className="text-sm font-medium">
            Activity Type
          </Label>
          <Select
            value={model.activity_activity_type || "api_call"}
            onValueChange={(value) => handleInputChange("activity_activity_type", value)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select activity type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="api_call">
                <div className="flex items-center gap-2">
                  <Zap className="h-3 w-3" />
                  <span>API Call</span>
                </div>
              </SelectItem>
              <SelectItem value="query">
                <div className="flex items-center gap-2">
                  <span>Query</span>
                </div>
              </SelectItem>
              <SelectItem value="completion">
                <div className="flex items-center gap-2">
                  <span>Completion</span>
                </div>
              </SelectItem>
              <SelectItem value="tokens">
                <div className="flex items-center gap-2">
                  <span>Tokens</span>
                </div>
              </SelectItem>
              <SelectItem value="execution">
                <div className="flex items-center gap-2">
                  <span>Execution</span>
                </div>
              </SelectItem>
              <SelectItem value="analysis">
                <div className="flex items-center gap-2">
                  <span>Analysis</span>
                </div>
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Unit Type */}
        <div className="space-y-2">
          <Label htmlFor="activity-unit-type" className="text-sm font-medium">
            Unit Type
          </Label>
          <Select
            value={model.activity_unit_type || "action"}
            onValueChange={(value) => handleInputChange("activity_unit_type", value)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select unit type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="action">Action</SelectItem>
              <SelectItem value="token">Token</SelectItem>
              <SelectItem value="minute">Minute</SelectItem>
              <SelectItem value="request">Request</SelectItem>
              <SelectItem value="query">Query</SelectItem>
              <SelectItem value="execution">Execution</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <Separator />

        {/* Base Agent Fee */}
        <div className="space-y-2">
          <Label htmlFor="activity-base-agent-fee" className="text-sm font-medium">
            Base Agent Fee (USD)
          </Label>
          <Input
            id="activity-base-agent-fee"
            type="number"
            step="0.01"
            min="0"
            placeholder="e.g., 50.00"
            value={model.activity_base_agent_fee !== undefined ? model.activity_base_agent_fee.toString() : ""}
            onChange={(e) => {
              const value = e.target.value;
              if (value === "") {
                handleInputChange("activity_base_agent_fee", "");
              } else {
                const numValue = parseFloat(value);
                if (!isNaN(numValue)) {
                  handleInputChange("activity_base_agent_fee", numValue);
                }
              }
            }}
          />
          <p className="text-xs text-muted-foreground">
            Optional base monthly fee per agent (in addition to per-activity charges)
          </p>
        </div>

        {/* Minimum Charge */}
        <div className="space-y-2">
          <Label htmlFor="activity-minimum-charge" className="text-sm font-medium">
            Minimum Charge (USD)
          </Label>
          <Input
            id="activity-minimum-charge"
            type="number"
            step="0.01"
            min="0"
            placeholder="e.g., 10.00"
            value={model.activity_minimum_charge !== undefined ? model.activity_minimum_charge.toString() : ""}
            onChange={(e) => {
              const value = e.target.value;
              if (value === "") {
                handleInputChange("activity_minimum_charge", "");
              } else {
                const numValue = parseFloat(value);
                if (!isNaN(numValue)) {
                  handleInputChange("activity_minimum_charge", numValue);
                }
              }
            }}
          />
          <p className="text-xs text-muted-foreground">
            Minimum charge per billing period
          </p>
        </div>

        {/* Billing Frequency */}
        <div className="space-y-2">
          <Label htmlFor="activity-billing-frequency" className="text-sm font-medium">
            Billing Frequency
          </Label>
          <Select
            value={model.activity_billing_frequency || "monthly"}
            onValueChange={(value) => handleInputChange("activity_billing_frequency", value)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select billing frequency" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="daily">Daily</SelectItem>
              <SelectItem value="monthly">Monthly</SelectItem>
              <SelectItem value="per_use">Per Use (immediate)</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <Separator />

        {/* Volume Pricing Configuration */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="text-sm font-medium flex items-center gap-2">
                <Calculator className="h-3 w-3" />
                Volume Pricing
              </Label>
              <p className="text-xs text-muted-foreground">
                Tiered pricing based on usage volume
              </p>
            </div>
            <Switch
              checked={model.activity_volume_pricing_enabled || false}
              onCheckedChange={(checked) => handleInputChange("activity_volume_pricing_enabled", checked)}
            />
          </div>

          {model.activity_volume_pricing_enabled && (
            <div className="space-y-4 p-4 border rounded-lg bg-muted/20">
              <p className="text-sm font-medium">Volume Pricing Tiers</p>
              
              {/* Tier 1 */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="tier1-threshold" className="text-sm font-medium">
                    Tier 1 Threshold
                  </Label>
                  <Input
                    id="tier1-threshold"
                    type="number"
                    min="1"
                    placeholder="e.g., 1000"
                    value={model.activity_volume_tier_1_threshold !== undefined ? model.activity_volume_tier_1_threshold : ""}
                    onChange={(e) => {
                      const value = e.target.value;
                      if (value === "") {
                        handleInputChange("activity_volume_tier_1_threshold", 0);
                      } else {
                        const numValue = parseInt(value);
                        handleInputChange("activity_volume_tier_1_threshold", isNaN(numValue) ? 0 : numValue);
                      }
                    }}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="tier1-price" className="text-sm font-medium">
                    Tier 1 Price
                  </Label>
                  <Input
                    id="tier1-price"
                    type="number"
                    step="0.001"
                    min="0"
                    placeholder="e.g., 0.04"
                    value={model.activity_volume_tier_1_price !== undefined ? model.activity_volume_tier_1_price : ""}
                    onChange={(e) => {
                      const value = e.target.value;
                      if (value === "") {
                        handleInputChange("activity_volume_tier_1_price", 0);
                      } else {
                        const numValue = parseFloat(value);
                        handleInputChange("activity_volume_tier_1_price", isNaN(numValue) ? 0 : numValue);
                      }
                    }}
                  />
                </div>
              </div>

              {/* Tier 2 */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="tier2-threshold" className="text-sm font-medium">
                    Tier 2 Threshold
                  </Label>
                  <Input
                    id="tier2-threshold"
                    type="number"
                    min="1"
                    placeholder="e.g., 5000"
                    value={model.activity_volume_tier_2_threshold !== undefined ? model.activity_volume_tier_2_threshold : ""}
                    onChange={(e) => {
                      const value = e.target.value;
                      if (value === "") {
                        handleInputChange("activity_volume_tier_2_threshold", 0);
                      } else {
                        const numValue = parseInt(value);
                        handleInputChange("activity_volume_tier_2_threshold", isNaN(numValue) ? 0 : numValue);
                      }
                    }}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="tier2-price" className="text-sm font-medium">
                    Tier 2 Price
                  </Label>
                  <Input
                    id="tier2-price"
                    type="number"
                    step="0.001"
                    min="0"
                    placeholder="e.g., 0.03"
                    value={model.activity_volume_tier_2_price !== undefined ? model.activity_volume_tier_2_price : ""}
                    onChange={(e) => {
                      const value = e.target.value;
                      if (value === "") {
                        handleInputChange("activity_volume_tier_2_price", 0);
                      } else {
                        const numValue = parseFloat(value);
                        handleInputChange("activity_volume_tier_2_price", isNaN(numValue) ? 0 : numValue);
                      }
                    }}
                  />
                </div>
              </div>

              {/* Tier 3 */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="tier3-threshold" className="text-sm font-medium">
                    Tier 3 Threshold
                  </Label>
                  <Input
                    id="tier3-threshold"
                    type="number"
                    min="1"
                    placeholder="e.g., 10000"
                    value={model.activity_volume_tier_3_threshold !== undefined ? model.activity_volume_tier_3_threshold : ""}
                    onChange={(e) => {
                      const value = e.target.value;
                      if (value === "") {
                        handleInputChange("activity_volume_tier_3_threshold", 0);
                      } else {
                        const numValue = parseInt(value);
                        handleInputChange("activity_volume_tier_3_threshold", isNaN(numValue) ? 0 : numValue);
                      }
                    }}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="tier3-price" className="text-sm font-medium">
                    Tier 3 Price
                  </Label>
                  <Input
                    id="tier3-price"
                    type="number"
                    step="0.001"
                    min="0"
                    placeholder="e.g., 0.02"
                    value={model.activity_volume_tier_3_price !== undefined ? model.activity_volume_tier_3_price : ""}
                    onChange={(e) => {
                      const value = e.target.value;
                      if (value === "") {
                        handleInputChange("activity_volume_tier_3_price", 0);
                      } else {
                        const numValue = parseFloat(value);
                        handleInputChange("activity_volume_tier_3_price", isNaN(numValue) ? 0 : numValue);
                      }
                    }}
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Pricing Preview */}
        <Card className="bg-muted/30">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <Calculator className="h-4 w-4" />
              Pricing Preview
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Base price per {model.activity_unit_type || "action"}:</span>
                <span className="font-medium">${(model.activity_price_per_unit || 0).toFixed(3)}</span>
              </div>
              {model.activity_base_agent_fee > 0 && (
                <div className="flex justify-between">
                  <span>Base agent fee:</span>
                  <span className="font-medium">${(model.activity_base_agent_fee || 0).toFixed(2)}/month</span>
                </div>
              )}
              {model.activity_minimum_charge > 0 && (
                <div className="flex justify-between">
                  <span>Minimum charge:</span>
                  <span className="font-medium">${(model.activity_minimum_charge || 0).toFixed(2)}</span>
                </div>
              )}
              {model.activity_volume_pricing_enabled && (
                <div className="flex justify-between text-purple-600">
                  <span>Volume pricing:</span>
                  <span className="font-medium">Enabled</span>
                </div>
              )}
              <Separator />
              <div className="flex justify-between font-medium">
                <span>Activity type:</span>
                <span className="capitalize">{(model.activity_activity_type || "api_call").replace("_", " ")}</span>
              </div>
              <div className="flex justify-between font-medium">
                <span>Billing:</span>
                <span className="capitalize">{(model.activity_billing_frequency || "monthly").replace("_", " ")}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
