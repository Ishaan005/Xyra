'use client'

import { useState, useMemo, useCallback } from 'react'
import type { Invoice } from '../types'

export function useInvoiceFilters(invoices: Invoice[]) {
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedInvoices, setSelectedInvoices] = useState<number[]>([])

  const filteredInvoices = useMemo(() => {
    return invoices.filter(invoice => {
      const matchesSearch = invoice.invoice_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           invoice.notes?.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesStatus = statusFilter === 'all' || invoice.status === statusFilter
      return matchesSearch && matchesStatus
    })
  }, [invoices, searchQuery, statusFilter])

  const pendingInvoicesCount = useMemo(() => {
    return filteredInvoices.filter(inv => inv.status === 'pending').length
  }, [filteredInvoices])

  const toggleInvoiceSelection = useCallback((invoiceId: number) => {
    setSelectedInvoices(prev => 
      prev.includes(invoiceId) 
        ? prev.filter(id => id !== invoiceId)
        : [...prev, invoiceId]
    )
  }, [])

  const selectAllInvoices = useCallback(() => {
    const pendingInvoiceIds = filteredInvoices
      .filter(inv => inv.status === 'pending')
      .map(inv => inv.id)
    setSelectedInvoices(pendingInvoiceIds)
  }, [filteredInvoices])

  const clearSelection = useCallback(() => {
    setSelectedInvoices([])
  }, [])

  return {
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
  }
}
