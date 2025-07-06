"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Plus, Users, Activity, Target, Zap, GitBranch } from "lucide-react";
import WorkflowBasedForm from "@/app/pricing/components/WorkflowBasedForm";
import OutcomeBasedForm from "@/app/pricing/components/OutcomeBasedForm";
import AgentBasedForm from "@/app/pricing/components/AgentBasedForm";
import ActivityBasedForm from "@/app/pricing/components/ActivityBasedForm";

interface ComprehensivePricingFormProps {
  show: boolean;
  onCancel: () => void;
  onSubmit: (data: any) => void;
  isLoading?: boolean;
}

const billingModelTypes = [
  {
    id: "agent",
    name: "Agent-Based",
    description: "Fixed monthly/yearly fee per agent with optional volume discounts",
    icon: Users,
    badge: "Popular",
    badgeVariant: "default" as const,
    features: ["Per-agent pricing", "Volume discounts", "Setup fees", "Tier-based features"]
  },
  {
    id: "activity",
    name: "Activity-Based", 
    description: "Pay-per-use pricing based on API calls, queries, or other activities",
    icon: Activity,
    badge: "Flexible",
    badgeVariant: "secondary" as const,
    features: ["Usage-based billing", "Volume tiers", "Minimum charges", "Multiple activity types"]
  },
  {
    id: "outcome",
    name: "Outcome-Based",
    description: "Performance-based pricing tied to business outcomes and results",
    icon: Target,
    badge: "Results-driven",
    badgeVariant: "outline" as const,
    features: ["Success-based fees", "Multi-tier pricing", "Risk premiums", "Performance bonuses"]
  },
  {
    id: "workflow",
    name: "Workflow-Based",
    description: "Pricing based on specific workflows and commitment tiers",
    icon: Zap,
    badge: "Structured",
    badgeVariant: "secondary" as const,
    features: ["Workflow pricing", "Commitment tiers", "Volume discounts", "Overage handling"]
  },
  {
    id: "hybrid",
    name: "Hybrid",
    description: "Combine multiple billing models for comprehensive pricing",
    icon: GitBranch,
    badge: "Advanced",
    badgeVariant: "outline" as const,
    features: ["Multiple models", "Custom combinations", "Complex pricing", "Enterprise-ready"]
  }
];

export default function ComprehensivePricingForm({ 
  show, 
  onCancel, 
  onSubmit, 
  isLoading = false 
}: ComprehensivePricingFormProps) {
  const [selectedModelType, setSelectedModelType] = useState<string | null>(null);
  const [formData, setFormData] = useState<any>({});

  if (!show) return null;

  const handleModelTypeSelect = (modelType: string) => {
    setSelectedModelType(modelType);
    setFormData({ 
      model_type: modelType,
      name: "",
      description: ""
    }); // Initialize form data with required fields
  };

  const handleFormSubmit = (data?: any) => {
    console.log('Form submission data:', data); // Debug log
    console.log('Current formData:', formData); // Debug log
    const submissionData = {
      ...formData,
      ...data,
      model_type: selectedModelType
    };
    console.log('Final submission data:', submissionData); // Debug log
    onSubmit(submissionData);
  };

  const renderBillingModelForm = () => {
    const commonFormSection = (
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Basic Information</CardTitle>
          <CardDescription>
            Provide basic details for your pricing model
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label htmlFor="model-name" className="text-sm font-medium">
                Model Name *
              </label>
              <input
                id="model-name"
                type="text"
                placeholder="e.g., Enterprise Outcome Model"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={formData.name || ""}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="model-description" className="text-sm font-medium">
                Description
              </label>
              <input
                id="model-description"
                type="text"
                placeholder="Brief description of the pricing model"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={formData.description || ""}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </div>
          </div>
        </CardContent>
      </Card>
    );

    switch (selectedModelType) {
      case "agent":
        return (
          <div className="space-y-6">
            {commonFormSection}
            <AgentBasedForm
              model={formData}
              setModel={setFormData}
            />
            <div className="flex justify-end space-x-4">
              <Button variant="outline" onClick={() => setSelectedModelType(null)}>
                Back
              </Button>
              <Button onClick={() => handleFormSubmit(formData)} disabled={isLoading}>
                {isLoading ? "Creating..." : "Create Agent-Based Model"}
              </Button>
            </div>
          </div>
        );
      case "activity":
        return (
          <div className="space-y-6">
            {commonFormSection}
            <ActivityBasedForm
              model={formData}
              setModel={setFormData}
            />
            <div className="flex justify-end space-x-4">
              <Button variant="outline" onClick={() => setSelectedModelType(null)}>
                Back
              </Button>
              <Button onClick={() => handleFormSubmit(formData)} disabled={isLoading}>
                {isLoading ? "Creating..." : "Create Activity-Based Model"}
              </Button>
            </div>
          </div>
        );
      case "outcome":
        return (
          <div className="space-y-6">
            {commonFormSection}
            <OutcomeBasedForm
              model={formData}
              setModel={setFormData}
            />
            <div className="flex justify-end space-x-4">
              <Button variant="outline" onClick={() => setSelectedModelType(null)}>
                Back
              </Button>
              <Button onClick={() => handleFormSubmit(formData)} disabled={isLoading}>
                {isLoading ? "Creating..." : "Create Outcome-Based Model"}
              </Button>
            </div>
          </div>
        );
      case "workflow":
        return (
          <div className="space-y-6">
            {commonFormSection}
            <WorkflowBasedForm
              model={formData}
              setModel={setFormData}
            />
            <div className="flex justify-end space-x-4">
              <Button variant="outline" onClick={() => setSelectedModelType(null)}>
                Back
              </Button>
              <Button onClick={() => handleFormSubmit(formData)} disabled={isLoading}>
                {isLoading ? "Creating..." : "Create Workflow-Based Model"}
              </Button>
            </div>
          </div>
        );
      case "hybrid":
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <GitBranch className="h-5 w-5" />
                Hybrid Billing Model
              </CardTitle>
              <CardDescription>
                Combine multiple billing models for comprehensive pricing
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="text-center py-8">
                <GitBranch className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">Hybrid Billing Coming Soon</h3>
                <p className="text-muted-foreground mb-4">
                  Advanced hybrid billing models that combine multiple pricing strategies are currently in development.
                </p>
                <p className="text-sm text-muted-foreground">
                  For now, you can create individual billing models and combine them manually.
                </p>
              </div>
              <div className="flex justify-end space-x-4">
                <Button variant="outline" onClick={() => setSelectedModelType(null)}>
                  Back
                </Button>
              </div>
            </CardContent>
          </Card>
        );
      default:
        return null;
    }
  };

  if (selectedModelType) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4 mb-6">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSelectedModelType(null)}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Model Selection
          </Button>
        </div>
        {renderBillingModelForm()}
      </div>
    );
  }

  return (
    <Card className="border-border/8 ring-1 ring-border/5 shadow-sm">
      <CardHeader className="bg-gradient-to-r from-blue-50/50 to-transparent">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Plus className="h-5 w-5 text-blue-600" />
            <CardTitle>Create New Pricing Model</CardTitle>
          </div>
          <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
            New
          </Badge>
        </div>
        <CardDescription>
          Choose a billing model type that best fits your business needs
        </CardDescription>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {billingModelTypes.map((modelType) => {
            const Icon = modelType.icon;
            return (
              <Card
                key={modelType.id}
                className="cursor-pointer hover:shadow-md transition-all duration-200 border-border/50 hover:border-border"
                onClick={() => handleModelTypeSelect(modelType.id)}
              >
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between mb-2">
                    <Icon className="h-5 w-5 text-primary" />
                    <Badge variant={modelType.badgeVariant} className="text-xs">
                      {modelType.badge}
                    </Badge>
                  </div>
                  <CardTitle className="text-lg">{modelType.name}</CardTitle>
                  <CardDescription className="text-sm leading-relaxed">
                    {modelType.description}
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-0">
                  <ul className="space-y-1">
                    {modelType.features.map((feature, index) => (
                      <li key={index} className="text-xs text-muted-foreground flex items-center gap-2">
                        <div className="w-1 h-1 bg-primary rounded-full" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            );
          })}
        </div>
        
        <div className="flex justify-end mt-6 pt-4 border-t">
          <Button variant="outline" onClick={onCancel}>
            Cancel
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
