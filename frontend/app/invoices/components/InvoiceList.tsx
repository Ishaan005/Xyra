'use client'

import { memo } from 'react'
import InvoiceCard from './InvoiceCard'
import type { Invoice } from '../types'

interface InvoiceListProps {
  invoices: Invoice[]
  selectedInvoices: number[]
  onToggleSelection: (invoiceId: number) => void
  onViewDetails: (invoiceId: number) => void
  onDownloadPDF: (invoiceId: number, invoiceNumber: string) => void
  onMarkAsPaid: (invoiceId: number) => void
}

const InvoiceList = memo(function InvoiceList({
  invoices,
  selectedInvoices,
  onToggleSelection,
  onViewDetails,
  onDownloadPDF,
  onMarkAsPaid
}: InvoiceListProps) {
  return (
    <div className="grid gap-4">
      {invoices.map((invoice) => (
        <InvoiceCard
          key={invoice.id}
          invoice={invoice}
          isSelected={selectedInvoices.includes(invoice.id)}
          onToggleSelection={onToggleSelection}
          onViewDetails={onViewDetails}
          onDownloadPDF={onDownloadPDF}
          onMarkAsPaid={onMarkAsPaid}
        />
      ))}
    </div>
  )
})

export default InvoiceList
