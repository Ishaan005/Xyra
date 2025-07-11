'use client'

import { memo } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { FileText } from 'lucide-react'

interface EmptyInvoiceStateProps {
  statusFilter: string
  onGenerateClick: () => void
}

const EmptyInvoiceState = memo(function EmptyInvoiceState({ statusFilter, onGenerateClick }: EmptyInvoiceStateProps) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="text-center py-8">
          <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium mb-2">No invoices found</h3>
          <p className="text-muted-foreground mb-4">
            {statusFilter === 'all' 
              ? 'No invoices have been generated yet.' 
              : `No ${statusFilter} invoices found.`}
          </p>
          <Button onClick={onGenerateClick}>
            Generate First Invoice
          </Button>
        </div>
      </CardContent>
    </Card>
  )
})

export default EmptyInvoiceState
