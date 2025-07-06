import React from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Edit, Trash2, CheckCircle2, Copy } from "lucide-react";

/**
 * PricingModelCard component
 * Renders a single pricing model card in the grid.
 *
 * Props:
 * - model: any (pricing model data)
 * - onEdit: () => void (handler to edit the model)
 * - onDelete: () => void (handler to delete the model)
 * - onDuplicate: () => void (handler to duplicate the model)
 * - getModelIcon: (type: string) => React.ReactNode (icon renderer)
 * - getModelTypeColor: (type: string) => string (color class renderer)
 */

interface PricingModelCardProps {
  model: any;
  onEdit: () => void;
  onDelete: () => void;
  onDuplicate: () => void;
  getModelIcon: (type: string) => React.ReactNode;
  getModelTypeColor: (type: string) => string;
}

export default function PricingModelCard({ model, onEdit, onDelete, onDuplicate, getModelIcon, getModelTypeColor }: PricingModelCardProps) {
  return (
    <Card className="h-full flex flex-col overflow-hidden border-border/8 ring-1 ring-border/5 shadow-sm hover:shadow-md transition-shadow duration-300 hover:ring-border/10">
      <CardHeader className="pb-4 bg-gradient-to-r from-muted/30 to-transparent">
        <div className="flex justify-between items-start">
          <Badge className={`${getModelTypeColor(model.model_type)} px-2 py-0.5 text-xs font-medium`}>
            {model.model_type}
          </Badge>
          <div className="flex gap-1">
            <Button size="icon" className="h-8 w-8 text-blue hover:text-blue hover:border-blue" variant="ghost" onClick={onEdit}>
              <Edit className="h-4 w-4" />
            </Button>
            <Button size="icon" className="h-8 w-8 text-destructive hover:text-destructive hover:border-destructive" variant="ghost" onClick={onDelete}>
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
        <div className="flex items-center gap-2 mt-2">
          <div className={`rounded-full p-2 ${getModelTypeColor(model.model_type)}`}>{getModelIcon(model.model_type)}</div>
          <CardTitle>{model.name}</CardTitle>
        </div>
        <CardDescription>
          {model.description || `A ${model.model_type.toLowerCase()} pricing model for your services`}
        </CardDescription>
      </CardHeader>
      <CardContent className="pb-4 flex-1">
        {/* Example: Activity config, Agent config, Workflow config, etc. */}
        <div className="space-y-3">
          {model.model_type === "activity" && model.activity_config && model.activity_config[0] && (
            <div className="bg-muted/20 rounded-lg p-3 border border-border/10">
              <h4 className="font-medium text-sm mb-2">Activity Configuration</h4>
              <div className="grid grid-cols-1 gap-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Price per unit:</span>
                  <span className="font-mono">${model.activity_config[0].price_per_unit}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Activity type:</span>
                  <span className="font-mono">{model.activity_config[0].activity_type}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Unit type:</span>
                  <span className="font-mono">{model.activity_config[0].unit_type}</span>
                </div>
                {model.activity_config[0].base_agent_fee > 0 && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Base agent fee:</span>
                    <span className="font-mono">${model.activity_config[0].base_agent_fee}</span>
                  </div>
                )}
                {model.activity_config[0].volume_pricing_enabled && (
                  <div className="mt-2">
                    <span className="text-muted-foreground text-xs">Volume pricing enabled</span>
                    {model.activity_config[0].volume_tier_1_threshold && (
                      <div className="flex justify-between text-xs mt-1">
                        <span>Tier 1 ({model.activity_config[0].volume_tier_1_threshold}+ units):</span>
                        <span className="font-mono">${model.activity_config[0].volume_tier_1_price}</span>
                      </div>
                    )}
                    {model.activity_config[0].volume_tier_2_threshold && (
                      <div className="flex justify-between text-xs">
                        <span>Tier 2 ({model.activity_config[0].volume_tier_2_threshold}+ units):</span>
                        <span className="font-mono">${model.activity_config[0].volume_tier_2_price}</span>
                      </div>
                    )}
                    {model.activity_config[0].volume_tier_3_threshold && (
                      <div className="flex justify-between text-xs">
                        <span>Tier 3 ({model.activity_config[0].volume_tier_3_threshold}+ units):</span>
                        <span className="font-mono">${model.activity_config[0].volume_tier_3_price}</span>
                      </div>
                    )}
                  </div>
                )}
                {model.activity_config[0].minimum_charge > 0 && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Minimum charge:</span>
                    <span className="font-mono">${model.activity_config[0].minimum_charge}</span>
                  </div>
                )}
              </div>
            </div>
          )}
          {model.model_type === "agent" && model.agent_config && (
            <div className="bg-muted/20 rounded-lg p-3 border border-border/10">
              <h4 className="font-medium text-sm mb-2">Agent Configuration</h4>
              <div className="grid grid-cols-1 gap-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Base agent fee:</span>
                  <span className="font-mono">${model.agent_config.base_agent_fee}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Billing frequency:</span>
                  <span className="font-mono">{model.agent_config.billing_frequency}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Agent tier:</span>
                  <span className="font-mono">{model.agent_config.agent_tier}</span>
                </div>
              </div>
            </div>
          )}
          {/* Add similar sections for workflow, outcome, etc. as needed */}
        </div>
      </CardContent>
      <CardFooter className="flex justify-between border-t pt-4">
        <div className="flex items-center text-sm">
          <CheckCircle2 className="h-4 w-4 text-success mr-1" />
          Active
        </div>
        <Button className="gap-1 text-sm" variant="outline" onClick={onDuplicate}>
          <Copy className="h-3 w-3" />
          Duplicate
        </Button>
      </CardFooter>
    </Card>
  );
}
