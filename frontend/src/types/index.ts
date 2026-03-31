export interface Company {
  id: string
  company_name: string
  email: string
  phone?: string
  country?: string
  address?: string
  rccm?: string
  tax_number?: string
  website?: string
  legal_representative?: string
  status: string
  is_validated: boolean
  validated_at?: string
  documents_submitted?: boolean
  documents_validated?: boolean
  documents_validated_at?: string
  documents_rejection_reason?: string
  subscription_plan?: string
  monthly_quota: number
  quota_used: number
  subscription_expires_at?: string
  public_key?: string
  secret_key?: string
  webhook_url?: string
  webhook_secret?: string
  created_at: string
  updated_at?: string
}

export interface SubscriptionPlan {
  id: string
  name: string
  slug: string
  description: string
  price: number
  currency: string
  billing_period: string
  monthly_quota: number
  max_api_keys?: number
  max_users?: number
  features: {
    webhook_support: boolean
    priority_support: boolean
    custom_branding: boolean
    api_access: boolean
    bulk_upload: boolean
    advanced_analytics: boolean
    [key: string]: boolean
  }
  advantages: string[]
  is_active: boolean
  is_popular: boolean
  is_custom: boolean
  display_order: number
}

export interface Payment {
  id: string
  payment_reference: string
  company_id: string
  plan_id: string
  amount: number
  currency: string
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
  payment_method: string
  created_at: string
  paid_at?: string
}

export interface Verification {
  verification_id: string
  company_id: string
  first_name: string
  last_name: string
  date_of_birth: string
  document_type: string
  document_number: string
  status: 'pending' | 'processing' | 'verified' | 'rejected'
  created_at: string
  updated_at: string
}

export interface AdminUser {
  id: string
  username: string
  email: string
  full_name: string
  role: 'super_admin' | 'admin' | 'support'
  is_active: boolean
  created_at: string
}
