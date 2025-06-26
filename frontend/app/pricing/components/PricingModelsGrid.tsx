import PricingModelCard from "@/app/pricing/components/PricingModelCard";

interface PricingModelsGridProps {
  models: any[];
  onEdit: (model: any) => void;
  onDelete: (modelId: number) => void;
  onDuplicate: (model: any) => void;
  getModelIcon: (type: string) => React.ReactNode;
  getModelTypeColor: (type: string) => string;
}

/**
 * PricingModelsGrid component
 * Renders a grid of pricing model cards.
 *
 * Props:
 * - models: any[] (array of pricing models)
 * - onEdit: (model: any) => void (handler to edit a model)
 * - onDelete: (modelId: number) => void (handler to delete a model)
 * - onDuplicate: (model: any) => void (handler to duplicate a model)
 * - getModelIcon: (type: string) => React.ReactNode (icon renderer)
 * - getModelTypeColor: (type: string) => string (color class renderer)
 */

export default function PricingModelsGrid({ models, onEdit, onDelete, onDuplicate, getModelIcon, getModelTypeColor }: PricingModelsGridProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {models.map((model) => (
        <PricingModelCard
          key={model.id}
          model={model}
          onEdit={() => onEdit(model)}
          onDelete={() => onDelete(model.id)}
          onDuplicate={() => onDuplicate(model)}
          getModelIcon={getModelIcon}
          getModelTypeColor={getModelTypeColor}
        />
      ))}
    </div>
  );
}
