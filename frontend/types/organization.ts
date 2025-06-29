export interface Organization {
  id: number;
  name: string;
  description?: string;
  external_id?: string;
  status: string;
  billing_email?: string;
  contact_name?: string;
  contact_phone?: string;
  timezone: string;
  settings: Record<string, any>;
  created_at: string;
  updated_at: string;
  stripe_customer_id?: string;
}

export interface OrganizationWithStats extends Organization {
  agent_count: number;
  active_agent_count: number;
  monthly_cost: number;
  monthly_revenue: number;
}

export interface OrganizationCreate {
  name: string;
  description?: string;
  external_id?: string;
  status?: string;
  billing_email?: string;
  contact_name?: string;
  contact_phone?: string;
  timezone?: string;
  settings?: Record<string, any>;
}

export interface OrganizationUpdate {
  name?: string;
  description?: string;
  external_id?: string;
  status?: string;
  billing_email?: string;
  contact_name?: string;
  contact_phone?: string;
  timezone?: string;
  settings?: Record<string, any>;
}
