'use client'

import { memo } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import { Eye, Download, CreditCard, Calendar, DollarSign } from 'lucide-react'
import { format } from 'date-fns'
import type { Invoice } from '../types'

interface InvoiceCardProps {
  invoice: Invoice
  isSelected: boolean
  onToggleSelection: (invoiceId: number) => void
  onViewDetails: (invoiceId: number) => void
  onDownloadPDF: (invoiceId: number, invoiceNumber: string) => void
  onMarkAsPaid: (invoiceId: number) => void
}

const InvoiceCard = memo(function InvoiceCard({
  invoice,
  isSelected,
  onToggleSelection,
  onViewDetails,
  onDownloadPDF,
  onMarkAsPaid
}: InvoiceCardProps) {
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

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="pt-6">
        <div className="flex justify-between items-start">
          <div className="flex items-start space-x-3">
            {/* Checkbox for bulk operations (only for pending invoices) */}
            {invoice.status === 'pending' && (
              <Checkbox
                checked={isSelected}
                onCheckedChange={() => onToggleSelection(invoice.id)}
                className="mt-1"
              />
            )}
            
            <div className="space-y-2 flex-1">
              <div className="flex items-center space-x-3">
                <h3 className="font-semibold text-lg">{invoice.invoice_number}</h3>
                {getStatusBadge(invoice.status)}
              </div>
            
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-muted-foreground">
                <div className="flex items-center space-x-2">
                  <Calendar className="w-4 h-4" />
                  <span>Issued: {format(new Date(invoice.issue_date), 'MMM dd, yyyy')}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Calendar className="w-4 h-4" />
                  <span>Due: {format(new Date(invoice.due_date), 'MMM dd, yyyy')}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <DollarSign className="w-4 h-4" />
                  <span>Amount: ${invoice.total_amount.toFixed(2)}</span>
                </div>
                {invoice.payment_date && (
                  <div className="flex items-center space-x-2">
                    <CreditCard className="w-4 h-4" />
                    <span>Paid: {format(new Date(invoice.payment_date), 'MMM dd, yyyy')}</span>
                  </div>
                )}
              </div>
              
              {invoice.notes && (
                <p className="text-sm text-muted-foreground mt-2">{invoice.notes}</p>
              )}
            </div>
          </div>
          
          <div className="flex space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onViewDetails(invoice.id)}
            >
              <Eye className="w-4 h-4 mr-1" />
              View
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => onDownloadPDF(invoice.id, invoice.invoice_number)}
            >
              <Download className="w-4 h-4 mr-1" />
              PDF
            </Button>
            
            {invoice.status === 'pending' && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  if (confirm(`Are you sure you want to mark invoice ${invoice.invoice_number} as paid?`)) {
                    onMarkAsPaid(invoice.id)
                  }
                }}
              >
                <CreditCard className="w-4 h-4 mr-1" />
                Mark Paid
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
})

export default InvoiceCard
