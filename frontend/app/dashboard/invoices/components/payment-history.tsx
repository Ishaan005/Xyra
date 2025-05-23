"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { format } from "date-fns"
import api from "../../../../utils/api"

interface PaymentHistoryProps {
  invoiceId: number;
}

interface PaymentRecord {
  id: number;
  invoice_id: number;
  amount: number;
  currency: string;
  payment_method: string;
  payment_date: string;
  status: string;
  transaction_id: string;
  metadata?: any;
  created_at: string;
}

export default function PaymentHistory({ invoiceId }: PaymentHistoryProps) {
  const [payments, setPayments] = useState<PaymentRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPaymentHistory();
  }, [invoiceId]);

  const fetchPaymentHistory = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/invoices/${invoiceId}/payments`);
      setPayments(response.data);
      setError(null);
    } catch (err: any) {
      console.error("Error fetching payment history:", err);
      setError(err.message || "Failed to load payment history");
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case "succeeded":
      case "success":
        return <Badge className="bg-green-500">Succeeded</Badge>;
      case "pending":
        return <Badge className="bg-yellow-500">Pending</Badge>;
      case "failed":
        return <Badge className="bg-red-500">Failed</Badge>;
      case "refunded":
        return <Badge className="bg-blue-500">Refunded</Badge>;
      default:
        return <Badge className="bg-gray-500">{status}</Badge>;
    }
  };

  // If no payments and not loading, don't display the component
  if (!loading && payments.length === 0) {
    return null;
  }

  return (
    <Card className="mt-6">
      <CardHeader>
        <CardTitle>Payment History</CardTitle>
        <CardDescription>Transaction records for this invoice</CardDescription>
      </CardHeader>
      <CardContent>
        {loading ? (
          <p className="text-center py-4 text-sm text-muted-foreground">Loading payment history...</p>
        ) : error ? (
          <p className="text-center py-4 text-sm text-red-500">{error}</p>
        ) : payments.length === 0 ? (
          <p className="text-center py-4 text-sm text-muted-foreground">No payment records found</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Method</TableHead>
                <TableHead>Transaction ID</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {payments.map((payment) => (
                <TableRow key={payment.id}>
                  <TableCell>{format(new Date(payment.payment_date), 'MMM dd, yyyy HH:mm')}</TableCell>
                  <TableCell>
                    {payment.currency} {payment.amount.toFixed(2)}
                  </TableCell>
                  <TableCell>{payment.payment_method}</TableCell>
                  <TableCell className="font-mono text-xs">
                    {payment.transaction_id}
                  </TableCell>
                  <TableCell>{getStatusBadge(payment.status)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
