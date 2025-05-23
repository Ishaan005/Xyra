"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { 
  Calendar as CalendarIcon, 
  Search, 
  Filter, 
  X, 
  ChevronDown 
} from "lucide-react"
import { format } from "date-fns"

interface InvoiceFilterProps {
  onFilter: (filters: InvoiceFilters) => void;
  onReset: () => void;
}

export interface InvoiceFilters {
  search?: string;
  status?: "all" | "pending" | "paid" | "cancelled" | "overdue";
  startDate?: string;
  endDate?: string;
  minAmount?: number;
  maxAmount?: number;
}

export function InvoiceFilter({ onFilter, onReset }: InvoiceFilterProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [filters, setFilters] = useState<InvoiceFilters>({
    search: "",
    status: "all",
    startDate: "",
    endDate: "",
    minAmount: undefined,
    maxAmount: undefined,
  });

  const handleChange = (field: keyof InvoiceFilters, value: any) => {
    setFilters({
      ...filters,
      [field]: value,
    });
  };

  const handleFilter = () => {
    onFilter(filters);
  };

  const handleReset = () => {
    setFilters({
      search: "",
      status: "all",
      startDate: "",
      endDate: "",
      minAmount: undefined,
      maxAmount: undefined,
    });
    onReset();
  };

  return (
    <Card className="mb-6">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle>Filter Invoices</CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? <X className="h-4 w-4" /> : <Filter className="h-4 w-4" />}
            <span className="ml-1">{isExpanded ? "Close" : "Expand"}</span>
          </Button>
        </div>
      </CardHeader>

      <CardContent>
        <div className="flex items-center gap-2 mb-4">
          <div className="relative flex-1">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search invoices..."
              className="pl-8"
              value={filters.search}
              onChange={(e) => handleChange("search", e.target.value)}
            />
          </div>
          <div>
            <select
              className="h-10 rounded-md border border-input bg-background px-3 py-2"
              value={filters.status}
              onChange={(e) => handleChange("status", e.target.value)}
            >
              <option value="all">All Status</option>
              <option value="pending">Pending</option>
              <option value="paid">Paid</option>
              <option value="cancelled">Cancelled</option>
              <option value="overdue">Overdue</option>
            </select>
          </div>
        </div>

        {isExpanded && (
          <div className="space-y-4 pt-3 border-t">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="startDate" className="mb-1 block text-sm">
                  Start Date
                </Label>
                <div className="relative">
                  <CalendarIcon className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="startDate"
                    type="date"
                    className="pl-8"
                    value={filters.startDate}
                    onChange={(e) => handleChange("startDate", e.target.value)}
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="endDate" className="mb-1 block text-sm">
                  End Date
                </Label>
                <div className="relative">
                  <CalendarIcon className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="endDate"
                    type="date"
                    className="pl-8"
                    value={filters.endDate}
                    onChange={(e) => handleChange("endDate", e.target.value)}
                  />
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="minAmount" className="mb-1 block text-sm">
                  Min Amount
                </Label>
                <Input
                  id="minAmount"
                  type="number"
                  placeholder="0.00"
                  value={filters.minAmount || ""}
                  onChange={(e) => handleChange("minAmount", e.target.value ? Number(e.target.value) : undefined)}
                  step="0.01"
                  min="0"
                />
              </div>
              <div>
                <Label htmlFor="maxAmount" className="mb-1 block text-sm">
                  Max Amount
                </Label>
                <Input
                  id="maxAmount"
                  type="number"
                  placeholder="Any"
                  value={filters.maxAmount || ""}
                  onChange={(e) => handleChange("maxAmount", e.target.value ? Number(e.target.value) : undefined)}
                  step="0.01"
                  min="0"
                />
              </div>
            </div>
          </div>
        )}
      </CardContent>

      <CardFooter className="flex justify-between">
        <Button variant="outline" onClick={handleReset}>
          Reset
        </Button>
        <Button onClick={handleFilter}>
          Apply Filters
        </Button>
      </CardFooter>
    </Card>
  );
}
