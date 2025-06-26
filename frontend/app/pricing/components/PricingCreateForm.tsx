import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus } from "lucide-react";
import WorkflowBillingForm from "@/app/pricing/components/workflow-billing-form";

/**
 * PricingCreateForm component
 * Renders the form for creating a new pricing model.
 *
 * Props:
 * - show: boolean (whether to show the form)
 * - newModel: any (form state for the new model)
 * - setNewModel: (m: any) => void (handler to update form state)
 * - onCancel: () => void (handler to cancel form)
 * - onCreate: () => void (handler to create model)
 */
interface PricingCreateFormProps {
  show: boolean;
  newModel: any;
  setNewModel: (m: any) => void;
  onCancel: () => void;
  onCreate: () => void;
}

export default function PricingCreateForm({ show, newModel, setNewModel, onCancel, onCreate }: PricingCreateFormProps) {
  if (!show) return null;
  return (
    <Card className="border-border/8 ring-1 ring-border/5 shadow-sm overflow-hidden hover:ring-border/10 transition-all duration-300">
      <CardHeader className="bg-gradient-to-r from-gold/5 to-transparent">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Plus className="h-4 w-4 text-gold" />
            <CardTitle>Create New Pricing Model</CardTitle>
          </div>
          <Badge variant="outline" className="bg-gold/10 text-gold-dark border-gold/8">New</Badge>
        </div>
        <CardDescription>Configure a new pricing model for your agents</CardDescription>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="model-name" className="text-sm font-medium">
                Model Name
              </label>
              <Input
                id="model-name"
                placeholder="Enter model name"
                value={newModel.name}
                onChange={(e) => setNewModel({ ...newModel, name: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="model-description" className="text-sm font-medium">
                Description
              </label>
              <Input
                id="model-description"
                placeholder="Enter description"
                value={newModel.description}
                onChange={(e) => setNewModel({ ...newModel, description: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="model-type" className="text-sm font-medium">
                Model Type
              </label>
              <select
                id="model-type"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                value={newModel.model_type}
                onChange={(e) => setNewModel({ ...newModel, model_type: e.target.value })}
              >
                <option value="activity">Activity-based</option>
                <option value="agent">Agent-based</option>
                <option value="hybrid">Hybrid</option>
                <option value="outcome">Outcome-based</option>
                <option value="workflow">Workflow-based</option>
              </select>
            </div>
          </div>
          <div className="space-y-2">
            {/* Render config fields by model_type */}
            {newModel.model_type === "workflow" && (
              <WorkflowBillingForm
                workflowTypes={newModel.workflow_types}
                commitmentTiers={newModel.commitment_tiers}
                onWorkflowTypesChange={(types) => setNewModel({ ...newModel, workflow_types: types })}
                onCommitmentTiersChange={(tiers) => setNewModel({ ...newModel, commitment_tiers: tiers })}
                baseModel={newModel}
                onBaseModelChange={setNewModel}
              />
            )}
            {/* ...add other model type forms here as needed... */}
          </div>
        </div>
      </CardContent>
      <CardFooter className="flex justify-between border-t pt-4">
        <Button variant="outline" onClick={onCancel}>Cancel</Button>
        <Button onClick={onCreate}>
          <Plus className="h-4 w-4 mr-2" />
          Create Model
        </Button>
      </CardFooter>
    </Card>
  );
}
