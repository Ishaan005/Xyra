"use client"

import { useState, useEffect, Fragment } from "react"
import { useSession } from "next-auth/react"
import { useRouter } from "next/navigation"
import api, { setAuthToken } from "@/utils/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Zap,
  Plus,
  Edit,
  Trash2,
  CheckCircle,
  XCircle,
  Activity,
  DollarSign,
  BarChart,
  Percent,
  Search,
  ArrowUpDown,
  AlertCircle,
} from "lucide-react"

interface Agent {
  id: number
  name: string
  description?: string
  config?: Record<string, any>
  is_active: boolean
  billing_model_id?: number
  activity_count?: number
  total_cost?: number
  total_outcomes_value?: number
  margin?: number
}

interface AgentStats {
  activity_count: number
  total_cost: number
  total_outcomes_value: number
  margin: number
}

export default function AgentsPage() {
  const router = useRouter()
  const { data: session, status } = useSession({
    required: true,
    onUnauthenticated() {
      router.push('/login')
    }
  })
  const [agents, setAgents] = useState<Agent[]>([])
  const [agentStats, setAgentStats] = useState<Record<number, AgentStats>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState("all")
  const [searchQuery, setSearchQuery] = useState("")

  const [newAgent, setNewAgent] = useState({
    name: "",
    description: "",
    billing_model_id: "",
  })
  const [billingModels, setBillingModels] = useState<{ id: number; name: string }[]>([])

  const [editAgentId, setEditAgentId] = useState<number | null>(null)
  const [editData, setEditData] = useState({
    name: "",
    description: "",
    billing_model_id: "",
    is_active: true,
  })

  // fetch list
  const fetchAgents = async () => {
    setLoading(true)
    try {
      const res = await api.get<Agent[]>("/agents", {
        params: { org_id: 1 },
      })
      setAgents(res.data)
    } catch (e: any) {
      setError(e.message || "Failed to load agents")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (status !== 'authenticated') return
    // authenticated: set token and fetch data
    const token = session.user.accessToken ?? ""
    setAuthToken(token)
    fetchAgents()
    api.get<{ id: number; name: string }[]>('/billing-models', { params: { org_id: 1 } })
      .then(res => setBillingModels(res.data))
      .catch(() => {})
  }, [status, session, router])

  // fetch stats for each agent when list changes
  useEffect(() => {
    if (!agents.length) return
    const loadStats = async () => {
      try {
        const statsArr = await Promise.all(
          agents.map((agent) =>
            api.get<AgentStats>(`/agents/${agent.id}/stats`).then((res) => ({ id: agent.id, ...res.data })),
          ),
        )
        const statsMap: Record<number, AgentStats> = {}
        statsArr.forEach((s) => {
          statsMap[s.id] = {
            activity_count: s.activity_count,
            total_cost: s.total_cost,
            total_outcomes_value: s.total_outcomes_value,
            margin: s.margin,
          }
        })
        setAgentStats(statsMap)
      } catch {
        // ignore stats errors
      }
    }
    loadStats()
  }, [agents])

  // create new
  const handleCreate = async () => {
    if (!newAgent.name) return
    try {
      await api.post("/agents", {
        name: newAgent.name,
        description: newAgent.description,
        billing_model_id: newAgent.billing_model_id ? Number(newAgent.billing_model_id) : undefined,
        organization_id: 1,
      })
      setNewAgent({ name: "", description: "", billing_model_id: "" })
      fetchAgents()
    } catch (e: any) {
      setError(e.message || "Failed to create agent")
    }
  }

  // update existing
  const handleSave = async (id: number) => {
    try {
      await api.put(`/agents/${id}`, {
        ...editData,
        billing_model_id: editData.billing_model_id ? Number(editData.billing_model_id) : undefined,
      })
      setEditAgentId(null)
      fetchAgents()
    } catch (e: any) {
      setError(e.message || "Failed to update agent")
    }
  }

  // delete
  const handleDelete = async (id: number) => {
    if (!confirm("Delete this agent?")) return
    try {
      await api.delete(`/agents/${id}`)
      fetchAgents()
    } catch (e: any) {
      setError(e.message || "Failed to delete agent")
    }
  }

  // Filter agents based on active tab and search query
  const filteredAgents = agents.filter((agent) => {
    const matchesTab =
      activeTab === "all" ||
      (activeTab === "active" && agent.is_active) ||
      (activeTab === "inactive" && !agent.is_active)
    const matchesSearch =
      searchQuery === "" ||
      agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (agent.description && agent.description.toLowerCase().includes(searchQuery.toLowerCase()))
    return matchesTab && matchesSearch
  })

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between md:items-center gap-12 bg-gradient-to-r from-background to-muted/20 p-6 rounded-xl border border-border/50 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="rounded-full bg-gold/10 p-2">
            <Zap className="h-6 w-6 text-gold" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">Agents</h1>
            <p className="text-muted-foreground">Manage your AI agents and their billing models</p>
          </div>
        </div>
        <div className="flex items-center gap-3 md:w-auto">
          <div className="relative md:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search agents..."
              className="pl-9"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <Button onClick={() => window.location.reload()} variant="outline" size="icon" className="flex-shrink-0">
            <ArrowUpDown className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {error && (
        <div className="bg-destructive/10 text-destructive rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
          <div>
            <h3 className="font-medium">Error</h3>
            <p>{error}</p>
          </div>
        </div>
      )}

      {/* Create New Agent Card */}
      <Card className="border-border/50 shadow-gray">
        <CardHeader className="bg-gradient-to-r from-gold/5 to-transparent">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Plus className="h-4 w-4 text-gold" />
              <CardTitle>Create New Agent</CardTitle>
            </div>
            <Badge variant="outline" className="bg-gold/10 text-gold-dark border-gold/20">
              New
            </Badge>
          </div>
          <CardDescription>Configure a new AI agent and assign a billing model</CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <label htmlFor="agent-name" className="text-sm font-medium">
                Agent Name
              </label>
              <Input
                id="agent-name"
                placeholder="Enter agent name"
                value={newAgent.name}
                onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="agent-description" className="text-sm font-medium">
                Description
              </label>
              <Input
                id="agent-description"
                placeholder="Enter description"
                value={newAgent.description}
                onChange={(e) => setNewAgent({ ...newAgent, description: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="billing-model" className="text-sm font-medium">
                Billing Model
              </label>
              <select
                id="billing-model"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                value={newAgent.billing_model_id}
                onChange={(e) => {
                  const val = e.target.value
                  if (val === "new") router.push("/pricing")
                  else setNewAgent({ ...newAgent, billing_model_id: val })
                }}
              >
                <option value="">Select billing model</option>
                {billingModels.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.name}
                  </option>
                ))}
                <option value="new">+ Create new model</option>
              </select>
            </div>
          </div>
          <Button className="mt-6" onClick={handleCreate}>
            <Plus className="h-4 w-4 mr-2" />
            Create Agent
          </Button>
        </CardContent>
      </Card>

      {/* Agents List */}
      <Card className="border-border/50 shadow-sm overflow-hidden">
        <CardHeader className="bg-gradient-to-r from-purple/5 to-transparent">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <CardTitle>Agents</CardTitle>
              <CardDescription>
                {filteredAgents.length} agent{filteredAgents.length !== 1 ? "s" : ""} available
              </CardDescription>
            </div>
            <Tabs defaultValue="all" value={activeTab} onValueChange={setActiveTab} className="w-full sm:w-auto">
              <TabsList>
                <TabsTrigger value="all">All</TabsTrigger>
                <TabsTrigger value="active">Active</TabsTrigger>
                <TabsTrigger value="inactive">Inactive</TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {loading ? (
            <div className="p-6 space-y-4">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="flex items-center gap-4">
                  <Skeleton className="h-12 w-12 rounded-full" />
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-[250px]" />
                    <Skeleton className="h-4 w-[200px]" />
                  </div>
                </div>
              ))}
            </div>
          ) : filteredAgents.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="rounded-full bg-muted p-4 mb-4">
                <Zap className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="text-xl font-bold mb-2">No agents found</h3>
              <p className="text-muted-foreground mb-4">
                {searchQuery ? "Try a different search term" : "Create your first agent to get started"}
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-muted/30">
                    <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      Agent
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      <div className="flex items-center justify-end">
                        <Activity className="h-3.5 w-3.5 mr-1" />
                        Activity
                      </div>
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      <div className="flex items-center justify-end">
                        <DollarSign className="h-3.5 w-3.5 mr-1" />
                        Cost
                      </div>
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      <div className="flex items-center justify-end">
                        <BarChart className="h-3.5 w-3.5 mr-1" />
                        Outcomes
                      </div>
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      <div className="flex items-center justify-end">
                        <Percent className="h-3.5 w-3.5 mr-1" />
                        Margin
                      </div>
                    </th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-muted-foreground uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/50">
                  {filteredAgents.map((agent) => {
                    const stats = agentStats[agent.id]
                    return (
                      <Fragment key={agent.id}>
                        <tr className="hover:bg-muted/20 transition-colors">
                          <td className="px-4 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div className="h-10 w-10 rounded-full bg-gradient-to-br from-purple-20 to-blue-20 flex items-center justify-center text-sm font-medium">
                                {agent.name.charAt(0).toUpperCase()}
                              </div>
                              <div className="ml-3">
                                <div className="text-sm font-medium">{agent.name}</div>
                                <div className="text-xs text-muted-foreground">
                                  {agent.description || "No description"}
                                </div>
                              </div>
                            </div>
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap">
                            {agent.is_active ? (
                              <Badge className="bg-success/20 text-success hover:bg-success/30 border-0">
                                <CheckCircle className="h-3.5 w-3.5 mr-1" />
                                Active
                              </Badge>
                            ) : (
                              <Badge className="bg-muted text-muted-foreground hover:bg-muted/80 border-0">
                                <XCircle className="h-3.5 w-3.5 mr-1" />
                                Inactive
                              </Badge>
                            )}
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-sm text-right">
                            {stats ? stats.activity_count.toLocaleString() : "—"}
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-sm text-right">
                            {stats ? `$${stats.total_cost.toFixed(2)}` : "—"}
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-sm text-right">
                            {stats ? `$${stats.total_outcomes_value.toFixed(2)}` : "—"}
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-sm text-right">
                            {stats ? (
                              <span
                                className={
                                  stats.margin >= 0.5
                                    ? "text-success font-medium"
                                    : stats.margin >= 0.2
                                      ? "text-gold-dark font-medium"
                                      : "text-destructive font-medium"
                                }
                              >
                                {Math.round(stats.margin * 100)}%
                              </span>
                            ) : (
                              "—"
                            )}
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-center">
                            <div className="flex justify-center gap-2">
                              <Button
                                size="sm"
                                variant="outline"
                                className="h-8 px-2 text-blue hover:text-blue hover:border-blue"
                                onClick={() => {
                                  setEditAgentId(agent.id)
                                  setEditData({
                                    name: agent.name || "",
                                    description: agent.description || "",
                                    billing_model_id: agent.billing_model_id?.toString() || "",
                                    is_active: agent.is_active,
                                  })
                                }}
                              >
                                <Edit className="h-3.5 w-3.5 mr-1" />
                                Edit
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                className="h-8 px-2 text-destructive hover:text-destructive hover:border-destructive"
                                onClick={() => handleDelete(agent.id)}
                              >
                                <Trash2 className="h-3.5 w-3.5 mr-1" />
                                Delete
                              </Button>
                            </div>
                          </td>
                        </tr>
                        {editAgentId === agent.id && (
                          <tr>
                            <td colSpan={7} className="bg-muted/30 p-4">
                              <div className="rounded-lg border border-border bg-card p-4 shadow-sm">
                                <h3 className="text-sm font-medium mb-3">Edit Agent</h3>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                  <div className="space-y-2">
                                    <label className="text-xs font-medium text-muted-foreground">Name</label>
                                    <Input
                                      placeholder="Agent name"
                                      value={editData.name}
                                      onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                                    />
                                  </div>
                                  <div className="space-y-2">
                                    <label className="text-xs font-medium text-muted-foreground">Description</label>
                                    <Input
                                      placeholder="Description"
                                      value={editData.description}
                                      onChange={(e) => setEditData({ ...editData, description: e.target.value })}
                                    />
                                  </div>
                                  <div className="space-y-2">
                                    <label className="text-xs font-medium text-muted-foreground">Billing Model</label>
                                    <select
                                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                      value={editData.billing_model_id}
                                      onChange={(e) => {
                                        const val = e.target.value
                                        if (val === "new") router.push("/pricing")
                                        else setEditData({ ...editData, billing_model_id: val })
                                      }}
                                    >
                                      <option value="">Select billing model</option>
                                      {billingModels.map((m) => (
                                        <option key={m.id} value={m.id}>
                                          {m.name}
                                        </option>
                                      ))}
                                      <option value="new">+ Create new model</option>
                                    </select>
                                  </div>
                                </div>
                                <div className="flex items-center gap-3 mt-4">
                                  <div className="flex items-center">
                                    <input
                                      type="checkbox"
                                      id={`active-${agent.id}`}
                                      className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                                      checked={editData.is_active}
                                      onChange={(e) => setEditData({ ...editData, is_active: e.target.checked })}
                                    />
                                    <label htmlFor={`active-${agent.id}`} className="ml-2 text-sm">
                                      Active
                                    </label>
                                  </div>
                                  <div className="flex-1"></div>
                                  <Button size="sm" variant="ghost" onClick={() => setEditAgentId(null)}>
                                    Cancel
                                  </Button>
                                  <Button size="sm" onClick={() => handleSave(agent.id)}>
                                    Save Changes
                                  </Button>
                                </div>
                              </div>
                            </td>
                          </tr>
                        )}
                      </Fragment>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
