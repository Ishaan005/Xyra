import api from './api';
import { Invoice, InvoiceWithItems } from '../types/invoice';

export const invoiceApi = {
  /**
   * Get all invoices for an organization
   */
  getAllInvoices: async (orgId: number, limit?: number, status?: string): Promise<Invoice[]> => {
    let url = `/invoices/?org_id=${orgId}`;
    if (limit) url += `&limit=${limit}`;
    if (status) url += `&status=${status}`;
    
    const response = await api.get(url);
    return response.data;
  },
  
  /**
   * Get a single invoice by ID with all line items
   */
  getInvoice: async (invoiceId: number): Promise<InvoiceWithItems> => {
    const response = await api.get(`/invoices/${invoiceId}`);
    return response.data;
  },
  
  /**
   * Create a new invoice
   */
  createInvoice: async (invoiceData: any): Promise<InvoiceWithItems> => {
    const response = await api.post('/invoices/', invoiceData);
    return response.data;
  },
  
  /**
   * Update an invoice
   */
  updateInvoice: async (invoiceId: number, updateData: any): Promise<InvoiceWithItems> => {
    const response = await api.patch(`/invoices/${invoiceId}`, updateData);
    return response.data;
  },
  
  /**
   * Cancel an invoice
   */
  cancelInvoice: async (invoiceId: number): Promise<InvoiceWithItems> => {
    const response = await api.post(`/invoices/${invoiceId}/cancel`);
    return response.data;
  },
  
  /**
   * Send an invoice via email
   */
  sendInvoiceEmail: async (
    invoiceNumber: string,
    recipientEmail: string,
    options?: {
      paymentLink?: string;
      includePdf?: boolean;
      message?: string;
    }
  ): Promise<{success: boolean}> => {
    const response = await api.post(`/invoices/send-email`, {
      invoice_number: invoiceNumber,
      recipient_email: recipientEmail,
      payment_link: options?.paymentLink || null,
      include_pdf: options?.includePdf !== undefined ? options.includePdf : true,
      message: options?.message || null
    });
    return response.data;
  },
  
  /**
   * Get invoice PDF URL
   */
  getInvoicePdfUrl: (invoiceId: number): string => {
    return `/api/v1/invoices/${invoiceId}/pdf`;
  },
  
  /**
   * Get analytics for invoices
   */
  getInvoiceAnalytics: async (
    orgId: number, 
    period: 'week' | 'month' | 'quarter' | 'year' = 'month'
  ): Promise<any> => {
    const response = await api.get(`/analytics/invoices/?org_id=${orgId}&period=${period}`);
    return response.data;
  }
};
