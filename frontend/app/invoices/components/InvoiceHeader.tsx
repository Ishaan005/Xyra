'use client'

import { memo } from 'react'
import { Button } from '@/components/ui/button'
import { Plus } from 'lucide-react'

interface InvoiceHeaderProps {
  onGenerateClick: () => void
}

const InvoiceHeader = memo(function InvoiceHeader({ onGenerateClick }: InvoiceHeaderProps) {
  return (
    <div className="flex justify-between items-center">
      <div>
        <h1 className="text-3xl font-bold">Invoices</h1>
        <p className="text-muted-foreground">Manage your organization's invoices and billing</p>
      </div>
      
      <Button onClick={onGenerateClick}>
        <Plus className="w-4 h-4 mr-2" />
        Generate Invoice
      </Button>
    </div>
  )
})

export default InvoiceHeader
