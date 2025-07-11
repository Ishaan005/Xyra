'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { useOrganization } from '@/contexts/OrganizationContext'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { FileText, BarChart3 } from 'lucide-react'

// Custom hooks
import { useInvoiceOperations } from './hooks/useInvoiceOperations'
import { useInvoiceFilters } from './hooks/useInvoiceFilters'
import type { GenerateInvoiceForm } from './types'

// Component imports
import InvoiceHeader from '@/app/invoices/components/InvoiceHeader'
import InvoiceFilters from '@/app/invoices/components/InvoiceFilters'
import InvoiceSummaryCards from '@/app/invoices/components/InvoiceSummaryCards'
import InvoiceList from '@/app/invoices/components/InvoiceList'
import EmptyInvoiceState from '@/app/invoices/components/EmptyInvoiceState'
import GenerateInvoiceDialog from '@/app/invoices/components/GenerateInvoiceDialog'
import InvoiceModal from '@/app/invoices/components/InvoiceModal'
import ErrorAlert from '@/app/invoices/components/ErrorAlert'
import InvoiceAnalytics from '@/app/invoices/components/InvoiceAnalytics'



export default function InvoicesPage() {
  const { status } = useSession()
  const { currentOrgId } = useOrganization()
  const [showGenerateDialog, setShowGenerateDialog] = useState(false)
  
  // Invoice operations hook
  const {
    invoices,
    loading,
    error,
    selectedInvoice,
    generating,
    fetchInvoices,
    fetchInvoiceDetail,
    generateMonthlyInvoice,
    downloadPDF,
    markAsPaid,
    bulkMarkAsPaid,
    setSelectedInvoice
  } = useInvoiceOperations()

  // Invoice filtering and selection hook
  const {
    statusFilter,
    setStatusFilter,
    searchQuery,
    setSearchQuery,
    selectedInvoices,
    setSelectedInvoices,
    filteredInvoices,
    pendingInvoicesCount,
    toggleInvoiceSelection,
    selectAllInvoices,
    clearSelection
  } = useInvoiceFilters(invoices)

  // Initial data fetch
  useEffect(() => {
    if (status === 'authenticated' && currentOrgId) {
      fetchInvoices(statusFilter)
    }
  }, [status, currentOrgId, fetchInvoices, statusFilter])

  // Handlers
  const handleGenerateInvoice = async (form: GenerateInvoiceForm) => {
    try {
      await generateMonthlyInvoice(form)
      setShowGenerateDialog(false)
    } catch (error) {
      // Error is handled in the hook
    }
  }

  const handleBulkMarkAsPaid = async () => {
    await bulkMarkAsPaid(selectedInvoices)
    clearSelection()
  }
  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="text-center">Loading invoices...</div>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <InvoiceHeader onGenerateClick={() => setShowGenerateDialog(true)} />

      {/* Error Display */}
      <ErrorAlert error={error} />

      {/* Main Content with Tabs */}
      <Tabs defaultValue="invoices" className="space-y-6">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="invoices" className="flex items-center space-x-2">
            <FileText className="w-4 h-4" />
            <span>Invoices</span>
          </TabsTrigger>
          <TabsTrigger value="analytics" className="flex items-center space-x-2">
            <BarChart3 className="w-4 h-4" />
            <span>Analytics</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="invoices" className="space-y-6">
          {/* Summary Cards */}
          <InvoiceSummaryCards invoices={invoices} />

          {/* Filters */}
          <InvoiceFilters
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            statusFilter={statusFilter}
            setStatusFilter={setStatusFilter}
            selectedInvoices={selectedInvoices}
            setSelectedInvoices={setSelectedInvoices}
            onRefresh={() => fetchInvoices(statusFilter)}
            onBulkMarkAsPaid={handleBulkMarkAsPaid}
            onSelectAllInvoices={selectAllInvoices}
            pendingInvoicesCount={pendingInvoicesCount}
          />

          {/* Invoice List or Empty State */}
          {filteredInvoices.length === 0 && !loading ? (
            <EmptyInvoiceState 
              statusFilter={statusFilter} 
              onGenerateClick={() => setShowGenerateDialog(true)} 
            />
          ) : (
            <InvoiceList
              invoices={filteredInvoices}
              selectedInvoices={selectedInvoices}
              onToggleSelection={toggleInvoiceSelection}
              onViewDetails={fetchInvoiceDetail}
              onDownloadPDF={downloadPDF}
              onMarkAsPaid={markAsPaid}
            />
          )}
        </TabsContent>

        <TabsContent value="analytics" className="space-y-6">
          <InvoiceAnalytics invoices={invoices} />
        </TabsContent>
      </Tabs>

      {/* Generate Invoice Dialog */}
      <GenerateInvoiceDialog
        isOpen={showGenerateDialog}
        onClose={() => setShowGenerateDialog(false)}
        onGenerate={handleGenerateInvoice}
        generating={generating}
      />

      {/* Invoice Detail Modal */}
      <InvoiceModal
        invoice={selectedInvoice}
        isOpen={!!selectedInvoice}
        onClose={() => setSelectedInvoice(null)}
        onDownloadPDF={downloadPDF}
        onMarkAsPaid={markAsPaid}
      />
    </div>
  )
}
