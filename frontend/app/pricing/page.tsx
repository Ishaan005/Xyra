"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useSession } from "next-auth/react"
import api, { setAuthToken } from "../../utils/api"
import toast from "react-hot-toast"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Input } from "@/components/ui/input"
import {
  AlertCircle,
  CheckCircle2,
  Copy,
  Edit,
  Plus,
  Settings,
  Trash2,
  DollarSign,
  Users,
  BarChart,
  Zap,
  Search,
  Filter,
} from "lucide-react"

export default function PricingPage() {
  const router = useRouter()
  const { data: session, status } = useSession({
    required: true,
    onUnauthenticated() {
      router.push('/login')
    }
  })
  const [models, setModels] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [orgId, setOrgId] = useState<number | null>(null)
  const [activeTab, setActiveTab] = useState("all")
  const [searchQuery, setSearchQuery] = useState("")
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newModel, setNewModel] = useState({
    name: "",
    description: "",
    model_type: "activity",
    // Enhanced Activity/Usage
    price_per_unit: "",
    activity_type: "",
    unit_type: "action",
    base_agent_fee: "",
    volume_pricing_enabled: false,
    volume_tier_1_threshold: "",
    volume_tier_1_price: "",
    volume_tier_2_threshold: "",
    volume_tier_2_price: "",
    volume_tier_3_threshold: "",
    volume_tier_3_price: "",
    minimum_charge: "",
    billing_frequency: "monthly",
    is_active: true,
    // Agent
    agent_base_agent_fee: "",
    agent_billing_frequency: "monthly",
    agent_setup_fee: "",
    agent_volume_discount_enabled: false,
    agent_volume_discount_threshold: "",
    agent_volume_discount_percentage: "",
    agent_tier: "professional",
    // Outcome
    outcome_type: "",
    percentage: "",
    // Hybrid
    hybrid_base_fee: "",
    include_agent: false,
    include_activity: false,
    include_outcome: false,
  })

  useEffect(() => {
    if (status !== 'authenticated') return
    const token = session.user.accessToken ?? ""
    setAuthToken(token)
    // fetch organization and models
    api.get('/auth/me')
      .then(res => {
        const oid = res.data.organization_id
        setOrgId(oid)
        return api.get(`/billing-models?org_id=${oid}`)
      })
      .then(res => setModels(res.data))
      .catch(err => setError(err.response?.data?.detail || err.message))
      .finally(() => setLoading(false))
  }, [status, session])

  const handleCreateModel = async () => {
    if (!orgId || !newModel.name || !newModel.model_type) return
    
    // Build payload with dedicated fields instead of config object
    const payload: any = {
      name: newModel.name,
      description: newModel.description,
      model_type: newModel.model_type,
      is_active: true,
      organization_id: orgId,
    }

    switch (newModel.model_type) {
      case "activity":
        payload.activity_price_per_unit = Number.parseFloat(newModel.price_per_unit) || 0
        payload.activity_activity_type = newModel.activity_type
        payload.activity_unit_type = newModel.unit_type
        payload.activity_base_agent_fee = Number.parseFloat(newModel.base_agent_fee) || 0
        payload.activity_volume_pricing_enabled = newModel.volume_pricing_enabled
        if (newModel.volume_pricing_enabled) {
          payload.activity_volume_tier_1_threshold = Number.parseInt(newModel.volume_tier_1_threshold) || null
          payload.activity_volume_tier_1_price = Number.parseFloat(newModel.volume_tier_1_price) || null
          payload.activity_volume_tier_2_threshold = Number.parseInt(newModel.volume_tier_2_threshold) || null
          payload.activity_volume_tier_2_price = Number.parseFloat(newModel.volume_tier_2_price) || null
          payload.activity_volume_tier_3_threshold = Number.parseInt(newModel.volume_tier_3_threshold) || null
          payload.activity_volume_tier_3_price = Number.parseFloat(newModel.volume_tier_3_price) || null
        }
        payload.activity_minimum_charge = Number.parseFloat(newModel.minimum_charge) || 0
        payload.activity_billing_frequency = newModel.billing_frequency
        payload.activity_is_active = newModel.is_active
        break
      case "agent":
        payload.agent_base_agent_fee = Number.parseFloat(newModel.agent_base_agent_fee) || 0
        payload.agent_billing_frequency = newModel.agent_billing_frequency
        payload.agent_setup_fee = Number.parseFloat(newModel.agent_setup_fee) || 0
        payload.agent_volume_discount_enabled = newModel.agent_volume_discount_enabled
        if (newModel.agent_volume_discount_enabled) {
          payload.agent_volume_discount_threshold = Number.parseInt(newModel.agent_volume_discount_threshold) || 0
          payload.agent_volume_discount_percentage = Number.parseFloat(newModel.agent_volume_discount_percentage) || 0
        }
        payload.agent_tier = newModel.agent_tier
        break
      case "outcome":
        payload.outcome_outcome_type = newModel.outcome_type
        payload.outcome_percentage = Number.parseFloat(newModel.percentage) || 0
        break
      case "hybrid":
        payload.hybrid_base_fee = Number.parseFloat(newModel.hybrid_base_fee) || 0
        if (newModel.include_agent) {
          payload.hybrid_agent_config = {
            base_agent_fee: Number.parseFloat(newModel.agent_base_agent_fee) || 0,
            billing_frequency: newModel.agent_billing_frequency,
            setup_fee: Number.parseFloat(newModel.agent_setup_fee) || 0,
            volume_discount_enabled: newModel.agent_volume_discount_enabled,
            volume_discount_threshold: newModel.agent_volume_discount_enabled ? Number.parseInt(newModel.agent_volume_discount_threshold) || 0 : null,
            volume_discount_percentage: newModel.agent_volume_discount_enabled ? Number.parseFloat(newModel.agent_volume_discount_percentage) || 0 : null,
            agent_tier: newModel.agent_tier,
          }
        }
        if (newModel.include_activity) {
          payload.hybrid_activity_configs = [
            {
              activity_type: newModel.activity_type,
              price_per_unit: Number.parseFloat(newModel.price_per_unit) || 0,
              unit_type: newModel.unit_type,
              base_agent_fee: Number.parseFloat(newModel.base_agent_fee) || 0,
              volume_pricing_enabled: newModel.volume_pricing_enabled,
              volume_tier_1_threshold: newModel.volume_pricing_enabled ? Number.parseInt(newModel.volume_tier_1_threshold) || null : null,
              volume_tier_1_price: newModel.volume_pricing_enabled ? Number.parseFloat(newModel.volume_tier_1_price) || null : null,
              volume_tier_2_threshold: newModel.volume_pricing_enabled ? Number.parseInt(newModel.volume_tier_2_threshold) || null : null,
              volume_tier_2_price: newModel.volume_pricing_enabled ? Number.parseFloat(newModel.volume_tier_2_price) || null : null,
              volume_tier_3_threshold: newModel.volume_pricing_enabled ? Number.parseInt(newModel.volume_tier_3_threshold) || null : null,
              volume_tier_3_price: newModel.volume_pricing_enabled ? Number.parseFloat(newModel.volume_tier_3_price) || null : null,
              minimum_charge: Number.parseFloat(newModel.minimum_charge) || 0,
              billing_frequency: newModel.billing_frequency,
              is_active: newModel.is_active,
            },
          ]
        }
        if (newModel.include_outcome) {
          payload.hybrid_outcome_configs = [
            {
              outcome_type: newModel.outcome_type,
              percentage: Number.parseFloat(newModel.percentage) || 0,
            },
          ]
        }
        break
    }

    try {
      const res = await api.post("/billing-models", payload)
      setModels((prev) => [...prev, res.data])
      setShowCreateForm(false)
      // reset form
      setNewModel({
        name: "",
        description: "",
        model_type: "activity",
        // Enhanced Activity/Usage
        price_per_unit: "",
        activity_type: "",
        unit_type: "action",
        base_agent_fee: "",
        volume_pricing_enabled: false,
        volume_tier_1_threshold: "",
        volume_tier_1_price: "",
        volume_tier_2_threshold: "",
        volume_tier_2_price: "",
        volume_tier_3_threshold: "",
        volume_tier_3_price: "",
        minimum_charge: "",
        billing_frequency: "monthly",
        is_active: true,
        // Agent
        agent_base_agent_fee: "",
        agent_billing_frequency: "monthly",
        agent_setup_fee: "",
        agent_volume_discount_enabled: false,
        agent_volume_discount_threshold: "",
        agent_volume_discount_percentage: "",
        agent_tier: "professional",
        // Outcome
        outcome_type: "",
        percentage: "",
        // Hybrid
        hybrid_base_fee: "",
        include_agent: false,
        include_activity: false,
        include_outcome: false,
      })
      toast.success("Pricing model created successfully")
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message
      setError(msg)
      toast.error(msg)
    }
  }

  const handleDuplicate = async (model: any) => {
    if (!orgId) return
    try {
      const payload = {
        ...model,
        name: `${model.name} (Copy)`,
        organization_id: orgId,
        id: undefined,
      }
      delete payload.id

      const res = await api.post("/billing-models", payload)
      setModels((prev) => [...prev, res.data])
      toast.success("Pricing model duplicated")
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message
      setError(msg)
      toast.error(msg)
    }
  }

  // Delete billing model
  const handleDeleteModel = async (modelId: number) => {
    if (!orgId) return
    if (!confirm("Are you sure you want to delete this pricing model?")) return
    try {
      await api.delete(`/billing-models/${modelId}`)
      setModels((prev) => prev.filter((m) => m.id !== modelId))
      toast.success("Pricing model deleted")
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message
      setError(msg)
      toast.error(msg)
    }
  }

  const getModelIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case "activity":
        return <BarChart className="h-5 w-5" />
      case "agent":
        return <Users className="h-5 w-5" />
      case "hybrid":
        return <Zap className="h-5 w-5" />
      case "outcome":
        return <DollarSign className="h-5 w-5" />
      default:
        return <DollarSign className="h-5 w-5" />
    }
  }

  const getModelTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case "activity":
        return "bg-blue/10 text-blue border-blue/8"
      case "agent":
        return "bg-purple/10 text-purple border-purple/8"
      case "hybrid":
        return "bg-gold/10 text-gold-dark border-gold/8"
      case "outcome":
        return "bg-green/10 text-green border-green/8"
      default:
        return "bg-teal/10 text-teal border-teal/8"
    }
  }

  const filteredModels = models.filter((model) => {
    const matchesTab = activeTab === "all" || model.model_type.toLowerCase() === activeTab
    const matchesSearch =
      searchQuery === "" ||
      model.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (model.description && model.description.toLowerCase().includes(searchQuery.toLowerCase()))
    return matchesTab && matchesSearch
  })

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-gradient-to-r from-background to-muted/20 p-6 rounded-xl border border-border/8 shadow-sm ring-1 ring-border/5 hover:ring-border/10 transition-all duration-300">
        <div className="flex items-center gap-3">
          <div className="rounded-full bg-gold/10 p-2">
            <DollarSign className="h-6 w-6 text-gold" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">Pricing Models</h1>
            <p className="text-muted-foreground">Manage your pricing strategies and billing configurations</p>
          </div>
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto">
          <div className="relative flex-grow w-full">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search pricing models..."
              className="pl-9 w-full"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <Button onClick={() => window.location.reload()} variant="outline" size="icon" className="flex-shrink-0">
            <Filter className="h-4 w-4" />
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

      {/* Tabs and Create Button */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <Tabs defaultValue="all" value={activeTab} onValueChange={setActiveTab} className="w-full sm:w-auto">
          <TabsList className="grid grid-cols-4 w-full sm:w-auto">
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="activity">Activity</TabsTrigger>
            <TabsTrigger value="agent">Agent</TabsTrigger>
            <TabsTrigger value="hybrid">Hybrid</TabsTrigger>
          </TabsList>
        </Tabs>

        <Button className="gap-2 w-full sm:w-auto" onClick={() => setShowCreateForm(!showCreateForm)}>
          <Plus className="h-4 w-4" />
          Create New Model
        </Button>
      </div>

      {/* Create Form */}
      {showCreateForm && (
        <Card className="border-border/8 ring-1 ring-border/5 shadow-sm overflow-hidden hover:ring-border/10 transition-all duration-300">
          <CardHeader className="bg-gradient-to-r from-gold/5 to-transparent">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Plus className="h-4 w-4 text-gold" />
                <CardTitle>Create New Pricing Model</CardTitle>
              </div>
              <Badge variant="outline" className="bg-gold/10 text-gold-dark border-gold/8">
                New
              </Badge>
            </div>
            <CardDescription>Configure a new pricing model for your agents</CardDescription>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="space-y-2">
                  <label htmlFor="model-name" className="text-sm font-medium">
                    Model Name
                  </label>
                  <Input
                    id="model-name"
                    placeholder="Enter model name"
                    value={newModel.name}
                    onChange={(e) => setNewModel({ ...newModel, name: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <label htmlFor="model-description" className="text-sm font-medium">
                    Description
                  </label>
                  <Input
                    id="model-description"
                    placeholder="Enter description"
                    value={newModel.description}
                    onChange={(e) => setNewModel({ ...newModel, description: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <label htmlFor="model-type" className="text-sm font-medium">
                    Model Type
                  </label>
                  <select
                    id="model-type"
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    value={newModel.model_type}
                    onChange={(e) => setNewModel({ ...newModel, model_type: e.target.value })}
                  >
                    <option value="activity">Activity-based</option>
                    <option value="agent">Agent-based</option>
                    <option value="hybrid">Hybrid</option>
                    <option value="outcome">Outcome-based</option>
                  </select>
                </div>
              </div>
              <div className="space-y-2">
                {/* Render config fields by model_type */}
                {newModel.model_type === "activity" && (
                  <>
                    {/* Enhanced Activity-based */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Price per unit</label>
                        <Input
                          type="number"
                          step="0.001"
                          placeholder="0.001"
                          value={newModel.price_per_unit}
                          onChange={(e) => setNewModel({ ...newModel, price_per_unit: e.target.value })}
                        />
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Activity type</label>
                        <Input
                          placeholder="tokens, api_calls, queries..."
                          value={newModel.activity_type}
                          onChange={(e) => setNewModel({ ...newModel, activity_type: e.target.value })}
                        />
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Unit type</label>
                        <select
                          className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                          value={newModel.unit_type}
                          onChange={(e) => setNewModel({ ...newModel, unit_type: e.target.value })}
                        >
                          <option value="action">Action</option>
                          <option value="token">Token</option>
                          <option value="minute">Minute</option>
                          <option value="request">Request</option>
                          <option value="query">Query</option>
                          <option value="completion">Completion</option>
                        </select>
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Base agent fee (optional)</label>
                        <Input
                          type="number"
                          step="0.01"
                          placeholder="0.00"
                          value={newModel.base_agent_fee}
                          onChange={(e) => setNewModel({ ...newModel, base_agent_fee: e.target.value })}
                        />
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="volume-pricing"
                          checked={newModel.volume_pricing_enabled}
                          onChange={(e) => setNewModel({ ...newModel, volume_pricing_enabled: e.target.checked })}
                        />
                        <label htmlFor="volume-pricing" className="text-sm font-medium">
                          Enable volume pricing tiers
                        </label>
                      </div>
                      
                      {newModel.volume_pricing_enabled && (
                        <div className="space-y-4 p-4 border rounded-lg bg-slate-50">
                          <h4 className="font-medium text-sm">Volume Pricing Tiers</h4>
                          
                          {/* Tier 1 */}
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                              <label className="text-sm">Tier 1 threshold</label>
                              <Input
                                type="number"
                                placeholder="10000"
                                value={newModel.volume_tier_1_threshold}
                                onChange={(e) => setNewModel({ ...newModel, volume_tier_1_threshold: e.target.value })}
                              />
                            </div>
                            <div className="space-y-2">
                              <label className="text-sm">Tier 1 price per unit</label>
                              <Input
                                type="number"
                                step="0.0001"
                                placeholder="0.0008"
                                value={newModel.volume_tier_1_price}
                                onChange={(e) => setNewModel({ ...newModel, volume_tier_1_price: e.target.value })}
                              />
                            </div>
                          </div>
                          
                          {/* Tier 2 */}
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                              <label className="text-sm">Tier 2 threshold</label>
                              <Input
                                type="number"
                                placeholder="50000"
                                value={newModel.volume_tier_2_threshold}
                                onChange={(e) => setNewModel({ ...newModel, volume_tier_2_threshold: e.target.value })}
                              />
                            </div>
                            <div className="space-y-2">
                              <label className="text-sm">Tier 2 price per unit</label>
                              <Input
                                type="number"
                                step="0.0001"
                                placeholder="0.0006"
                                value={newModel.volume_tier_2_price}
                                onChange={(e) => setNewModel({ ...newModel, volume_tier_2_price: e.target.value })}
                              />
                            </div>
                          </div>
                          
                          {/* Tier 3 */}
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                              <label className="text-sm">Tier 3 threshold</label>
                              <Input
                                type="number"
                                placeholder="100000"
                                value={newModel.volume_tier_3_threshold}
                                onChange={(e) => setNewModel({ ...newModel, volume_tier_3_threshold: e.target.value })}
                              />
                            </div>
                            <div className="space-y-2">
                              <label className="text-sm">Tier 3 price per unit</label>
                              <Input
                                type="number"
                                step="0.0001"
                                placeholder="0.0004"
                                value={newModel.volume_tier_3_price}
                                onChange={(e) => setNewModel({ ...newModel, volume_tier_3_price: e.target.value })}
                              />
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Minimum charge</label>
                        <Input
                          type="number"
                          step="0.01"
                          placeholder="0.00"
                          value={newModel.minimum_charge}
                          onChange={(e) => setNewModel({ ...newModel, minimum_charge: e.target.value })}
                        />
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Billing frequency</label>
                        <select
                          className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                          value={newModel.billing_frequency}
                          onChange={(e) => setNewModel({ ...newModel, billing_frequency: e.target.value })}
                        >
                          <option value="monthly">Monthly</option>
                          <option value="daily">Daily</option>
                          <option value="per_use">Per Use</option>
                        </select>
                      </div>
                    </div>
                  </>
                )}
                {newModel.model_type === "agent" && (
                  <>
                    {/* Agent-based */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Base agent fee</label>
                      <Input
                        type="number"
                        value={newModel.agent_base_agent_fee}
                        onChange={(e) => setNewModel({ ...newModel, agent_base_agent_fee: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Setup fee (optional)</label>
                      <Input
                        type="number"
                        value={newModel.agent_setup_fee}
                        onChange={(e) => setNewModel({ ...newModel, agent_setup_fee: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Agent tier</label>
                      <select
                        className="w-full"
                        value={newModel.agent_tier}
                        onChange={(e) => setNewModel({ ...newModel, agent_tier: e.target.value })}
                      >
                        <option value="starter">Starter</option>
                        <option value="professional">Professional</option>
                        <option value="enterprise">Enterprise</option>
                      </select>
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Billing frequency</label>
                      <select
                        className="w-full"
                        value={newModel.agent_billing_frequency}
                        onChange={(e) => setNewModel({ ...newModel, agent_billing_frequency: e.target.value })}
                      >
                        <option value="monthly">Monthly</option>
                        <option value="yearly">Yearly</option>
                      </select>
                    </div>
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={newModel.agent_volume_discount_enabled}
                        onChange={(e) => setNewModel({ ...newModel, agent_volume_discount_enabled: e.target.checked })}
                      />
                      <label className="text-sm">Enable volume discount</label>
                    </div>
                    {newModel.agent_volume_discount_enabled && (
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Volume threshold (number of agents)</label>
                        <Input
                          type="number"
                          value={newModel.agent_volume_discount_threshold}
                          onChange={(e) => setNewModel({ ...newModel, agent_volume_discount_threshold: e.target.value })}
                        />
                        <label className="text-sm font-medium">Discount percentage</label>
                        <Input
                          type="number"
                          value={newModel.agent_volume_discount_percentage}
                          onChange={(e) => setNewModel({ ...newModel, agent_volume_discount_percentage: e.target.value })}
                        />
                      </div>
                    )}
                  </>
                )}
                {newModel.model_type === "outcome" && (
                  <>
                    {" "}
                    {/* Outcome-based */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Outcome type</label>
                      <Input
                        placeholder="revenue_uplift…"
                        value={newModel.outcome_type}
                        onChange={(e) => setNewModel({ ...newModel, outcome_type: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Percentage</label>
                      <Input
                        type="number"
                        value={newModel.percentage}
                        onChange={(e) => setNewModel({ ...newModel, percentage: e.target.value })}
                      />
                    </div>
                  </>
                )}
                {newModel.model_type === "hybrid" && (
                  <>
                    {/* Hybrid */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Base fee</label>
                      <Input
                        type="number"
                        value={newModel.hybrid_base_fee}
                        onChange={(e) => setNewModel({ ...newModel, hybrid_base_fee: e.target.value })}
                      />
                    </div>
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={newModel.include_agent}
                        onChange={(e) => setNewModel({ ...newModel, include_agent: e.target.checked })}
                      />
                      <label className="text-sm">Include agent configuration</label>
                    </div>
                    {newModel.include_agent && (
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Base agent fee</label>
                        <Input
                          type="number"
                          value={newModel.agent_base_agent_fee}
                          onChange={(e) => setNewModel({ ...newModel, agent_base_agent_fee: e.target.value })}
                        />
                        <label className="text-sm font-medium">Setup fee (optional)</label>
                        <Input
                          type="number"
                          value={newModel.agent_setup_fee}
                          onChange={(e) => setNewModel({ ...newModel, agent_setup_fee: e.target.value })}
                        />
                        <label className="text-sm font-medium">Agent tier</label>
                        <select
                          className="w-full"
                          value={newModel.agent_tier}
                          onChange={(e) => setNewModel({ ...newModel, agent_tier: e.target.value })}
                        >
                          <option value="starter">Starter</option>
                          <option value="professional">Professional</option>
                          <option value="enterprise">Enterprise</option>
                        </select>
                        <label className="text-sm font-medium">Billing frequency</label>
                        <select
                          className="w-full"
                          value={newModel.agent_billing_frequency}
                          onChange={(e) => setNewModel({ ...newModel, agent_billing_frequency: e.target.value })}
                        >
                          <option value="monthly">Monthly</option>
                          <option value="yearly">Yearly</option>
                        </select>
                        <div className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={newModel.agent_volume_discount_enabled}
                            onChange={(e) => setNewModel({ ...newModel, agent_volume_discount_enabled: e.target.checked })}
                          />
                          <label className="text-sm">Enable volume discount</label>
                        </div>
                        {newModel.agent_volume_discount_enabled && (
                          <div className="space-y-2">
                            <label className="text-sm font-medium">Volume threshold</label>
                            <Input
                              type="number"
                              value={newModel.agent_volume_discount_threshold}
                              onChange={(e) => setNewModel({ ...newModel, agent_volume_discount_threshold: e.target.value })}
                            />
                            <label className="text-sm font-medium">Discount percentage</label>
                            <Input
                              type="number"
                              value={newModel.agent_volume_discount_percentage}
                              onChange={(e) => setNewModel({ ...newModel, agent_volume_discount_percentage: e.target.value })}
                            />
                          </div>
                        )}
                      </div>
                    )}
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={newModel.include_activity}
                        onChange={(e) => setNewModel({ ...newModel, include_activity: e.target.checked })}
                      />
                      <label className="text-sm">Include activity configuration</label>
                    </div>
                    {newModel.include_activity && (
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Activity type</label>
                        <Input
                          placeholder="tokens, api_calls..."
                          value={newModel.activity_type}
                          onChange={(e) => setNewModel({ ...newModel, activity_type: e.target.value })}
                        />
                        <label className="text-sm font-medium">Price per unit</label>
                        <Input
                          type="number"
                          step="0.001"
                          value={newModel.price_per_unit}
                          onChange={(e) => setNewModel({ ...newModel, price_per_unit: e.target.value })}
                        />
                      </div>
                    )}
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={newModel.include_outcome}
                        onChange={(e) => setNewModel({ ...newModel, include_outcome: e.target.checked })}
                      />
                      <label className="text-sm">Include outcome configuration</label>
                    </div>
                    {newModel.include_outcome && (
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Outcome type</label>
                        <Input
                          placeholder="revenue_uplift…"
                          value={newModel.outcome_type}
                          onChange={(e) => setNewModel({ ...newModel, outcome_type: e.target.value })}
                        />
                        <label className="text-sm font-medium">Percentage</label>
                        <Input
                          type="number"
                          value={newModel.percentage}
                          onChange={(e) => setNewModel({ ...newModel, percentage: e.target.value })}
                        />
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex justify-between border-t pt-4">
            <Button variant="outline" onClick={() => setShowCreateForm(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateModel}>
              <Plus className="h-4 w-4 mr-2" />
              Create Model
            </Button>
          </CardFooter>
        </Card>
      )}

      {/* Cost Calculator Preview */}
      {newModel.model_type === "activity" && newModel.price_per_unit && (
        <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h4 className="font-medium text-sm mb-3 text-blue-800">💡 Cost Preview</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-blue-700">Example usage:</label>
              <input
                type="number"
                placeholder="10000"
                className="w-full mt-1 px-2 py-1 text-sm border rounded"
                onChange={(e) => {
                  const units = parseInt(e.target.value) || 0;
                  const agents = 1;
                  const basePrice = parseFloat(newModel.price_per_unit) || 0;
                  const baseFee = parseFloat(newModel.base_agent_fee) || 0;
                  const minCharge = parseFloat(newModel.minimum_charge) || 0;
                  
                  let cost = baseFee * agents;
                  
                  if (newModel.volume_pricing_enabled) {
                    const tier1Threshold = parseInt(newModel.volume_tier_1_threshold) || 0;
                    const tier1Price = parseFloat(newModel.volume_tier_1_price) || basePrice;
                    
                    if (units <= tier1Threshold) {
                      cost += units * tier1Price;
                    } else {
                      cost += tier1Threshold * tier1Price;
                      const remainingUnits = units - tier1Threshold;
                      const tier2Threshold = parseInt(newModel.volume_tier_2_threshold) || 0;
                      const tier2Price = parseFloat(newModel.volume_tier_2_price) || basePrice;
                      
                      if (remainingUnits <= (tier2Threshold - tier1Threshold)) {
                        cost += remainingUnits * tier2Price;
                      } else {
                        cost += (tier2Threshold - tier1Threshold) * tier2Price;
                        const finalUnits = remainingUnits - (tier2Threshold - tier1Threshold);
                        const tier3Price = parseFloat(newModel.volume_tier_3_price) || basePrice;
                        cost += finalUnits * tier3Price;
                      }
                    }
                  } else {
                    cost += units * basePrice;
                  }
                  
                  cost = Math.max(cost, minCharge);
                  
                  const preview = document.getElementById('cost-preview');
                  if (preview) {
                    preview.textContent = `$${cost.toFixed(2)}`;
                  }
                }}
              />
              <span className="text-xs text-blue-600">{newModel.unit_type}s</span>
            </div>
            <div>
              <label className="text-xs text-blue-700">Estimated cost:</label>
              <div id="cost-preview" className="mt-1 px-2 py-1 bg-white border rounded text-sm font-mono">
                $0.00
              </div>
            </div>
          </div>
          <p className="text-xs text-blue-600 mt-2">
            * Preview includes base agent fee{newModel.volume_pricing_enabled ? " and volume discounts" : ""}
          </p>
        </div>
      )}

      {/* Models Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <Card key={i} className="overflow-hidden">
              <CardHeader className="pb-4">
                <div className="flex justify-between items-start">
                  <Skeleton className="h-6 w-24" />
                  <div className="flex gap-1">
                    <Skeleton className="h-8 w-8 rounded-md" />
                    <Skeleton className="h-8 w-8 rounded-md" />
                  </div>
                </div>
                <div className="flex items-center gap-2 mt-2">
                  <Skeleton className="h-10 w-10 rounded-full" />
                  <Skeleton className="h-6 w-40" />
                </div>
                <Skeleton className="h-4 w-full mt-2" />
              </CardHeader>
              <CardContent className="pb-4">
                <Skeleton className="h-[200px] w-full rounded-lg" />
              </CardContent>
              <CardFooter className="flex justify-between border-t pt-4">
                <Skeleton className="h-4 w-20" />
                <Skeleton className="h-8 w-24" />
              </CardFooter>
            </Card>
          ))}
        </div>
      ) : filteredModels.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="rounded-full bg-muted p-4 mb-4">
            <Settings className="h-8 w-8 text-muted-foreground" />
          </div>
          <h2 className="text-xl font-bold mb-2">No pricing models found</h2>
          <p className="text-muted-foreground mb-4">
            {searchQuery ? "Try a different search term" : "Create your first pricing model to get started"}
          </p>
          <Button className="gap-2" onClick={() => setShowCreateForm(true)}>
            <Plus className="h-4 w-4" />
            Create New Model
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredModels.map((model) => (
            <Card
              key={model.id}
              className="overflow-hidden border-border/8 ring-1 ring-border/5 shadow-sm hover:shadow-md transition-shadow duration-300 hover:ring-border/10"
            >
              <CardHeader className="pb-4 bg-gradient-to-r from-muted/30 to-transparent">
                <div className="flex justify-between items-start">
                  <Badge className={`${getModelTypeColor(model.model_type)} px-2 py-0.5 text-xs font-medium`}>
                    {model.model_type}
                  </Badge>
                  <div className="flex gap-1">
                    <Button size="icon" className="h-8 w-8 text-blue hover:text-blue hover:border-blue" variant="ghost">
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      size="icon"
                      className="h-8 w-8 text-destructive hover:text-destructive hover:border-destructive"
                      variant="ghost"
                      onClick={() => handleDeleteModel(model.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <div className="flex items-center gap-2 mt-2">
                  <div className={`rounded-full p-2 ${getModelTypeColor(model.model_type)}`}>
                    {getModelIcon(model.model_type)}
                  </div>
                  <CardTitle>{model.name}</CardTitle>
                </div>
                <CardDescription>
                  {model.description || `A ${model.model_type.toLowerCase()} pricing model for your services`}
                </CardDescription>
              </CardHeader>
              <CardContent className="pb-4">
                <div className="space-y-3">
                  {model.model_type === "activity" && model.activity_config && model.activity_config[0] && (
                    <div className="bg-muted/20 rounded-lg p-3 border border-border/10">
                      <h4 className="font-medium text-sm mb-2">Activity Configuration</h4>
                      <div className="grid grid-cols-1 gap-2 text-xs">
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Price per unit:</span>
                          <span className="font-mono">${model.activity_config[0].price_per_unit}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Activity type:</span>
                          <span className="font-mono">{model.activity_config[0].activity_type}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Unit type:</span>
                          <span className="font-mono">{model.activity_config[0].unit_type}</span>
                        </div>
                        {model.activity_config[0].base_agent_fee > 0 && (
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Base agent fee:</span>
                            <span className="font-mono">${model.activity_config[0].base_agent_fee}</span>
                          </div>
                        )}
                        {model.activity_config[0].volume_pricing_enabled && (
                          <div className="mt-2">
                            <span className="text-muted-foreground text-xs">Volume pricing enabled</span>
                            {model.activity_config[0].volume_tier_1_threshold && (
                              <div className="flex justify-between text-xs mt-1">
                                <span>Tier 1 ({model.activity_config[0].volume_tier_1_threshold}+ units):</span>
                                <span className="font-mono">${model.activity_config[0].volume_tier_1_price}</span>
                              </div>
                            )}
                            {model.activity_config[0].volume_tier_2_threshold && (
                              <div className="flex justify-between text-xs">
                                <span>Tier 2 ({model.activity_config[0].volume_tier_2_threshold}+ units):</span>
                                <span className="font-mono">${model.activity_config[0].volume_tier_2_price}</span>
                              </div>
                            )}
                            {model.activity_config[0].volume_tier_3_threshold && (
                              <div className="flex justify-between text-xs">
                                <span>Tier 3 ({model.activity_config[0].volume_tier_3_threshold}+ units):</span>
                                <span className="font-mono">${model.activity_config[0].volume_tier_3_price}</span>
                              </div>
                            )}
                          </div>
                        )}
                        {model.activity_config[0].minimum_charge > 0 && (
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Minimum charge:</span>
                            <span className="font-mono">${model.activity_config[0].minimum_charge}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                  
                  {model.model_type === "agent" && model.agent_config && (
                    <div className="bg-muted/20 rounded-lg p-3 border border-border/10">
                      <h4 className="font-medium text-sm mb-2">Agent Configuration</h4>
                      <div className="grid grid-cols-1 gap-2 text-xs">
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Base agent fee:</span>
                          <span className="font-mono">${model.agent_config.base_agent_fee}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Billing frequency:</span>
                          <span className="font-mono">{model.agent_config.billing_frequency}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Agent tier:</span>
                          <span className="font-mono">{model.agent_config.agent_tier}</span>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {(model.model_type === "outcome" || model.model_type === "hybrid") && (
                    <div className="bg-muted/20 rounded-lg p-3 border border-border/10">
                      <h4 className="font-medium text-sm mb-2">Configuration</h4>
                      <div className="overflow-auto max-h-[120px]">
                        <pre className="text-xs font-mono">{JSON.stringify(model, null, 2)}</pre>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
              <CardFooter className="flex justify-between border-t pt-4">
                <div className="flex items-center text-sm">
                  <CheckCircle2 className="h-4 w-4 text-success mr-1" />
                  Active
                </div>
                <Button className="gap-1 text-sm" variant="outline" onClick={() => handleDuplicate(model)}>
                  <Copy className="h-3 w-3" />
                  Duplicate
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
