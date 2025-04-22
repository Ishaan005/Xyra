"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import api, { setAuthToken } from "../../utils/api"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
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
} from "lucide-react"

export default function PricingPage() {
  const router = useRouter()
  const [models, setModels] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState("all")

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
        const orgId = res.data.organization_id
        return api.get(`/billing-models?org_id=${orgId}`)
      })
      .then((res) => setModels(res.data))
      .catch((err) => setError(err.response?.data?.detail || err.message))
      .finally(() => setLoading(false))
  }, [router])

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
        return "bg-blue-20 text-blue border-blue"
      case "seat":
        return "bg-purple-20 text-purple border-purple"
      case "hybrid":
        return "bg-gold-20 text-gold-dark border-gold"
      default:
        return "bg-teal-20 text-teal border-teal"
    }
  }

  const filteredModels =
    activeTab === "all" ? models : models.filter((model) => model.model_type.toLowerCase() === activeTab)

  if (loading) {
    return (
      <div className="p-8 space-y-6 max-w-[1200px] mx-auto">
        <div className="flex items-center justify-between">
          <Skeleton className="h-10 w-[250px]" />
          <Skeleton className="h-10 w-[120px]" />
        </div>
        <Skeleton className="h-12 w-[400px] rounded-lg" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <Skeleton key={i} className="h-[300px] w-full rounded-xl" />
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-8 flex flex-col items-center justify-center min-h-[50vh] text-center">
        <div className="rounded-full bg-destructive/10 p-4 mb-4">
          <AlertCircle className="h-8 w-8 text-destructive" />
        </div>
        <h2 className="text-2xl font-bold mb-2">Error Loading Pricing Models</h2>
        <p className="text-gray-dark mb-4">{error}</p>
        <Button onClick={() => window.location.reload()}>Try Again</Button>
      </div>
    )
  }

  return (
    <div className="p-4 md:p-8 space-y-8 max-w-[1200px] mx-auto">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold">Pricing Models</h1>
          <p className="text-gray-dark">Manage your pricing strategies and billing configurations</p>
        </div>

        <Button className="gap-2">
          <Plus className="h-4 w-4" />
          Create New Model
        </Button>
      </div>

      <Tabs defaultValue="all" value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid grid-cols-4 w-full max-w-md">
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="usage">Usage</TabsTrigger>
          <TabsTrigger value="seat">Seat</TabsTrigger>
          <TabsTrigger value="hybrid">Hybrid</TabsTrigger>
        </TabsList>
      </Tabs>

      {filteredModels.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="rounded-full bg-muted p-4 mb-4">
            <Settings className="h-8 w-8 text-muted-foreground" />
          </div>
          <h2 className="text-xl font-bold mb-2">No pricing models found</h2>
          <p className="text-gray-dark mb-4">Create your first pricing model to get started</p>
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            Create New Model
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredModels.map((model) => (
            <Card key={model.id} className="overflow-hidden">
              <CardHeader className="pb-4">
                <div className="flex justify-between items-start">
                  <Badge className={`${getModelTypeColor(model.model_type)} px-2 py-0.5 text-xs font-medium`}>
                    {model.model_type}
                  </Badge>
                  <div className="flex gap-1">
                    <Button className="h-8 w-8">
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button className="h-8 w-8 text-destructive">
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
                <div className="bg-gray-20 rounded-lg p-3 overflow-auto max-h-[200px]">
                  <pre className="text-xs font-mono">{JSON.stringify(model.config, null, 2)}</pre>
                </div>
              </CardContent>
              <CardFooter className="flex justify-between border-t pt-4">
                <div className="flex items-center text-sm">
                  <CheckCircle2 className="h-4 w-4 text-success mr-1" />
                  Active
                </div>
                <Button className="gap-1 text-sm">
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
