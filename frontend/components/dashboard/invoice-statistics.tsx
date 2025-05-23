"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { ArrowDown, ArrowUp, DollarSign } from "lucide-react"
import api from "../../utils/api"

interface InvoiceStatisticsProps {
  orgId: number;
  period?: "week" | "month" | "quarter" | "year";
}

interface InvoiceStats {
  totalInvoiced: number;
  totalPaid: number;
  totalPending: number;
  paymentRate: number;
  currency: string;
  changePercentage: number;
}

export function InvoiceStatistics({ orgId, period = "month" }: InvoiceStatisticsProps) {
  const [stats, setStats] = useState<InvoiceStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchInvoiceStats();
  }, [orgId, period]);

  const fetchInvoiceStats = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/analytics/invoices/?org_id=${orgId}&period=${period}`);
      setStats(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to load invoice statistics");
      setStats(null);
    } finally {
      setLoading(false);
    }
  };
  
  // Fallback data if API doesn't return stats yet
  const fallbackStats: InvoiceStats = {
    totalInvoiced: 0,
    totalPaid: 0,
    totalPending: 0,
    paymentRate: 0,
    currency: "USD",
    changePercentage: 0
  };
  
  const displayStats = stats || fallbackStats;

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Invoiced</CardTitle>
          <DollarSign className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          {loading ? (
            <Skeleton className="h-7 w-[120px]" />
          ) : error ? (
            <p className="text-sm text-red-500">Error loading data</p>
          ) : (
            <>
              <div className="text-2xl font-bold">
                {displayStats.currency} {displayStats.totalInvoiced.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
              </div>
              <p className="text-xs text-muted-foreground">
                {displayStats.changePercentage > 0 ? (
                  <span className="text-green-500 flex items-center">
                    <ArrowUp className="mr-1 h-3 w-3" />
                    {Math.abs(displayStats.changePercentage)}% from last {period}
                  </span>
                ) : displayStats.changePercentage < 0 ? (
                  <span className="text-red-500 flex items-center">
                    <ArrowDown className="mr-1 h-3 w-3" />
                    {Math.abs(displayStats.changePercentage)}% from last {period}
                  </span>
                ) : (
                  <span>No change from last {period}</span>
                )}
              </p>
            </>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Paid</CardTitle>
          <DollarSign className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          {loading ? (
            <Skeleton className="h-7 w-[120px]" />
          ) : error ? (
            <p className="text-sm text-red-500">Error loading data</p>
          ) : (
            <div className="text-2xl font-bold">
              {displayStats.currency} {displayStats.totalPaid.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Pending</CardTitle>
          <DollarSign className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          {loading ? (
            <Skeleton className="h-7 w-[120px]" />
          ) : error ? (
            <p className="text-sm text-red-500">Error loading data</p>
          ) : (
            <div className="text-2xl font-bold">
              {displayStats.currency} {displayStats.totalPending.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Payment Rate</CardTitle>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            className="h-4 w-4 text-muted-foreground"
          >
            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
          </svg>
        </CardHeader>
        <CardContent>
          {loading ? (
            <Skeleton className="h-7 w-[120px]" />
          ) : error ? (
            <p className="text-sm text-red-500">Error loading data</p>
          ) : (
            <div className="text-2xl font-bold">
              {displayStats.paymentRate.toFixed(1)}%
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
