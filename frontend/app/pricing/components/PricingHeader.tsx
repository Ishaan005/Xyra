import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { DollarSign, Search, Filter } from "lucide-react";

interface PricingHeaderProps {
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  onReload: () => void;
}

/**
 * PricingHeader component
 * Renders the page header, search bar, and reload button for the pricing page.
 *
 * Props:
 * - searchQuery: string (current search input value)
 * - setSearchQuery: (q: string) => void (handler to update search input)
 * - onReload: () => void (handler to reload the page)
 */

export default function PricingHeader({ searchQuery, setSearchQuery, onReload }: PricingHeaderProps) {
  return (
    <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-gradient-to-r from-background to-muted/20 p-6 rounded-xl border border-border/8 shadow-sm ring-1 ring-border/5 hover:ring-border/10 transition-all duration-300">
      <div className="flex items-center gap-3">
        <div className="rounded-full bg-gold/10 p-2">
          <DollarSign className="h-6 w-6 text-gold" />
        </div>
        <div>
          <h1 className="text-3xl font-bold">Pricing Models</h1>
          <p className="text-muted-foreground">Manage your pricing strategies and billing configurations</p>
        </div>
      </div>
      <div className="flex items-center gap-3 w-full md:w-auto">
        <div className="relative flex-grow w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search pricing models..."
            className="pl-9 w-full"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Button onClick={onReload} variant="outline" size="icon" className="flex-shrink-0">
          <Filter className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
