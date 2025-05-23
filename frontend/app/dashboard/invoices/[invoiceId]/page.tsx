"use client"

import { useState, useEffect } from "react"
import { useSession } from "next-auth/react"
import { useRouter } from "next/navigation"
import { setAuthToken } from "../../../../utils/api"
import api from "../../../../utils/api"
import { invoiceApi } from "../../../../utils/invoice-api"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle
} from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Download, ExternalLink, ArrowLeft, Mail, Ban } from "lucide-react"
import { format } from "date-fns"
import { Separator } from "@/components/ui/separator"
import InvoicePaymentEmailDialog from "../components/invoice-payment-email-dialog"
import PaymentStatusAlert from "../components/payment-status-alert"
import ConfirmationDialog from "../components/confirmation-dialog"
import { EmailTracking } from "../components/email-tracking"
import PaymentHistory from "../components/payment-history"
import PdfPreview from "../components/pdf-preview"
import { InvoiceWithItems } from "../../../../types/invoice"

interface InvoiceDetailPageProps {
  params: {
    invoiceId: string;
  };
}

export default function InvoiceDetailPage({ params }: InvoiceDetailPageProps) {
  const router = useRouter()
  const { data: session, status } = useSession()
  const [invoice, setInvoice] = useState<InvoiceWithItems | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isEmailDialogOpen, setIsEmailDialogOpen] = useState(false)
  const [isConfirmCancelOpen, setIsConfirmCancelOpen] = useState(false)
  const [isPdfPreviewOpen, setIsPdfPreviewOpen] = useState(false)
  const [isCancelling, setIsCancelling] = useState(false)
  const invoiceId = params.invoiceId

  useEffect(() => {
    if (status === "loading") return
    if (status === "unauthenticated") return router.push("/login")
    if (status === "authenticated" && session?.user?.accessToken) {
      setAuthToken(session.user.accessToken)
      fetchInvoice()
    }
  }, [status, session, router])
  const fetchInvoice = async () => {
    try {
      setLoading(true)
      const data = await invoiceApi.getInvoice(parseInt(invoiceId))
      setInvoice(data)
    } catch (err: any) {
      setError(err.message || "Failed to load invoice")
    } finally {
      setLoading(false)
    }
  }

  const cancelInvoice = async () => {
    try {
      setIsCancelling(true)
      await invoiceApi.cancelInvoice(parseInt(invoiceId))
      // Refresh the invoice data
      fetchInvoice()
    } catch (err: any) {
      setError(err.message || "Failed to cancel invoice")
    } finally {
      setIsCancelling(false)
    }
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

  if (loading) return <div className="p-8">Loading invoice details...</div>
  if (error) return <div className="p-8 text-red-500">Error loading invoice: {error}</div>;
  if (!invoice) return <div className="p-8">Invoice not found</div>;

  const pdfUrl = invoiceApi.getInvoicePdfUrl(invoice.id)

  return (
    <div className="p-8">
      <Button 
        variant="ghost" 
        onClick={() => router.back()}
        className="mb-6"
      >
        <ArrowLeft className="h-4 w-4 mr-2" /> Back to Invoices
      </Button>      <PaymentStatusAlert />
      
      <Card className="mb-6">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Invoice {invoice.invoice_number}</CardTitle>
            <CardDescription>
              Issued: {format(new Date(invoice.issue_date), 'MMM dd, yyyy')}
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            {getStatusBadge(invoice.status)}
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Due Date</h3>
              <p>{format(new Date(invoice.due_date), 'MMM dd, yyyy')}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Total Amount</h3>
              <p className="text-xl font-bold">{invoice.currency} {invoice.total_amount.toFixed(2)}</p>
            </div>
          </div>

          <Separator className="my-4" />

          <h3 className="font-medium mb-4">Invoice Items</h3>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Description</TableHead>
                <TableHead>Quantity</TableHead>
                <TableHead>Unit Price</TableHead>
                <TableHead className="text-right">Amount</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {invoice.line_items && invoice.line_items.length > 0 ? (
                invoice.line_items.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>{item.description}</TableCell>
                    <TableCell>{item.quantity}</TableCell>
                    <TableCell>{invoice.currency} {item.unit_price.toFixed(2)}</TableCell>
                    <TableCell className="text-right">{invoice.currency} {item.amount.toFixed(2)}</TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={4} className="text-center">No items found</TableCell>
                </TableRow>
              )}
              <TableRow>
                <TableCell colSpan={3} className="text-right font-medium">Subtotal:</TableCell>
                <TableCell className="text-right">{invoice.currency} {invoice.amount.toFixed(2)}</TableCell>
              </TableRow>
              {invoice.tax_amount > 0 && (
                <TableRow>
                  <TableCell colSpan={3} className="text-right font-medium">Tax:</TableCell>
                  <TableCell className="text-right">{invoice.currency} {invoice.tax_amount.toFixed(2)}</TableCell>
                </TableRow>
              )}
              <TableRow>
                <TableCell colSpan={3} className="text-right font-bold">Total:</TableCell>
                <TableCell className="text-right font-bold">{invoice.currency} {invoice.total_amount.toFixed(2)}</TableCell>
              </TableRow>
            </TableBody>
          </Table>

          {invoice.notes && (
            <div className="mt-6">
              <h3 className="font-medium mb-2">Notes</h3>
              <p className="text-gray-600">{invoice.notes}</p>
            </div>
          )}
        </CardContent>

        <CardFooter className="flex justify-between flex-wrap gap-2">          <div>
            <Button 
              variant="outline"
              onClick={() => setIsPdfPreviewOpen(true)}
              className="mr-2"
            >
              <Download className="h-4 w-4 mr-2" /> View PDF
            </Button>
            
            <Button 
              variant="outline"
              onClick={() => setIsEmailDialogOpen(true)}
            >
              <Mail className="h-4 w-4 mr-2" /> Share Invoice
            </Button>
          </div>

          <div>
            {invoice.status === "pending" && (
              <Button
                variant="outline"
                onClick={() => setIsConfirmCancelOpen(true)}
                className="border-red-200 text-red-600 hover:bg-red-50 mr-2"
                disabled={isCancelling}
              >
                <Ban className="h-4 w-4 mr-2" /> 
                {isCancelling ? "Cancelling..." : "Cancel Invoice"}
              </Button>
            )}

            {invoice.status === "pending" && invoice.stripe_payment_link && (
              <Button 
                onClick={() => window.open(invoice.stripe_payment_link, '_blank')}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <ExternalLink className="h-4 w-4 mr-2" /> Pay Now
              </Button>
            )}          </div>
        </CardFooter>
      </Card>

      {/* Email tracking for this invoice */}
      <EmailTracking invoiceId={invoice.id} />
      
      {/* Payment history for this invoice */}
      <PaymentHistory invoiceId={invoice.id} />

      <InvoicePaymentEmailDialog
        isOpen={isEmailDialogOpen}
        onClose={() => setIsEmailDialogOpen(false)}
        invoiceNumber={invoice.invoice_number}
        recipientEmail=""
        paymentLink={invoice.stripe_payment_link}
        pdfUrl={pdfUrl}
      />

      <PdfPreview
        isOpen={isPdfPreviewOpen}
        onClose={() => setIsPdfPreviewOpen(false)}
        pdfUrl={pdfUrl}
        title={`Invoice #${invoice.invoice_number}`}
      />

      <ConfirmationDialog
        isOpen={isConfirmCancelOpen}
        onClose={() => setIsConfirmCancelOpen(false)}
        onConfirm={cancelInvoice}
        title="Cancel Invoice"
        description="Are you sure you want to cancel this invoice? This action cannot be undone."
        confirmLabel="Yes, Cancel Invoice"
        cancelLabel="No, Keep Invoice"
        variant="destructive"
      />
    </div>
  )
}
