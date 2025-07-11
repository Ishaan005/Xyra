'use client'

import { memo } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { CreditCard } from 'lucide-react'

interface InvoiceFiltersProps {
  searchQuery: string
  setSearchQuery: (query: string) => void
  statusFilter: string
  setStatusFilter: (status: string) => void
  selectedInvoices: number[]
  setSelectedInvoices: (invoices: number[]) => void
  onRefresh: () => void
  onBulkMarkAsPaid: () => void
  onSelectAllInvoices: () => void
  pendingInvoicesCount: number
}

const InvoiceFilters = memo(function InvoiceFilters({
  searchQuery,
  setSearchQuery,
  statusFilter,
  setStatusFilter,
  selectedInvoices,
  setSelectedInvoices,
  onRefresh,
  onBulkMarkAsPaid,
  onSelectAllInvoices,
  pendingInvoicesCount
}: InvoiceFiltersProps) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex space-x-4">
          <div className="flex-1">
            <Input
              placeholder="Search invoices..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="processing">Processing</SelectItem>
              <SelectItem value="paid">Paid</SelectItem>
              <SelectItem value="overdue">Overdue</SelectItem>
              <SelectItem value="cancelled">Cancelled</SelectItem>
              <SelectItem value="failed">Failed</SelectItem>
            </SelectContent>
          </Select>
          
          <div className="flex justify-end space-x-2">
            <Button variant="outline" onClick={onRefresh}>
              Refresh
            </Button>
            
            {selectedInvoices.length > 0 && (
              <>
                <Button 
                  variant="outline" 
                  onClick={() => setSelectedInvoices([])}
                >
                  Clear ({selectedInvoices.length})
                </Button>
                <Button 
                  onClick={onBulkMarkAsPaid}
                  disabled={selectedInvoices.length === 0}
                >
                  <CreditCard className="w-4 h-4 mr-2" />
                  Mark {selectedInvoices.length} as Paid
                </Button>
              </>
            )}
            
            {pendingInvoicesCount > 0 && selectedInvoices.length === 0 && (
              <Button variant="outline" onClick={onSelectAllInvoices}>
                Select All Pending
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
})

export default InvoiceFilters
