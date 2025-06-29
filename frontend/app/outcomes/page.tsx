"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useSession } from "next-auth/react"
import api, { setAuthToken } from "../../utils/api"
import toast from "react-hot-toast"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  TrendingUp,
  DollarSign,
  CheckCircle,
  Clock,
  XCircle,
  Eye,
  AlertCircle,
  Target,
  Award,
  BarChart3,
  FileText,
  Plus,
  Search,
  Calendar,
} from "lucide-react"

export default function OutcomeTrackingPage() {
  const router = useRouter()
  const { data: session, status } = useSession({
    required: true,
    onUnauthenticated() {
      router.push('/login')
    }
  })

  const [outcomes, setOutcomes] = useState<any[]>([])
  const [agents, setAgents] = useState<any[]>([])
  const [statistics, setStatistics] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedAgent, setSelectedAgent] = useState<string>("all")
  const [verificationStatus, setVerificationStatus] = useState<string>("all")
  const [billingStatus, setBillingStatus] = useState<string>("all")
  const [searchQuery, setSearchQuery] = useState("")
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [verifyingOutcomes, setVerifyingOutcomes] = useState<Set<number>>(new Set())

  // New outcome form state
  const [newOutcome, setNewOutcome] = useState({
    agent_id: "",
    outcome_value: "",
    outcome_currency: "USD",
    outcome_data: "",
    verification_required: true
  })

  useEffect(() => {
    if (status === 'authenticated') {
      const token = session.user.accessToken ?? ""
      setAuthToken(token)
      fetchData()
    }
  }, [status, session, selectedAgent, verificationStatus, billingStatus])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [outcomesRes, agentsRes, statsRes] = await Promise.all([
        api.get("/outcomes", {
          params: {
            agent_id: selectedAgent !== "all" ? selectedAgent : undefined,
            verification_status: verificationStatus !== "all" ? verificationStatus : undefined,
            billing_status: billingStatus !== "all" ? billingStatus : undefined,
            limit: 100
          }
        }),
        api.get("/agents"),
        api.get("/outcomes/statistics", {
          params: {
            agent_id: selectedAgent !== "all" ? selectedAgent : undefined
          }
        }).catch(() => ({ data: null })) // Handle if endpoint doesn't exist yet
      ])

      setOutcomes(outcomesRes.data)
      setAgents(agentsRes.data)
      setStatistics(statsRes.data)
    } catch (err: any) {
      console.error("Error fetching outcome data:", err)
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateOutcome = async () => {
    try {
      const payload = {
        agent_id: parseInt(newOutcome.agent_id),
        outcome_value: parseFloat(newOutcome.outcome_value),
        outcome_currency: newOutcome.outcome_currency,
        outcome_data: newOutcome.outcome_data ? JSON.parse(newOutcome.outcome_data) : null,
        verification_required: newOutcome.verification_required
      }

      const res = await api.post("/outcomes/record", payload)
      setOutcomes(prev => [res.data, ...prev])
      setShowCreateForm(false)
      setNewOutcome({
        agent_id: "",
        outcome_value: "",
        outcome_currency: "USD",
        outcome_data: "",
        verification_required: true
      })
      toast.success("Outcome recorded successfully")
      
      // Refresh statistics
      fetchData()
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message
      toast.error(`Failed to record outcome: ${msg}`)
    }
  }

  const handleVerifyOutcome = async (outcomeId: number, status: string, notes?: string) => {
    try {
      setVerifyingOutcomes(prev => new Set(prev).add(outcomeId))
      
      const res = await api.post(`/outcomes/${outcomeId}/verify`, null, {
        params: {
          verified_by: session?.user?.email || "system",
          verification_status: status,
          verification_notes: notes
        }
      })

      setOutcomes(prev => 
        prev.map(outcome => 
          outcome.id === outcomeId ? res.data : outcome
        )
      )

      toast.success(`Outcome ${status} successfully`)
      fetchData() // Refresh to update statistics
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message
      toast.error(`Failed to ${status} outcome: ${msg}`)
    } finally {
      setVerifyingOutcomes(prev => {
        const newSet = new Set(prev)
        newSet.delete(outcomeId)
        return newSet
      })
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "verified":
        return <Badge className="bg-green-100 text-green-800 border-green-200"><CheckCircle className="h-3 w-3 mr-1" />Verified</Badge>
      case "pending":
        return <Badge className="bg-yellow-100 text-yellow-800 border-yellow-200"><Clock className="h-3 w-3 mr-1" />Pending</Badge>
      case "rejected":
        return <Badge className="bg-red-100 text-red-800 border-red-200"><XCircle className="h-3 w-3 mr-1" />Rejected</Badge>
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }

  const getBillingStatusBadge = (status: string) => {
    switch (status) {
      case "ready":
        return <Badge className="bg-blue-100 text-blue-800 border-blue-200">Ready</Badge>
      case "billed":
        return <Badge className="bg-purple-100 text-purple-800 border-purple-200">Billed</Badge>
      case "pending":
        return <Badge className="bg-gray-100 text-gray-800 border-gray-200">Pending</Badge>
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }

  const formatCurrency = (amount: number, currency = "USD") => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(amount)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const filteredOutcomes = outcomes.filter(outcome => {
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      const agentName = agents.find(a => a.id === outcome.agent_id)?.name || ""
      return (
        agentName.toLowerCase().includes(query) ||
        outcome.outcome_value.toString().includes(query) ||
        outcome.outcome_currency.toLowerCase().includes(query)
      )
    }
    return true
  })

  if (loading) {
    return (
      <div className="container mx-auto py-8 space-y-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto py-8">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>Error loading outcome data: {error}</AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Outcome Tracking</h1>
          <p className="text-muted-foreground">Monitor and verify outcome-based billing metrics</p>
        </div>
        <Button onClick={() => setShowCreateForm(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Record Outcome
        </Button>
      </div>

      {/* Statistics Cards */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Outcomes</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.total_outcomes}</div>
              <p className="text-xs text-muted-foreground">
                Recorded outcomes
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Value</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(statistics.total_value)}</div>
              <p className="text-xs text-muted-foreground">
                Combined outcome value
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Fees</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(statistics.total_fees)}</div>
              <p className="text-xs text-muted-foreground">
                Calculated billing fees
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
              <Award className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{(statistics.success_rate * 100).toFixed(1)}%</div>
              <p className="text-xs text-muted-foreground">
                Verified outcomes
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label>Agent</Label>
              <Select value={selectedAgent} onValueChange={setSelectedAgent}>
                <SelectTrigger>
                  <SelectValue placeholder="Select agent" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Agents</SelectItem>
                  {agents.map((agent) => (
                    <SelectItem key={agent.id} value={agent.id.toString()}>
                      {agent.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Verification Status</Label>
              <Select value={verificationStatus} onValueChange={setVerificationStatus}>
                <SelectTrigger>
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="verified">Verified</SelectItem>
                  <SelectItem value="rejected">Rejected</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Billing Status</Label>
              <Select value={billingStatus} onValueChange={setBillingStatus}>
                <SelectTrigger>
                  <SelectValue placeholder="Select billing status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Billing Statuses</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="ready">Ready</SelectItem>
                  <SelectItem value="billed">Billed</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Search</Label>
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search outcomes..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Outcomes Table */}
      <Card>
        <CardHeader>
          <CardTitle>Outcomes</CardTitle>
          <CardDescription>
            {filteredOutcomes.length} outcome{filteredOutcomes.length !== 1 ? 's' : ''} found
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Agent</TableHead>
                  <TableHead>Value</TableHead>
                  <TableHead>Calculated Fee</TableHead>
                  <TableHead>Verification</TableHead>
                  <TableHead>Billing</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredOutcomes.map((outcome) => {
                  const agent = agents.find(a => a.id === outcome.agent_id)
                  return (
                    <TableRow key={outcome.id}>
                      <TableCell>
                        <div>
                          <div className="font-medium">{agent?.name || `Agent ${outcome.agent_id}`}</div>
                          <div className="text-sm text-muted-foreground">ID: {outcome.agent_id}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <div className="font-medium">
                            {formatCurrency(outcome.outcome_value, outcome.outcome_currency)}
                          </div>
                          {outcome.tier_applied && (
                            <div className="text-sm text-muted-foreground">
                              Tier: {outcome.tier_applied}
                            </div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <div className="font-medium">
                            {formatCurrency(outcome.calculated_fee, outcome.outcome_currency)}
                          </div>
                          {outcome.bonus_applied > 0 && (
                            <div className="text-sm text-green-600">
                              +{formatCurrency(outcome.bonus_applied)} bonus
                            </div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        {getStatusBadge(outcome.verification_status)}
                        {outcome.verification_notes && (
                          <div className="text-xs text-muted-foreground mt-1">
                            {outcome.verification_notes}
                          </div>
                        )}
                      </TableCell>
                      <TableCell>
                        {getBillingStatusBadge(outcome.billing_status)}
                      </TableCell>
                      <TableCell>
                        <div className="text-sm">
                          <div>{formatDate(outcome.attribution_end_date)}</div>
                          {outcome.verified_at && (
                            <div className="text-muted-foreground">
                              Verified: {formatDate(outcome.verified_at)}
                            </div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          {outcome.verification_status === "pending" && (
                            <>
                              <Button
                                size="sm"
                                variant="outline"
                                className="text-green-600 border-green-200 hover:bg-green-50"
                                onClick={() => handleVerifyOutcome(outcome.id, "verified")}
                                title="Verify outcome"
                                disabled={verifyingOutcomes.has(outcome.id)}
                              >
                                <CheckCircle className="h-3 w-3 mr-1" />
                                {verifyingOutcomes.has(outcome.id) ? "Verifying..." : "Verify"}
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                className="text-red-600 border-red-200 hover:bg-red-50"
                                onClick={() => handleVerifyOutcome(outcome.id, "rejected", "Manual rejection")}
                                title="Reject outcome"
                                disabled={verifyingOutcomes.has(outcome.id)}
                              >
                                <XCircle className="h-3 w-3 mr-1" />
                                {verifyingOutcomes.has(outcome.id) ? "Rejecting..." : "Reject"}
                              </Button>
                            </>
                          )}
                          <Button 
                            size="sm" 
                            variant="ghost"
                            title="View details"
                            onClick={() => {
                              // Future: implement outcome details modal
                              toast.success("Outcome details view coming soon!")
                            }}
                          >
                            <Eye className="h-3 w-3" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </div>

          {filteredOutcomes.length === 0 && (
            <div className="text-center py-8">
              <Target className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">No outcomes found</h3>
              <p className="text-muted-foreground mb-4">
                {searchQuery || selectedAgent !== "all" || verificationStatus !== "all" || billingStatus !== "all"
                  ? "Try adjusting your filters or search query"
                  : "Get started by recording your first outcome"}
              </p>
              {!searchQuery && selectedAgent === "all" && verificationStatus === "all" && billingStatus === "all" && (
                <Button onClick={() => setShowCreateForm(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Record First Outcome
                </Button>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create Outcome Form Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md m-4">
            <CardHeader>
              <CardTitle>Record New Outcome</CardTitle>
              <CardDescription>
                Record a new outcome for billing calculation
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="agent">Agent</Label>
                <Select value={newOutcome.agent_id} onValueChange={(value) => setNewOutcome(prev => ({ ...prev, agent_id: value }))}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select agent" />
                  </SelectTrigger>
                  <SelectContent>
                    {agents.map((agent) => (
                      <SelectItem key={agent.id} value={agent.id.toString()}>
                        {agent.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="outcome_value">Outcome Value</Label>
                <Input
                  id="outcome_value"
                  type="number"
                  step="0.01"
                  placeholder="e.g., 5000.00"
                  value={newOutcome.outcome_value}
                  onChange={(e) => setNewOutcome(prev => ({ ...prev, outcome_value: e.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="outcome_currency">Currency</Label>
                <Select value={newOutcome.outcome_currency} onValueChange={(value) => setNewOutcome(prev => ({ ...prev, outcome_currency: value }))}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="USD">USD ($)</SelectItem>
                    <SelectItem value="EUR">EUR (€)</SelectItem>
                    <SelectItem value="GBP">GBP (£)</SelectItem>
                    <SelectItem value="CAD">CAD (C$)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="outcome_data">Additional Data (Optional JSON)</Label>
                <Input
                  id="outcome_data"
                  placeholder='{"source": "campaign_a", "campaign_id": 123}'
                  value={newOutcome.outcome_data}
                  onChange={(e) => setNewOutcome(prev => ({ ...prev, outcome_data: e.target.value }))}
                />
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="verification_required"
                  checked={newOutcome.verification_required}
                  onChange={(e) => setNewOutcome(prev => ({ ...prev, verification_required: e.target.checked }))}
                />
                <Label htmlFor="verification_required">Requires verification</Label>
              </div>
            </CardContent>
            <CardContent className="flex justify-between pt-0">
              <Button variant="outline" onClick={() => setShowCreateForm(false)}>
                Cancel
              </Button>
              <Button 
                onClick={handleCreateOutcome}
                disabled={!newOutcome.agent_id || !newOutcome.outcome_value}
              >
                <Plus className="h-4 w-4 mr-2" />
                Record Outcome
              </Button>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
