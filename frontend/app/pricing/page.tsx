"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import api, { setAuthToken } from "../../utils/api"
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
  Code,
  FileJson,
} from "lucide-react"

export default function PricingPage() {
  const router = useRouter()
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
    model_type: "usage",
    config: "{}",
  })

  useEffect(() => {
    const token = localStorage.getItem("token")
    if (!token) {
      router.push("/login")
      return
    }
    setAuthToken(token)
    // fetch current user to get organization_id
    api
      .get("/auth/me")
      .then((res) => {
        const oid = res.data.organization_id
        setOrgId(oid)
        return api.get(`/billing-models?org_id=${oid}`)
      })
      .then((res) => setModels(res.data))
      .catch((err) => setError(err.response?.data?.detail || err.message))
      .finally(() => setLoading(false))
  }, [router])

  const handleCreateModel = async () => {
    if (!orgId || !newModel.name || !newModel.model_type) return

    try {
      let config = {}
      try {
        config = JSON.parse(newModel.config)
      } catch (e) {
        setError("Invalid JSON in config")
        return
      }

      const payload = {
        name: newModel.name,
        description: newModel.description,
        model_type: newModel.model_type,
        config,
        is_active: true,
        organization_id: orgId,
      }

      const res = await api.post("/billing-models", payload)
      setModels((prev) => [...prev, res.data])
      setShowCreateForm(false)
      setNewModel({
        name: "",
        description: "",
        model_type: "usage",
        config: "{}",
      })
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message)
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
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message)
    }
  }

  const getModelIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case "usage":
        return <BarChart className="h-5 w-5" />
      case "seat":
        return <Users className="h-5 w-5" />
      case "hybrid":
        return <Zap className="h-5 w-5" />
      default:
        return <DollarSign className="h-5 w-5" />
    }
  }

  const getModelTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case "usage":
        return "bg-blue/10 text-blue border-blue/20"
      case "seat":
        return "bg-purple/10 text-purple border-purple/20"
      case "hybrid":
        return "bg-gold/10 text-gold-dark border-gold/20"
      default:
        return "bg-teal/10 text-teal border-teal/20"
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
    <div className="p-4 md:p-8 space-y-8 max-w-[1400px] mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-gradient-to-r from-background to-muted/20 p-6 rounded-xl border border-border/50 shadow-sm">
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
          <div className="relative w-full md:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search pricing models..."
              className="pl-9"
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
            <TabsTrigger value="usage">Usage</TabsTrigger>
            <TabsTrigger value="seat">Seat</TabsTrigger>
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
        <Card className="border-border/50 shadow-sm overflow-hidden">
          <CardHeader className="bg-gradient-to-r from-gold/5 to-transparent">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Plus className="h-4 w-4 text-gold" />
                <CardTitle>Create New Pricing Model</CardTitle>
              </div>
              <Badge variant="outline" className="bg-gold/10 text-gold-dark border-gold/20">
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
                    <option value="usage">Usage-based</option>
                    <option value="seat">Seat-based</option>
                    <option value="hybrid">Hybrid</option>
                    <option value="outcome">Outcome-based</option>
                  </select>
                </div>
              </div>
              <div className="space-y-2">
                <label htmlFor="model-config" className="text-sm font-medium flex items-center gap-2">
                  <FileJson className="h-4 w-4" />
                  Configuration (JSON)
                </label>
                <div className="relative">
                  <textarea
                    id="model-config"
                    className="flex min-h-[200px] w-full rounded-md border border-input bg-card px-3 py-2 text-sm font-mono ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    placeholder='{"tier1": {"price": 10}, "tier2": {"price": 20}}'
                    value={newModel.config}
                    onChange={(e) => setNewModel({ ...newModel, config: e.target.value })}
                  />
                  <Code className="absolute right-3 bottom-3 h-4 w-4 text-muted-foreground" />
                </div>
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
              className="overflow-hidden border-border/50 shadow-sm hover:shadow-md transition-shadow duration-300"
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
                <div className="bg-muted/20 rounded-lg p-3 overflow-auto max-h-[200px] border border-border/30">
                  <pre className="text-xs font-mono">{JSON.stringify(model.config, null, 2)}</pre>
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
