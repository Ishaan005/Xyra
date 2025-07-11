'use client'

import { useState, useCallback } from 'react'
import { useSession } from 'next-auth/react'
import { useOrganization } from '@/contexts/OrganizationContext'
import api, { setAuthToken } from '@/utils/api'
import type { Invoice, GenerateInvoiceForm } from '../types'

export function useInvoiceOperations() {
  const { data: session } = useSession()
  const { currentOrgId } = useOrganization()
  
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null)
  const [generating, setGenerating] = useState(false)

  const fetchInvoices = useCallback(async (statusFilter?: string) => {
    try {
      setLoading(true)
      const token = session?.user?.accessToken ?? ""
      setAuthToken(token)
      
      const params = new URLSearchParams({
        org_id: currentOrgId?.toString() || '',
        limit: '100'
      })
      
      if (statusFilter && statusFilter !== 'all') {
        params.append('status', statusFilter)
      }

      const response = await api.get(`/invoices/?${params}`)
      setInvoices(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }, [session, currentOrgId])

  const fetchInvoiceDetail = useCallback(async (invoiceId: number) => {
    try {
      const response = await api.get(`/invoices/${invoiceId}`)
      setSelectedInvoice(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message)
    }
  }, [])

  const generateMonthlyInvoice = useCallback(async (form: GenerateInvoiceForm) => {
    try {
      setGenerating(true)
      const params = new URLSearchParams({
        org_id: currentOrgId?.toString() || '',
        month: form.month.toString(),
        year: form.year.toString()
      })

      const response = await api.post(`/invoices/generate/monthly?${params}`)
      setInvoices(prev => [response.data, ...prev])
      setError('')
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message)
      throw err
    } finally {
      setGenerating(false)
    }
  }, [currentOrgId])

  const downloadPDF = useCallback(async (invoiceId: number, invoiceNumber: string) => {
    try {
      const response = await api.get(`/invoices/${invoiceId}/pdf`, {
        responseType: 'blob'
      })
      
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `invoice_${invoiceNumber}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (err: any) {
      setError('Failed to download PDF')
    }
  }, [])

  const markAsPaid = useCallback(async (invoiceId: number) => {
    try {
      const paymentData = {
        payment_method: 'manual',
        payment_date: new Date().toISOString()
      }
      
      await api.post(`/invoices/${invoiceId}/pay`, paymentData)
      await fetchInvoices() // Refresh the list
      if (selectedInvoice?.id === invoiceId) {
        await fetchInvoiceDetail(invoiceId) // Refresh detail view
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message)
    }
  }, [fetchInvoices, fetchInvoiceDetail, selectedInvoice])

  const bulkMarkAsPaid = useCallback(async (invoiceIds: number[]) => {
    try {
      const promises = invoiceIds.map(invoiceId => {
        const paymentData = {
          payment_method: 'manual',
          payment_date: new Date().toISOString()
        }
        return api.post(`/invoices/${invoiceId}/pay`, paymentData)
      })
      
      await Promise.all(promises)
      await fetchInvoices()
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message)
    }
  }, [fetchInvoices])

  const clearError = useCallback(() => {
    setError('')
  }, [])

  return {
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
    setSelectedInvoice,
    clearError
  }
}
