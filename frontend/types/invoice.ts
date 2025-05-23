// Invoice types
export interface InvoiceLineItem {
  id: number;
  invoice_id: number;
  description: string;
  quantity: number;
  unit_price: number;
  amount: number;
  item_type: string;
  reference_id?: number;
  reference_type?: string;
  item_metadata?: any;
  created_at: string;
  updated_at: string;
}

export interface Invoice {
  id: number;
  organization_id: number;
  invoice_number: string;
  issue_date: string;
  due_date: string;
  status: 'pending' | 'paid' | 'cancelled' | 'overdue';
  amount: number;
  tax_amount: number;
  total_amount: number;
  currency: string;
  payment_method?: string;
  stripe_invoice_id?: string;
  stripe_checkout_session_id?: string;
  stripe_payment_link?: string;
  payment_date?: string;
  notes?: string;
  invoice_metadata?: any;
  created_at: string;
  updated_at: string;
}

export interface InvoiceWithItems extends Invoice {
  line_items: InvoiceLineItem[];
  pdf_url?: string;
}
