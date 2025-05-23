"use client"

import { useState, useEffect } from "react"
import { useSession } from "next-auth/react"
import { useRouter } from "next/navigation"
import { setAuthToken } from "../../../utils/api"
import api from "../../../utils/api"
import { invoiceApi } from "../../../utils/invoice-api"
import { Button } from "@/components/ui/button"
import { 
  Table, 
  TableBody, 
  TableCaption, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table"
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { Download, Plus } from "lucide-react"
import { format } from "date-fns"
import { Invoice } from "../../../types/invoice"
import { InvoiceFilter, type InvoiceFilters } from "./components/invoice-filter"
import BulkInvoiceOperations from "./components/bulk-invoice-operations"

export default function InvoicesPage() {
  const router = useRouter()
  const { data: session, status } = useSession()
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState<InvoiceFilters>({
    status: "all"
  })
  const [selectedInvoices, setSelectedInvoices] = useState<Invoice[]>([])
  const orgId = 1 // TODO: Get this from user session or context
  
  useEffect(() => {
    if (status === "loading") return
    if (status === "unauthenticated") return router.push("/login")
    if (status === "authenticated" && session?.user?.accessToken) {
      setAuthToken(session.user.accessToken)
      fetchInvoices()
    }
  }, [status, session, router])
  
  const fetchInvoices = async () => {
    try {
      setLoading(true)
      let data: Invoice[];
      
      // Apply filters
      if (filters.status && filters.status !== 'all') {
        data = await invoiceApi.getAllInvoices(orgId, undefined, filters.status);
      } else {
        data = await invoiceApi.getAllInvoices(orgId);
      }
      
      // Client-side filtering
      if (filters.search) {
        const searchLower = filters.search.toLowerCase();
        data = data.filter(invoice => 
          invoice.invoice_number.toLowerCase().includes(searchLower) ||
          (invoice.notes && invoice.notes.toLowerCase().includes(searchLower))
        );
      }
      
      if (filters.startDate) {
        const startDate = new Date(filters.startDate);
        data = data.filter(invoice => new Date(invoice.issue_date) >= startDate);
      }
      
      if (filters.endDate) {
        const endDate = new Date(filters.endDate);
        data = data.filter(invoice => new Date(invoice.issue_date) <= endDate);
      }
      
      if (filters.minAmount !== undefined) {
        data = data.filter(invoice => invoice.total_amount >= filters.minAmount!);
      }
      
      if (filters.maxAmount !== undefined) {
        data = data.filter(invoice => invoice.total_amount <= filters.maxAmount!);
      }
      
      setInvoices(data);
    } catch (err: any) {
      setError(err.message || "Failed to load invoices")
    } finally {
      setLoading(false)
    }
  }
    const handleFilter = (newFilters: InvoiceFilters) => {
    setFilters(newFilters);
    // fetchInvoices will be called after state updates
    setTimeout(fetchInvoices, 0);
  }
  
  const handleResetFilters = () => {
    setFilters({ status: 'all' });
    // fetchInvoices will be called after state updates
    setTimeout(fetchInvoices, 0);
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "paid":
        return <Badge className="bg-green-500">Paid</Badge>
      case "pending":
        return <Badge className="bg-yellow-500">Pending</Badge>
      case "cancelled":
        return <Badge className="bg-red-500">Cancelled</Badge>
      default:
        return <Badge className="bg-gray-500">{status}</Badge>
    }
  }

  if (loading) return <div className="p-8">Loading invoices...</div>
  if (error) return <div className="p-8 text-red-500">Error loading invoices: {error}</div>

  return (
    <div className="p-8">      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Invoices</h1>
        <Button onClick={() => router.push('/dashboard/invoices/create')}>
          <Plus className="mr-2 h-4 w-4" /> Create Invoice
        </Button>
      </div>
      
      {selectedInvoices.length > 0 && (
        <BulkInvoiceOperations
          selectedInvoices={selectedInvoices}
          onDeselectAll={() => setSelectedInvoices([])}
          onOperationComplete={fetchInvoices}
        />
      )}
      
      <InvoiceFilter onFilter={handleFilter} onReset={handleResetFilters} /><Card>
        <CardHeader>
          <CardTitle>Your Invoices</CardTitle>
          <CardDescription>
            View and manage all your invoices
          </CardDescription>
        </CardHeader><CardContent>          <Table>
            <TableHeader>
              <TableRow>                <TableHead className="w-[50px]">
                  <Checkbox 
                    checked={invoices.length > 0 && selectedInvoices.length === invoices.length}
                    onCheckedChange={(checked: boolean | "indeterminate") => {
                      if (checked === true) {
                        setSelectedInvoices(invoices);
                      } else {
                        setSelectedInvoices([]);
                      }
                    }}
                    aria-label="Select all invoices"
                  />
                </TableHead>
                <TableHead>Invoice #</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Due Date</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>              {invoices.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center">No invoices found</TableCell>
                </TableRow>
              ) : (invoices.map((invoice) => (
                  <TableRow key={invoice.id}>
                    <TableCell>
                      <Checkbox
                        checked={selectedInvoices.some(selected => selected.id === invoice.id)}
                        onCheckedChange={(checked: boolean | "indeterminate") => {
                          if (checked === true) {
                            setSelectedInvoices([...selectedInvoices, invoice]);
                          } else {
                            setSelectedInvoices(selectedInvoices.filter(i => i.id !== invoice.id));
                          }
                        }}
                        aria-label={`Select invoice ${invoice.invoice_number}`}
                      />
                    </TableCell>
                    <TableCell>
                      <Button 
                        variant="link" 
                        onClick={() => router.push(`/dashboard/invoices/${invoice.id}`)}
                      >
                        {invoice.invoice_number}
                      </Button>
                    </TableCell>
                    <TableCell>{format(new Date(invoice.issue_date), 'MMM dd, yyyy')}</TableCell>
                    <TableCell>{format(new Date(invoice.due_date), 'MMM dd, yyyy')}</TableCell>
                    <TableCell>{invoice.currency} {invoice.total_amount.toFixed(2)}</TableCell>
                    <TableCell>{getStatusBadge(invoice.status)}</TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => router.push(`/dashboard/invoices/${invoice.id}`)}
                        >
                          View
                        </Button><Button 
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            window.open(invoiceApi.getInvoicePdfUrl(invoice.id), '_blank')
                          }}
                        >
                          <Download className="h-4 w-4 mr-1" /> PDF
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
