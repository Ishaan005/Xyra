"use client";

import { useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Zap } from "lucide-react";
import WorkflowBillingForm from "@/app/pricing/components/workflow-billing-form";

interface WorkflowBasedFormProps {
  model: any;
  setModel: (model: any) => void;
}

export default function WorkflowBasedForm({ model, setModel }: WorkflowBasedFormProps) {
  // Initialize form with default values if model is empty or missing workflow fields
  useEffect(() => {
    if (!model || !model.hasOwnProperty('workflow_base_platform_fee')) {
      setModel({
        ...model, // Preserve any existing data (like model_type)
        model_type: model?.model_type || 'workflow',
        name: model?.name || '',
        description: model?.description || '',
        workflow_base_platform_fee: model?.workflow_base_platform_fee || 0,
        workflow_platform_fee_frequency: model?.workflow_platform_fee_frequency || 'monthly',
        workflow_default_billing_frequency: model?.workflow_default_billing_frequency || 'monthly',
        workflow_volume_discount_enabled: model?.workflow_volume_discount_enabled || false,
        workflow_volume_discount_threshold: model?.workflow_volume_discount_threshold || 0,
        workflow_volume_discount_percentage: model?.workflow_volume_discount_percentage || 0,
        workflow_overage_multiplier: model?.workflow_overage_multiplier || 1.0,
        workflow_currency: model?.workflow_currency || 'USD',
        workflow_is_active: model?.workflow_is_active !== false,
        workflow_types: model?.workflow_types || [],
        commitment_tiers: model?.commitment_tiers || [],
      });
    }
  }, [model, setModel]);

  const handleInputChange = (field: string, value: any) => {
    setModel({ ...model, [field]: value });
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <Zap className="h-4 w-4 text-yellow-500" />
        <h3 className="text-sm font-medium text-muted-foreground">Workflow-Based Configuration</h3>
        <Badge variant="outline" className="text-xs">Structured</Badge>
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
              placeholder="e.g., Enterprise Workflow Plan"
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

        {/* Workflow Configuration */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5" />
              Workflow Configuration
            </CardTitle>
            <CardDescription>
              Configure workflow-specific pricing with commitment tiers
            </CardDescription>
          </CardHeader>
          <CardContent>
            <WorkflowBillingForm
              workflowTypes={model.workflow_types || []}
              commitmentTiers={model.commitment_tiers || []}
              onWorkflowTypesChange={(types) => handleInputChange("workflow_types", types)}
              onCommitmentTiersChange={(tiers) => handleInputChange("commitment_tiers", tiers)}
              baseModel={model}
              onBaseModelChange={setModel}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
