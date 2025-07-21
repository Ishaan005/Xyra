"use client";

import { useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, DollarSign, Calculator, Settings } from "lucide-react";

interface AgentBasedFormProps {
  model: any;
  setModel: (model: any) => void;
}

export default function AgentBasedForm({ model, setModel }: AgentBasedFormProps) {
  // Initialize form with default values if model is empty or missing agent fields
  useEffect(() => {
    if (!model || !model.hasOwnProperty('agent_base_agent_fee')) {
      setModel({
        ...model, // Preserve any existing data (like model_type)
        model_type: model?.model_type || 'agent',
        name: model?.name || '',
        description: model?.description || '',
        agent_base_agent_fee: model?.agent_base_agent_fee || 0,
        agent_billing_frequency: model?.agent_billing_frequency || 'monthly',
        agent_tier: model?.agent_tier || 'professional',
        agent_setup_fee: model?.agent_setup_fee || 0,
        agent_human_equivalent_value: model?.agent_human_equivalent_value || 0,
        agent_volume_discount_enabled: model?.agent_volume_discount_enabled || false,
        agent_volume_discount_threshold: model?.agent_volume_discount_threshold || 0,
        agent_volume_discount_percentage: model?.agent_volume_discount_percentage || 0,
      });
    }
  }, [model, setModel]);

  const handleInputChange = (field: string, value: any) => {
    setModel({ ...model, [field]: value });
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <Users className="h-4 w-4 text-blue-500" />
        <h3 className="text-sm font-medium text-muted-foreground">Agent-Based Configuration</h3>
        <Badge variant="outline" className="text-xs">Per Agent</Badge>
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
              placeholder="e.g., Professional Agent Plan"
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
        {/* Base Agent Fee */}
        <div className="space-y-2">
          <Label htmlFor="agent-base-fee" className="text-sm font-medium flex items-center gap-2">
            <DollarSign className="h-3 w-3" />
            Base Agent Fee (USD)
          </Label>
          <Input
            id="agent-base-fee"
            type="number"
            step="0.01"
            min="0"
            placeholder="e.g., 299.00"
            value={model.agent_base_agent_fee !== undefined ? model.agent_base_agent_fee.toString() : ""}
            onChange={(e) => {
              const value = e.target.value;
              if (value === "") {
                handleInputChange("agent_base_agent_fee", "");
              } else {
                const numValue = parseFloat(value);
                if (!isNaN(numValue)) {
                  handleInputChange("agent_base_agent_fee", numValue);
                }
              }
            }}
          />
          <p className="text-xs text-muted-foreground">
            Monthly or yearly fee per agent (depending on billing frequency)
          </p>
        </div>

        {/* Agent Tier */}
        <div className="space-y-2">
          <Label htmlFor="agent-tier" className="text-sm font-medium">
            Agent Tier
          </Label>
          <Select
            value={model.agent_tier || "professional"}
            onValueChange={(value) => handleInputChange("agent_tier", value)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select agent tier" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="starter">
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-xs bg-green-50 text-green-700">Starter</Badge>
                  <span>Basic features</span>
                </div>
              </SelectItem>
              <SelectItem value="professional">
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-xs bg-blue-50 text-blue-700">Professional</Badge>
                  <span>Full features</span>
                </div>
              </SelectItem>
              <SelectItem value="enterprise">
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-xs bg-purple-50 text-purple-700">Enterprise</Badge>
                  <span>Advanced features</span>
                </div>
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Billing Frequency */}
        <div className="space-y-2">
          <Label htmlFor="agent-billing-frequency" className="text-sm font-medium">
            Billing Frequency
          </Label>
          <Select
            value={model.agent_billing_frequency || "monthly"}
            onValueChange={(value) => handleInputChange("agent_billing_frequency", value)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select billing frequency" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="monthly">Monthly</SelectItem>
              <SelectItem value="yearly">Yearly (typically discounted)</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <Separator />

        {/* Setup Fee */}
        <div className="space-y-2">
          <Label htmlFor="agent-setup-fee" className="text-sm font-medium">
            Setup Fee (USD)
          </Label>
          <Input
            id="agent-setup-fee"
            type="number"
            step="0.01"
            min="0"
            placeholder="e.g., 99.00"
            value={model.agent_setup_fee !== undefined ? model.agent_setup_fee.toString() : ""}
            onChange={(e) => {
              const value = e.target.value;
              if (value === "") {
                handleInputChange("agent_setup_fee", "");
              } else {
                const numValue = parseFloat(value);
                if (!isNaN(numValue)) {
                  handleInputChange("agent_setup_fee", numValue);
                }
              }
            }}
          />
          <p className="text-xs text-muted-foreground">
            One-time setup fee per agent (optional)
          </p>
        </div>

        {/* Human Equivalent Value */}
        <div className="space-y-2">
          <Label htmlFor="agent-human-equivalent" className="text-sm font-medium flex items-center gap-2">
            <Users className="h-3 w-3" />
            Human Equivalent Value (USD)
          </Label>
          <Input
            id="agent-human-equivalent"
            type="number"
            step="0.01"
            min="0"
            placeholder="e.g., 5000.00"
            value={model.agent_human_equivalent_value !== undefined ? model.agent_human_equivalent_value.toString() : ""}
            onChange={(e) => {
              const value = e.target.value;
              if (value === "") {
                handleInputChange("agent_human_equivalent_value", "");
              } else {
                const numValue = parseFloat(value);
                if (!isNaN(numValue)) {
                  handleInputChange("agent_human_equivalent_value", numValue);
                }
              }
            }}
          />
          <p className="text-xs text-muted-foreground">
            Cost of equivalent human resources per agent per billing period
          </p>
        </div>

        <Separator />

        {/* Volume Discount Configuration */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="text-sm font-medium flex items-center gap-2">
                <Calculator className="h-3 w-3" />
                Volume Discounts
              </Label>
              <p className="text-xs text-muted-foreground">
                Offer discounts for customers with multiple agents
              </p>
            </div>
            <Switch
              checked={model.agent_volume_discount_enabled || false}
              onCheckedChange={(checked) => handleInputChange("agent_volume_discount_enabled", checked)}
            />
          </div>

          {model.agent_volume_discount_enabled && (
            <div className="grid grid-cols-2 gap-4 p-4 border rounded-lg bg-muted/20">
              <div className="space-y-2">
                <Label htmlFor="agent-volume-threshold" className="text-sm font-medium">
                  Minimum Agents
                </Label>
                <Input
                  id="agent-volume-threshold"
                  type="number"
                  min="2"
                  placeholder="e.g., 5"
                  value={model.agent_volume_discount_threshold !== undefined ? model.agent_volume_discount_threshold.toString() : ""}
                  onChange={(e) => {
                    const value = e.target.value;
                    if (value === "") {
                      handleInputChange("agent_volume_discount_threshold", "");
                    } else {
                      const numValue = parseInt(value);
                      if (!isNaN(numValue)) {
                        handleInputChange("agent_volume_discount_threshold", numValue);
                      }
                    }
                  }}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="agent-volume-percentage" className="text-sm font-medium">
                  Discount %
                </Label>
                <Input
                  id="agent-volume-percentage"
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  placeholder="e.g., 15"
                  value={model.agent_volume_discount_percentage !== undefined ? model.agent_volume_discount_percentage : ""}
                  onChange={(e) => {
                    const value = e.target.value;
                    if (value === "") {
                      handleInputChange("agent_volume_discount_percentage", 0);
                    } else {
                      const numValue = parseFloat(value);
                      handleInputChange("agent_volume_discount_percentage", isNaN(numValue) ? 0 : numValue);
                    }
                  }}
                />
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
                <span>Base fee per agent:</span>
                <span className="font-medium">${(model.agent_base_agent_fee || 0).toFixed(2)}</span>
              </div>
              {model.agent_setup_fee > 0 && (
                <div className="flex justify-between">
                  <span>Setup fee (one-time):</span>
                  <span className="font-medium">${(model.agent_setup_fee || 0).toFixed(2)}</span>
                </div>
              )}
              {model.agent_volume_discount_enabled && model.agent_volume_discount_threshold && (
                <div className="flex justify-between text-green-600">
                  <span>Volume discount ({model.agent_volume_discount_threshold}+ agents):</span>
                  <span className="font-medium">-{model.agent_volume_discount_percentage || 0}%</span>
                </div>
              )}
              <Separator />
              <div className="flex justify-between font-medium">
                <span>Billing frequency:</span>
                <span className="capitalize">{model.agent_billing_frequency || "monthly"}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
