'use client'

import { memo } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { FileText, DollarSign, CreditCard, AlertCircle } from 'lucide-react'
import type { Invoice } from '../types'

interface InvoiceSummaryCardsProps {
  invoices: Invoice[]
}

const InvoiceSummaryCards = memo(function InvoiceSummaryCards({ invoices }: InvoiceSummaryCardsProps) {
  if (invoices.length === 0) return null

  const totalAmount = invoices.reduce((sum, inv) => sum + inv.total_amount, 0)
  const paidAmount = invoices.filter(inv => inv.status === 'paid').reduce((sum, inv) => sum + inv.total_amount, 0)
  const pendingAmount = invoices.filter(inv => inv.status === 'pending').reduce((sum, inv) => sum + inv.total_amount, 0)

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center space-x-2">
            <FileText className="w-4 h-4 text-muted-foreground" />
            <div>
              <p className="text-sm font-medium">Total Invoices</p>
              <p className="text-2xl font-bold">{invoices.length}</p>
            </div>
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center space-x-2">
            <DollarSign className="w-4 h-4 text-muted-foreground" />
            <div>
              <p className="text-sm font-medium">Total Amount</p>
              <p className="text-2xl font-bold">
                ${totalAmount.toFixed(2)}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center space-x-2">
            <CreditCard className="w-4 h-4 text-green-600" />
            <div>
              <p className="text-sm font-medium">Paid</p>
              <p className="text-2xl font-bold text-green-600">
                ${paidAmount.toFixed(2)}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-yellow-600" />
            <div>
              <p className="text-sm font-medium">Pending</p>
              <p className="text-2xl font-bold text-yellow-600">
                ${pendingAmount.toFixed(2)}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
})

export default InvoiceSummaryCards
