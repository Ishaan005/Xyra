'use client'

import { memo } from 'react'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Download, CreditCard } from 'lucide-react'
import { format } from 'date-fns'
import BillingModelSummary from './BillingModelSummary'
import type { Invoice, InvoiceLineItem } from '../types'

interface InvoiceModalProps {
  invoice: Invoice | null
  isOpen: boolean
  onClose: () => void
  onDownloadPDF: (invoiceId: number, invoiceNumber: string) => void
  onMarkAsPaid: (invoiceId: number) => void
}

const InvoiceModal = memo(function InvoiceModal({
  invoice,
  isOpen,
  onClose,
  onDownloadPDF,
  onMarkAsPaid
}: InvoiceModalProps) {
  if (!invoice) return null

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { variant: 'default' | 'secondary' | 'destructive' | 'outline', text: string }> = {
      pending: { variant: 'outline', text: 'Pending' },
      paid: { variant: 'default', text: 'Paid' },
      overdue: { variant: 'destructive', text: 'Overdue' },
      cancelled: { variant: 'secondary', text: 'Cancelled' },
      processing: { variant: 'outline', text: 'Processing' },
      failed: { variant: 'destructive', text: 'Failed' }
    }
    
    const config = variants[status] || { variant: 'outline', text: status }
    return <Badge variant={config.variant}>{config.text}</Badge>
  }

  const getItemTypeBadge = (itemType: string) => {
    const variants: Record<string, { variant: 'default' | 'secondary' | 'destructive' | 'outline', text: string, color: string }> = {
      subscription: { variant: 'default', text: 'Subscription', color: 'bg-blue-100 text-blue-800' },
      usage: { variant: 'secondary', text: 'Usage', color: 'bg-green-100 text-green-800' },
      outcome: { variant: 'outline', text: 'Outcome', color: 'bg-purple-100 text-purple-800' },
      workflow: { variant: 'outline', text: 'Workflow', color: 'bg-orange-100 text-orange-800' }
    }
    
    const config = variants[itemType] || { variant: 'outline', text: itemType, color: 'bg-gray-100 text-gray-800' }
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
        {config.text}
      </span>
    )
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-7xl w-[95vw] max-h-[95vh] overflow-hidden flex flex-col">
        <DialogHeader className="flex-shrink-0 pb-4 border-b">
          <div className="flex items-center justify-between">
            <div>
              <DialogTitle className="text-xl">Invoice {invoice.invoice_number}</DialogTitle>
              <DialogDescription>
                Detailed view of invoice and line items
              </DialogDescription>
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => onDownloadPDF(invoice.id, invoice.invoice_number)}
              >
                <Download className="w-4 h-4 mr-2" />
                Download PDF
              </Button>
              {invoice.status === 'pending' && (
                <Button
                  size="sm"
                  onClick={() => {
                    if (confirm(`Are you sure you want to mark invoice ${invoice.invoice_number} as paid?`)) {
                      onMarkAsPaid(invoice.id)
                    }
                  }}
                >
                  <CreditCard className="w-4 h-4 mr-2" />
                  Mark as Paid
                </Button>
              )}
            </div>
          </div>
        </DialogHeader>
        
        <div className="flex-1 overflow-y-auto">
          <div className="space-y-6 p-1">
            {/* Invoice Header */}
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
              <div className="xl:col-span-2">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-base">Invoice Information</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Number:</span>
                        <span className="font-medium">{invoice.invoice_number}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Status:</span>
                        <div>{getStatusBadge(invoice.status)}</div>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Issue Date:</span>
                        <span>{format(new Date(invoice.issue_date), 'MMM dd, yyyy')}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Due Date:</span>
                        <span>{format(new Date(invoice.due_date), 'MMM dd, yyyy')}</span>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-base">Payment Information</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Amount:</span>
                        <span>${invoice.amount.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Tax:</span>
                        <span>${invoice.tax_amount.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between font-medium text-base">
                        <span>Total:</span>
                        <span>${invoice.total_amount.toFixed(2)}</span>
                      </div>
                      {invoice.payment_method && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Payment Method:</span>
                          <span className="capitalize">{invoice.payment_method}</span>
                        </div>
                      )}
                      {invoice.payment_date && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Paid Date:</span>
                          <span>{format(new Date(invoice.payment_date), 'MMM dd, yyyy')}</span>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </div>
              </div>

              {/* Billing Model Summary */}
              <div>
                <BillingModelSummary lineItems={invoice.line_items} />
              </div>
            </div>
            
            {/* Line Items */}
            {invoice.line_items && invoice.line_items.length > 0 && (
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Line Items</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-muted/50">
                        <tr>
                          <th className="p-4 text-left font-medium">Description</th>
                          <th className="p-4 text-right font-medium">Qty</th>
                          <th className="p-4 text-right font-medium">Unit Price</th>
                          <th className="p-4 text-right font-medium">Amount</th>
                          <th className="p-4 text-center font-medium">Type</th>
                        </tr>
                      </thead>
                      <tbody>
                        {invoice.line_items.map((item) => (
                          <tr key={item.id} className="border-t hover:bg-muted/25">
                            <td className="p-4">
                              <div className="space-y-1">
                                <div className="font-medium text-sm break-words">{item.description}</div>
                                <div className="text-xs text-muted-foreground space-y-1">
                                  {item.reference_type && (
                                    <div className="flex items-center gap-1">
                                      <span className="inline-block w-2 h-2 bg-gray-300 rounded-full"></span>
                                      <span>Ref: {item.reference_type}</span>
                                    </div>
                                  )}
                                  {item.item_metadata?.billing_period && (
                                    <div className="flex items-center gap-1">
                                      <span className="inline-block w-2 h-2 bg-blue-300 rounded-full"></span>
                                      <span>Period: {item.item_metadata.billing_period}</span>
                                    </div>
                                  )}
                                  {item.item_metadata?.outcome_value && (
                                    <div className="flex items-center gap-1">
                                      <span className="inline-block w-2 h-2 bg-purple-300 rounded-full"></span>
                                      <span>Outcome Value: ${item.item_metadata.outcome_value.toFixed(2)}</span>
                                    </div>
                                  )}
                                  {item.item_metadata?.activity_type && (
                                    <div className="flex items-center gap-1">
                                      <span className="inline-block w-2 h-2 bg-green-300 rounded-full"></span>
                                      <span>Activity: {item.item_metadata.activity_type}</span>
                                    </div>
                                  )}
                                  {item.item_metadata?.agent_tier && (
                                    <div className="flex items-center gap-1">
                                      <span className="inline-block w-2 h-2 bg-orange-300 rounded-full"></span>
                                      <span>Tier: {item.item_metadata.agent_tier}</span>
                                    </div>
                                  )}
                                  {item.item_metadata?.volume_discount_applied && (
                                    <div className="flex items-center gap-1 text-green-600">
                                      <span className="inline-block w-2 h-2 bg-green-500 rounded-full"></span>
                                      <span>✓ Volume discount applied</span>
                                    </div>
                                  )}
                                  {item.item_metadata?.tier_breakdown && (
                                    <div className="flex items-center gap-1">
                                      <span className="inline-block w-2 h-2 bg-yellow-300 rounded-full"></span>
                                      <span>Tiered pricing applied</span>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </td>
                            <td className="p-4 text-right font-mono text-sm">{item.quantity}</td>
                            <td className="p-4 text-right font-mono text-sm">${item.unit_price.toFixed(2)}</td>
                            <td className="p-4 text-right font-mono text-sm font-medium">${item.amount.toFixed(2)}</td>
                            <td className="p-4 text-center">
                              {getItemTypeBadge(item.item_type)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            )}
            
            {/* Notes */}
            {invoice.notes && (
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Notes</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground whitespace-pre-wrap break-words">
                    {invoice.notes}
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
})

export default InvoiceModal
