"use client"

import { useState, useEffect } from "react"
import { useSession } from "next-auth/react"
import { useRouter } from "next/navigation"
import api, { setAuthToken } from "@/utils/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Skeleton } from "@/components/ui/skeleton"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Building2,
  Plus,
  Edit,
  Trash2,
  Users,
  Activity,
  DollarSign,
  BarChart,
  Search,
  AlertCircle,
  Mail,
  CheckCircle,
  XCircle,
  Calendar,
} from "lucide-react"
import { Organization, OrganizationWithStats, OrganizationCreate, OrganizationUpdate } from "@/types/organization"

export default function OrganizationsPage() {
  const router = useRouter()
  const { data: session, status } = useSession({
    required: true,
    onUnauthenticated() {
      router.push('/login')
    }
  })

  const [organizations, setOrganizations] = useState<OrganizationWithStats[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [activeTab, setActiveTab] = useState("all")

  // Create organization state
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [newOrg, setNewOrg] = useState<OrganizationCreate>({
    name: "",
    description: "",
    external_id: "",
    status: "active",
    billing_email: "",
    contact_name: "",
    contact_phone: "",
    timezone: "UTC",
    settings: {}
  })

  // Edit organization state
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [editingOrg, setEditingOrg] = useState<OrganizationWithStats | null>(null)
  const [editData, setEditData] = useState<OrganizationUpdate>({})

  // Stats modal state
  const [statsDialogOpen, setStatsDialogOpen] = useState(false)
  const [selectedOrgStats, setSelectedOrgStats] = useState<OrganizationWithStats | null>(null)

  const [isCreating, setIsCreating] = useState(false)
  const [isUpdating, setIsUpdating] = useState(false)
  const [isDeleting, setIsDeleting] = useState<number | null>(null)

  // Fetch organizations
  const fetchOrganizations = async () => {
    setLoading(true)
    setError(null)
    try {
      // First get the basic organization list
      const orgResponse = await api.get<Organization[]>("/organizations")
      
      // Then get stats for each organization (if user has permissions)
      const orgsWithStats = await Promise.all(
        orgResponse.data.map(async (org) => {
          try {
            const statsResponse = await api.get<OrganizationWithStats>(`/organizations/${org.id}/stats`)
            return statsResponse.data
          } catch (error) {
            // If we can't get stats, return the basic org with default stats
            return {
              ...org,
              agent_count: 0,
              active_agent_count: 0,
              monthly_cost: 0,
              monthly_revenue: 0
            } as OrganizationWithStats
          }
        })
      )
      
      setOrganizations(orgsWithStats)
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message || "Failed to load organizations")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (status !== 'authenticated') return
    const token = session.user.accessToken ?? ""
    setAuthToken(token)
    fetchOrganizations()
  }, [status, session])

  // Create organization
  const handleCreate = async () => {
    if (!newOrg.name.trim()) return
    
    setIsCreating(true)
    try {
      await api.post("/organizations", newOrg)
      setNewOrg({
        name: "",
        description: "",
        external_id: "",
        status: "active",
        billing_email: "",
        contact_name: "",
        contact_phone: "",
        timezone: "UTC",
        settings: {}
      })
      setCreateDialogOpen(false)
      fetchOrganizations()
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message || "Failed to create organization")
    } finally {
      setIsCreating(false)
    }
  }

  // Update organization
  const handleUpdate = async () => {
    if (!editingOrg) return
    
    setIsUpdating(true)
    try {
      await api.put(`/organizations/${editingOrg.id}`, editData)
      setEditDialogOpen(false)
      setEditingOrg(null)
      setEditData({})
      fetchOrganizations()
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message || "Failed to update organization")
    } finally {
      setIsUpdating(false)
    }
  }

  // Delete organization
  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this organization? This action cannot be undone.")) return
    
    setIsDeleting(id)
    try {
      await api.delete(`/organizations/${id}`)
      fetchOrganizations()
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message || "Failed to delete organization")
    } finally {
      setIsDeleting(null)
    }
  }

  // Start editing
  const startEdit = (org: OrganizationWithStats) => {
    setEditingOrg(org)
    setEditData({
      name: org.name,
      description: org.description || "",
      external_id: org.external_id || "",
      status: org.status,
      billing_email: org.billing_email || "",
      contact_name: org.contact_name || "",
      contact_phone: org.contact_phone || "",
      timezone: org.timezone,
      settings: org.settings
    })
    setEditDialogOpen(true)
  }

  // Show stats
  const showStats = (org: OrganizationWithStats) => {
    setSelectedOrgStats(org)
    setStatsDialogOpen(true)
  }

  // Filter organizations
  const filteredOrganizations = organizations.filter((org) => {
    const matchesTab = 
      activeTab === "all" ||
      (activeTab === "active" && org.status === "active") ||
      (activeTab === "inactive" && org.status !== "active")
    
    const matchesSearch = 
      searchQuery === "" ||
      org.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (org.description && org.description.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (org.contact_name && org.contact_name.toLowerCase().includes(searchQuery.toLowerCase()))
    
    return matchesTab && matchesSearch
  })

  // Calculate totals
  const totalStats = organizations.reduce((acc, org) => ({
    organizations: acc.organizations + 1,
    agents: acc.agents + org.agent_count,
    activeAgents: acc.activeAgents + org.active_agent_count,
    monthlyCost: acc.monthlyCost + org.monthly_cost,
    monthlyRevenue: acc.monthlyRevenue + org.monthly_revenue
  }), { organizations: 0, agents: 0, activeAgents: 0, monthlyCost: 0, monthlyRevenue: 0 })

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between md:items-center gap-12 bg-gradient-to-r from-background to-muted/20 p-6 rounded-xl border border-border/8 shadow-sm ring-1 ring-border/5 hover:ring-border/10 transition-all duration-300">
        <div className="flex items-center gap-3">
          <div className="rounded-full p-2">
            <Building2 className="h-6 w-6 text-gold" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">Organizations</h1>
            <p className="text-muted-foreground">Manage organizations and their settings</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button className="bg-gold hover:bg-gold-20 text-white">
                <Plus className="h-4 w-4 mr-2" />
                Add Organization
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>Create New Organization</DialogTitle>
                <DialogDescription>
                  Add a new organization to the system.
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="name" className="text-right">
                    Name *
                  </Label>
                  <Input
                    id="name"
                    value={newOrg.name}
                    onChange={(e) => setNewOrg({ ...newOrg, name: e.target.value })}
                    className="col-span-3"
                    placeholder="Organization name"
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="description" className="text-right">
                    Description
                  </Label>
                  <Input
                    id="description"
                    value={newOrg.description}
                    onChange={(e) => setNewOrg({ ...newOrg, description: e.target.value })}
                    className="col-span-3"
                    placeholder="Optional description"
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="external_id" className="text-right">
                    External ID
                  </Label>
                  <Input
                    id="external_id"
                    value={newOrg.external_id}
                    onChange={(e) => setNewOrg({ ...newOrg, external_id: e.target.value })}
                    className="col-span-3"
                    placeholder="External system ID"
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="billing_email" className="text-right">
                    Billing Email
                  </Label>
                  <Input
                    id="billing_email"
                    type="email"
                    value={newOrg.billing_email}
                    onChange={(e) => setNewOrg({ ...newOrg, billing_email: e.target.value })}
                    className="col-span-3"
                    placeholder="billing@example.com"
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="contact_name" className="text-right">
                    Contact Name
                  </Label>
                  <Input
                    id="contact_name"
                    value={newOrg.contact_name}
                    onChange={(e) => setNewOrg({ ...newOrg, contact_name: e.target.value })}
                    className="col-span-3"
                    placeholder="Primary contact"
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="contact_phone" className="text-right">
                    Contact Phone
                  </Label>
                  <Input
                    id="contact_phone"
                    value={newOrg.contact_phone}
                    onChange={(e) => setNewOrg({ ...newOrg, contact_phone: e.target.value })}
                    className="col-span-3"
                    placeholder="+1 (555) 123-4567"
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="timezone" className="text-right">
                    Timezone
                  </Label>
                  <Select value={newOrg.timezone} onValueChange={(value) => setNewOrg({ ...newOrg, timezone: value })}>
                    <SelectTrigger className="col-span-3">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="UTC">UTC</SelectItem>
                      <SelectItem value="America/New_York">Eastern Time</SelectItem>
                      <SelectItem value="America/Chicago">Central Time</SelectItem>
                      <SelectItem value="America/Denver">Mountain Time</SelectItem>
                      <SelectItem value="America/Los_Angeles">Pacific Time</SelectItem>
                      <SelectItem value="Europe/London">London</SelectItem>
                      <SelectItem value="Europe/Paris">Paris</SelectItem>
                      <SelectItem value="Asia/Tokyo">Tokyo</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreate} disabled={isCreating || !newOrg.name.trim()}>
                  {isCreating ? "Creating..." : "Create Organization"}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
          <AlertCircle className="h-4 w-4" />
          <span>{error}</span>
          <Button variant="ghost" size="sm" onClick={() => setError(null)} className="ml-auto">
            ×
          </Button>
        </div>
      )}

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Organizations</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalStats.organizations}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Agents</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalStats.agents}</div>
            <p className="text-xs text-muted-foreground">
              {totalStats.activeAgents} active
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Monthly Costs</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(totalStats.monthlyCost)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Monthly Revenue</CardTitle>
            <BarChart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(totalStats.monthlyRevenue)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Margin</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(totalStats.monthlyRevenue - totalStats.monthlyCost)}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="all">All Organizations</TabsTrigger>
            <TabsTrigger value="active">Active</TabsTrigger>
            <TabsTrigger value="inactive">Inactive</TabsTrigger>
          </TabsList>
        </Tabs>
        
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
          <Input
            placeholder="Search organizations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 w-64"
          />
        </div>
      </div>

      {/* Organizations List */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-3 w-1/2" />
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Skeleton className="h-3 w-full" />
                  <Skeleton className="h-3 w-2/3" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredOrganizations.map((org) => (
            <Card key={org.id} className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg font-semibold">{org.name}</CardTitle>
                    <CardDescription className="text-sm text-muted-foreground mt-1">
                      {org.description || "No description"}
                    </CardDescription>
                  </div>
                  <Badge variant={org.status === 'active' ? 'default' : 'secondary'} className="ml-2">
                    {org.status === 'active' ? (
                      <CheckCircle className="h-3 w-3 mr-1" />
                    ) : (
                      <XCircle className="h-3 w-3 mr-1" />
                    )}
                    {org.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="flex items-center gap-1 text-muted-foreground">
                      <Users className="h-3 w-3" />
                      <span>Agents</span>
                    </div>
                    <div className="font-medium">{org.agent_count} ({org.active_agent_count} active)</div>
                  </div>
                  <div>
                    <div className="flex items-center gap-1 text-muted-foreground">
                      <DollarSign className="h-3 w-3" />
                      <span>Monthly Revenue</span>
                    </div>
                    <div className="font-medium">{formatCurrency(org.monthly_revenue)}</div>
                  </div>
                </div>

                {org.contact_name && (
                  <div className="text-sm">
                    <div className="flex items-center gap-1 text-muted-foreground">
                      <Users className="h-3 w-3" />
                      <span>Contact</span>
                    </div>
                    <div className="font-medium">{org.contact_name}</div>
                  </div>
                )}

                {org.billing_email && (
                  <div className="text-sm">
                    <div className="flex items-center gap-1 text-muted-foreground">
                      <Mail className="h-3 w-3" />
                      <span>Billing Email</span>
                    </div>
                    <div className="font-medium">{org.billing_email}</div>
                  </div>
                )}

                <div className="text-sm">
                  <div className="flex items-center gap-1 text-muted-foreground">
                    <Calendar className="h-3 w-3" />
                    <span>Created</span>
                  </div>
                  <div className="font-medium">{formatDate(org.created_at)}</div>
                </div>

                <div className="flex items-center gap-2 pt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => showStats(org)}
                    className="flex-1"
                  >
                    <BarChart className="h-3 w-3 mr-1" />
                    Stats
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => startEdit(org)}
                  >
                    <Edit className="h-3 w-3" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDelete(org.id)}
                    disabled={isDeleting === org.id}
                    className="text-red-600 hover:text-red-700"
                  >
                    {isDeleting === org.id ? (
                      <div className="h-3 w-3 animate-spin rounded-full border-2 border-red-600 border-t-transparent" />
                    ) : (
                      <Trash2 className="h-3 w-3" />
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {filteredOrganizations.length === 0 && !loading && (
        <div className="text-center py-12">
          <Building2 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">No organizations found</h3>
          <p className="text-muted-foreground mb-4">
            {searchQuery ? "Try adjusting your search criteria." : "Get started by creating your first organization."}
          </p>
          {!searchQuery && (
            <Button className="bg-gold" onClick={() => setCreateDialogOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create Organization
            </Button>
          )}
        </div>
      )}

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Edit Organization</DialogTitle>
            <DialogDescription>
              Update the organization information below.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="edit-name" className="text-right">
                Name *
              </Label>
              <Input
                id="edit-name"
                value={editData.name || ""}
                onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                className="col-span-3"
                placeholder="Organization name"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="edit-description" className="text-right">
                Description
              </Label>
              <Input
                id="edit-description"
                value={editData.description || ""}
                onChange={(e) => setEditData({ ...editData, description: e.target.value })}
                className="col-span-3"
                placeholder="Optional description"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="edit-external_id" className="text-right">
                External ID
              </Label>
              <Input
                id="edit-external_id"
                value={editData.external_id || ""}
                onChange={(e) => setEditData({ ...editData, external_id: e.target.value })}
                className="col-span-3"
                placeholder="External system ID"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="edit-status" className="text-right">
                Status
              </Label>
              <Select value={editData.status} onValueChange={(value) => setEditData({ ...editData, status: value })}>
                <SelectTrigger className="col-span-3">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="inactive">Inactive</SelectItem>
                  <SelectItem value="suspended">Suspended</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="edit-billing_email" className="text-right">
                Billing Email
              </Label>
              <Input
                id="edit-billing_email"
                type="email"
                value={editData.billing_email || ""}
                onChange={(e) => setEditData({ ...editData, billing_email: e.target.value })}
                className="col-span-3"
                placeholder="billing@example.com"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="edit-contact_name" className="text-right">
                Contact Name
              </Label>
              <Input
                id="edit-contact_name"
                value={editData.contact_name || ""}
                onChange={(e) => setEditData({ ...editData, contact_name: e.target.value })}
                className="col-span-3"
                placeholder="Primary contact"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="edit-contact_phone" className="text-right">
                Contact Phone
              </Label>
              <Input
                id="edit-contact_phone"
                value={editData.contact_phone || ""}
                onChange={(e) => setEditData({ ...editData, contact_phone: e.target.value })}
                className="col-span-3"
                placeholder="+1 (555) 123-4567"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="edit-timezone" className="text-right">
                Timezone
              </Label>
              <Select value={editData.timezone} onValueChange={(value) => setEditData({ ...editData, timezone: value })}>
                <SelectTrigger className="col-span-3">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="UTC">UTC</SelectItem>
                  <SelectItem value="America/New_York">Eastern Time</SelectItem>
                  <SelectItem value="America/Chicago">Central Time</SelectItem>
                  <SelectItem value="America/Denver">Mountain Time</SelectItem>
                  <SelectItem value="America/Los_Angeles">Pacific Time</SelectItem>
                  <SelectItem value="Europe/London">London</SelectItem>
                  <SelectItem value="Europe/Paris">Paris</SelectItem>
                  <SelectItem value="Asia/Tokyo">Tokyo</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdate} disabled={isUpdating || !editData.name?.trim()}>
              {isUpdating ? "Updating..." : "Update Organization"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Stats Dialog */}
      <Dialog open={statsDialogOpen} onOpenChange={setStatsDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>{selectedOrgStats?.name} - Statistics</DialogTitle>
            <DialogDescription>
              Detailed statistics and information for this organization.
            </DialogDescription>
          </DialogHeader>
          {selectedOrgStats && (
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Total Agents</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{selectedOrgStats.agent_count}</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Active Agents</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{selectedOrgStats.active_agent_count}</div>
                  </CardContent>
                </Card>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Monthly Cost</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{formatCurrency(selectedOrgStats.monthly_cost)}</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Monthly Revenue</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{formatCurrency(selectedOrgStats.monthly_revenue)}</div>
                  </CardContent>
                </Card>
              </div>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">Monthly Margin</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {formatCurrency(selectedOrgStats.monthly_revenue - selectedOrgStats.monthly_cost)}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Revenue - Cost
                  </p>
                </CardContent>
              </Card>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Status:</span>
                  <Badge variant={selectedOrgStats.status === 'active' ? 'default' : 'secondary'}>
                    {selectedOrgStats.status}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Timezone:</span>
                  <span>{selectedOrgStats.timezone}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Created:</span>
                  <span>{formatDate(selectedOrgStats.created_at)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Last Updated:</span>
                  <span>{formatDate(selectedOrgStats.updated_at)}</span>
                </div>
                {selectedOrgStats.external_id && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">External ID:</span>
                    <span>{selectedOrgStats.external_id}</span>
                  </div>
                )}
              </div>
            </div>
          )}
          <DialogFooter>
            <Button onClick={() => setStatsDialogOpen(false)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
