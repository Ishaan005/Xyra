import React, { createContext, useContext, useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { usePathname } from 'next/navigation'
import api, { setAuthToken } from '@/utils/api'

interface Organization {
  id: number
  name: string
  description?: string
  status: string
}

interface OrganizationContextType {
  currentOrgId: number | null
  setCurrentOrgId: (orgId: number) => void
  organizations: Organization[]
  loading: boolean
  error: string | null
  refreshOrganizations: () => Promise<void>
}

const OrganizationContext = createContext<OrganizationContextType | undefined>(undefined)

export function useOrganization() {
  const context = useContext(OrganizationContext)
  if (context === undefined) {
    throw new Error('useOrganization must be used within an OrganizationProvider')
  }
  return context
}

interface OrganizationProviderProps {
  children: React.ReactNode
}

export function OrganizationProvider({ children }: OrganizationProviderProps) {
  const { data: session, status } = useSession()
  const pathname = usePathname()
  const [currentOrgId, setCurrentOrgIdState] = useState<number | null>(null)
  const [organizations, setOrganizations] = useState<Organization[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Check if we're on a page that needs organization data
  const shouldFetchOrganizations = !['/login', '/signup', '/'].includes(pathname)

  // Load saved organization from localStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedOrgId = localStorage.getItem('currentOrgId')
      if (savedOrgId) {
        setCurrentOrgIdState(parseInt(savedOrgId, 10))
      }
    }
  }, [])

  // Set current org and save to localStorage
  const setCurrentOrgId = (orgId: number) => {
    setCurrentOrgIdState(orgId)
    if (typeof window !== 'undefined') {
      localStorage.setItem('currentOrgId', orgId.toString())
    }
  }

  // Fetch organizations
  const refreshOrganizations = async () => {
    if (status !== 'authenticated' || !session?.user?.accessToken || !shouldFetchOrganizations) {
      setLoading(false)
      return
    }

    setLoading(true)
    setError(null)
    try {
      setAuthToken(session.user.accessToken)
      const response = await api.get<Organization[]>('/organizations')
      setOrganizations(response.data)
      
      // If no current org is set, default to first org
      if (!currentOrgId && response.data.length > 0) {
        setCurrentOrgId(response.data[0].id)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load organizations')
    } finally {
      setLoading(false)
    }
  }

  // Fetch organizations when authenticated and on appropriate pages
  useEffect(() => {
    if (shouldFetchOrganizations) {
      refreshOrganizations()
    } else {
      setLoading(false)
    }
  }, [status, session, shouldFetchOrganizations])

  const value = {
    currentOrgId,
    setCurrentOrgId,
    organizations,
    loading,
    error,
    refreshOrganizations,
  }

  return (
    <OrganizationContext.Provider value={value}>
      {children}
    </OrganizationContext.Provider>
  )
}
