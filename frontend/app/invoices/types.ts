// Types for invoice components

export interface Invoice {
  id: number
  invoice_number: string
  organization_id: number
  issue_date: string
  due_date: string
  status: string
  amount: number
  tax_amount: number
  total_amount: number
  currency: string
  payment_method?: string
  payment_date?: string
  notes?: string
  line_items?: InvoiceLineItem[]
}

export interface InvoiceLineItem {
  id: number
  description: string
  quantity: number
  unit_price: number
  amount: number
  item_type: string // subscription, usage, outcome, workflow
  reference_id?: number
  reference_type?: string
  item_metadata?: {
    billing_model_id?: number
    billing_period?: string
    // Outcome-based metadata
    outcome_value?: number
    outcome_count?: number
    percentage_fee?: number
    fixed_fee?: number
    total_fee?: number
    outcome_type?: string
    // Activity-based metadata
    activity_type?: string
    tier_breakdown?: {
      tier_1_units?: number
      tier_1_cost?: number
      tier_2_units?: number
      tier_2_cost?: number
      tier_3_units?: number
      tier_3_cost?: number
    }
    // Agent-based metadata
    agent_tier?: string
    volume_discount_applied?: boolean
    setup_fee_included?: boolean
    // Workflow-based metadata
    workflow_type?: string
    workflow_count?: number
    [key: string]: any
  }
}

export interface GenerateInvoiceForm {
  month: number
  year: number
}
