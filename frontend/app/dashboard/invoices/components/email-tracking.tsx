"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { format } from "date-fns"
import api from "../../../../utils/api"

interface EmailTrackingProps {
  invoiceId: number;
}

interface EmailLog {
  id: number;
  recipient: string;
  sent_at: string;
  status: "sent" | "delivered" | "opened" | "clicked" | "failed";
  error_message?: string;
}

export function EmailTracking({ invoiceId }: EmailTrackingProps) {
  const [emails, setEmails] = useState<EmailLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchEmailLogs();
    
    // Set up polling to check for updates every minute
    const interval = setInterval(fetchEmailLogs, 60000);
    
    return () => clearInterval(interval);
  }, [invoiceId]);

  const fetchEmailLogs = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/invoices/${invoiceId}/email-logs`);
      setEmails(response.data);
      setError(null);
    } catch (err: any) {
      // Just set error message but don't display error UI to keep the component subtle
      setError(err.message || "Failed to load email logs");
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "sent":
        return <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">Sent</Badge>;
      case "delivered":
        return <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">Delivered</Badge>;
      case "opened":
        return <Badge variant="outline" className="bg-green-500 text-white">Opened</Badge>;
      case "clicked":
        return <Badge variant="outline" className="bg-purple-500 text-white">Clicked</Badge>;
      case "failed":
        return <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">Failed</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  if (loading && !emails.length) {
    return null; // Don't show loading state initially
  }

  if (error && !emails.length) {
    return null; // Don't show error state if we have no data
  }

  if (!emails.length) {
    return null; // Don't show the component if there are no emails sent
  }

  return (
    <Card className="mt-6">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">Email History</CardTitle>
        <CardDescription>
          Tracking information for emails sent with this invoice
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Recipient</TableHead>
              <TableHead>Sent</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {emails.map((email) => (
              <TableRow key={email.id}>
                <TableCell>{email.recipient}</TableCell>
                <TableCell>{format(new Date(email.sent_at), 'MMM dd, yyyy HH:mm')}</TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    {getStatusBadge(email.status)}
                    {email.error_message && (
                      <span className="text-xs text-red-500" title={email.error_message}>
                        Error
                      </span>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
