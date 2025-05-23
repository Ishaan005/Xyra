"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ArrowRight } from "lucide-react"
import { format } from "date-fns"
import api from "../../utils/api"
import { Invoice } from "../../types/invoice"

interface RecentInvoicesProps {
  limit?: number;
  orgId: number;
}

export function RecentInvoices({ limit = 5, orgId }: RecentInvoicesProps) {
  const router = useRouter();
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRecentInvoices();
  }, []);

  const fetchRecentInvoices = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/invoices/?org_id=${orgId}&limit=${limit}`);
      setInvoices(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to load recent invoices");
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "paid":
        return <Badge className="bg-green-500">Paid</Badge>;
      case "pending":
        return <Badge className="bg-yellow-500">Pending</Badge>;
      case "cancelled":
        return <Badge className="bg-red-500">Cancelled</Badge>;
      case "overdue":
        return <Badge className="bg-orange-500">Overdue</Badge>;
      default:
        return <Badge className="bg-gray-500">{status}</Badge>;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Invoices</CardTitle>
        <CardDescription>Your most recent invoices and their statuses</CardDescription>
      </CardHeader>
      <CardContent>
        {loading ? (
          <p>Loading recent invoices...</p>
        ) : error ? (
          <p className="text-sm text-red-500">{error}</p>
        ) : invoices.length === 0 ? (
          <p className="text-sm text-muted-foreground">No invoices found</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Invoice #</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {invoices.map((invoice) => (
                <TableRow key={invoice.id} className="cursor-pointer hover:bg-muted/50" onClick={() => router.push(`/dashboard/invoices/${invoice.id}`)}>
                  <TableCell>{invoice.invoice_number}</TableCell>
                  <TableCell>{format(new Date(invoice.issue_date), 'MMM dd, yyyy')}</TableCell>
                  <TableCell>{invoice.currency} {invoice.total_amount.toFixed(2)}</TableCell>
                  <TableCell>{getStatusBadge(invoice.status)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
      <CardFooter>
        <Button variant="ghost" className="w-full" onClick={() => router.push('/dashboard/invoices')}>
          View All Invoices <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
      </CardFooter>
    </Card>
  );
}
