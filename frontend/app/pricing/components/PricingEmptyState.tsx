import { Button } from "@/components/ui/button";
import { Settings, Plus } from "lucide-react";

interface PricingEmptyStateProps {
  searchQuery: string;
  onCreate: () => void;
}

/**
 * PricingEmptyState component
 * Renders the empty state when no pricing models are found.
 *
 * Props:
 * - searchQuery: string (current search input value)
 * - onCreate: () => void (handler to open create form)
 */

export default function PricingEmptyState({ searchQuery, onCreate }: PricingEmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="rounded-full bg-muted p-4 mb-4">
        <Settings className="h-8 w-8 text-muted-foreground" />
      </div>
      <h2 className="text-xl font-bold mb-2">No pricing models found</h2>
      <p className="text-muted-foreground mb-4">
        {searchQuery ? "Try a different search term" : "Create your first pricing model to get started"}
      </p>
      <Button className="gap-2" onClick={onCreate}>
        <Plus className="h-4 w-4" />
        Create New Model
      </Button>
    </div>
  );
}
