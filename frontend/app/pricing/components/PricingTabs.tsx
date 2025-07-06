import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface PricingTabsProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

/**
 * PricingTabs component
 * Renders the model type filter tabs for the pricing page.
 *
 * Props:
 * - activeTab: string (currently selected tab)
 * - setActiveTab: (tab: string) => void (handler to change tab)
 */

export default function PricingTabs({ activeTab, setActiveTab }: PricingTabsProps) {
  return (
    <Tabs defaultValue="all" value={activeTab} onValueChange={setActiveTab} className="w-full sm:w-auto">
      <TabsList className="grid grid-cols-4 w-full sm:w-auto">
        <TabsTrigger value="all">All</TabsTrigger>
        <TabsTrigger value="activity">Activity</TabsTrigger>
        <TabsTrigger value="agent">Agent</TabsTrigger>
        <TabsTrigger value="workflow">Workflow</TabsTrigger>
      </TabsList>
    </Tabs>
  );
}
