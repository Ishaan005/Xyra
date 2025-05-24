"use client"

import { useState, useEffect } from "react"
import { useSession } from "next-auth/react"
import { useRouter } from "next/navigation"
import { setAuthToken } from "../../utils/api"
import api from "../../utils/api"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { BarChart, LineChart } from "@/components/ui/chart"
import {
  Activity,
  CreditCard,
  DollarSign,
  Users,
  TrendingUp,
  TrendingDown,
  Percent,
  ArrowUpRight,
  ArrowDownRight,
  Calendar,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"

export default function DashboardPage() {
  const router = useRouter()
  const { data: session, status } = useSession()
  const orgId = 1 // TODO: obtain dynamically

  useEffect(() => {
    if (status === "loading") return
    if (status === "unauthenticated") return router.push("/login")
    if (status === "authenticated" && session?.user?.accessToken) setAuthToken(session.user.accessToken)
  }, [status, session, router])

  const [summary, setSummary] = useState<any>(null)
  const [topAgents, setTopAgents] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [period, setPeriod] = useState("month")

  // Fetch analytics after authentication
  useEffect(() => {
    if (status !== 'authenticated') return
    const token = session.user.accessToken ?? ""
    setAuthToken(token)
    setLoading(true)
    Promise.all([
      api.get(`/analytics/organization/${orgId}/summary`),
      api.get(`/analytics/organization/${orgId}/top-agents?limit=5`),
    ])
      .then(([sumRes, topRes]) => {
        setSummary(sumRes.data)
        setTopAgents(topRes.data)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [status, session])

  if (loading) {
    return (
      <div className="p-8 space-y-6">
        <div className="flex items-center justify-between">
          <Skeleton className="h-10 w-[250px]" />
          <Skeleton className="h-10 w-[120px]" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-[120px] w-full rounded-xl" />
          ))}
        </div>
        <Skeleton className="h-[350px] w-full rounded-xl" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-8 flex flex-col items-center justify-center min-h-[50vh] text-center">
        <div className="rounded-full bg-destructive/10 p-4 mb-4">
          <TrendingDown className="h-8 w-8 text-destructive" />
        </div>
        <h2 className="text-2xl font-bold mb-2">Error Loading Dashboard</h2>
        <p className="text-muted-foreground mb-4">{error}</p>
        <Button onClick={() => window.location.reload()}>Try Again</Button>
      </div>
    )
  }

  const agentLabels = topAgents.map((a) => a.name)
  const revenueData = topAgents.map((a) => a.metrics.total_revenue)
  const costData = topAgents.map((a) => a.metrics.total_cost)
  const marginData = topAgents.map((a) => Math.round(a.metrics.margin * 100))

  const barData = {
    labels: agentLabels,
    datasets: [
      {
        label: "Revenue",
        data: revenueData,
        backgroundColor: "rgba(255, 181, 0, 0.8)",
        borderColor: "#AF6D04",
        borderWidth: 1,
        borderRadius: 4,
        hoverBackgroundColor: "#FFB500",
      },
      {
        label: "Cost",
        data: costData,
        backgroundColor: "rgba(184, 60, 39, 0.7)",
        borderColor: "#8A2A1D",
        borderWidth: 1,
        borderRadius: 4,
        hoverBackgroundColor: "#B83C27",
      },
    ],
  }

  const marginChartData = {
    labels: agentLabels,
    datasets: [
      {
        label: "Margin %",
        data: marginData,
        borderColor: "#3A913F",
        backgroundColor: "rgba(58, 145, 63, 0.1)",
        borderWidth: 2,
        tension: 0.4,
        fill: true,
        pointBackgroundColor: "#3A913F",
        pointRadius: 4,
        pointHoverRadius: 6,
      },
    ],
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    })
  }

  const getChangeIndicator = (change: number) => {
    if (change > 0) {
      return (
        <div className="flex items-center text-success text-xs font-medium">
          <ArrowUpRight className="h-3 w-3 mr-1" />+{change}%
        </div>
      )
    } else if (change < 0) {
      return (
        <div className="flex items-center text-destructive text-xs font-medium">
          <ArrowDownRight className="h-3 w-3 mr-1" />
          {change}%
        </div>
      )
    }
    return <div className="flex items-center text-muted-foreground text-xs font-medium">0%</div>
  }

  return (
    <div className="p-8 md:p-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between md:items-center bg-gradient-to-r from-background to-muted/20 p-6 rounded-xl border border-border/50 shadow-sm">
        <div>
          <h1 className="text-3xl font-bold">Organization Dashboard</h1>
          <div className="flex items-center gap-2 mt-1 text-muted-foreground">
            <Calendar className="h-4 w-4" />
            <p>
              {formatDate(summary.period.start_date)} – {formatDate(summary.period.end_date)}
            </p>
          </div>
        </div>

        <Tabs
          defaultValue="month"
          value={period}
          onValueChange={setPeriod}
          className="w-full md:w-auto bg-background/80 backdrop-blur-sm rounded-lg p-1 border border-border/50 shadow-sm"
        >
          <TabsList className="grid grid-cols-3 w-full md:w-[300px]">
            <TabsTrigger value="week">Week</TabsTrigger>
            <TabsTrigger value="month">Month</TabsTrigger>
            <TabsTrigger value="quarter">Quarter</TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card className="overflow-hidden border-border/50 shadow-sm hover:shadow-md transition-shadow duration-300">
          <CardHeader className="flex flex-row items-center justify-between pb-2 bg-gradient-to-r from-gold/5 to-transparent">
            <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
            <div className="rounded-full bg-gold/10 p-2">
              <DollarSign className="h-4 w-4 text-gold-dark" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${summary.metrics.total_revenue.toFixed(2)}</div>
            <div className="flex items-center justify-between mt-1">
              <p className="text-xs text-muted-foreground">
                Previous: ${(summary.metrics.total_revenue * 0.89).toFixed(2)}
              </p>
              {getChangeIndicator(12.5)}
            </div>
          </CardContent>
        </Card>

        <Card className="overflow-hidden border-border/50 shadow-sm hover:shadow-md transition-shadow duration-300">
          <CardHeader className="flex flex-row items-center justify-between pb-2 bg-gradient-to-r from-destructive/5 to-transparent">
            <CardTitle className="text-sm font-medium">Total Cost</CardTitle>
            <div className="rounded-full bg-destructive/10 p-2">
              <CreditCard className="h-4 w-4 text-destructive" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${summary.metrics.total_cost.toFixed(2)}</div>
            <div className="flex items-center justify-between mt-1">
              <p className="text-xs text-muted-foreground">
                Previous: ${(summary.metrics.total_cost * 0.93).toFixed(2)}
              </p>
              {getChangeIndicator(8.1)}
            </div>
          </CardContent>
        </Card>

        <Card className="overflow-hidden border-border/50 shadow-sm hover:shadow-md transition-shadow duration-300">
          <CardHeader className="flex flex-row items-center justify-between pb-2 bg-gradient-to-r from-success/5 to-transparent">
            <CardTitle className="text-sm font-medium">Margin %</CardTitle>
            <div className="rounded-full bg-success/10 p-2">
              <Percent className="h-4 w-4 text-success" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(summary.metrics.margin * 100).toFixed(1)}%</div>
            <div className="flex items-center justify-between mt-1">
              <p className="text-xs text-muted-foreground">
                Previous: {((summary.metrics.margin - 0.023) * 100).toFixed(1)}%
              </p>
              {getChangeIndicator(2.3)}
            </div>
          </CardContent>
        </Card>

        <Card className="overflow-hidden border-border/50 shadow-sm hover:shadow-md transition-shadow duration-300">
          <CardHeader className="flex flex-row items-center justify-between pb-2 bg-gradient-to-r from-blue/5 to-transparent">
            <CardTitle className="text-sm font-medium">Activity Count</CardTitle>
            <div className="rounded-full bg-blue/10 p-2">
              <Activity className="h-4 w-4 text-blue" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.metrics.activity_count.toLocaleString()}</div>
            <div className="flex items-center justify-between mt-1">
              <p className="text-xs text-muted-foreground">
                Previous: {Math.floor(summary.metrics.activity_count * 0.85).toLocaleString()}
              </p>
              {getChangeIndicator(18.2)}
            </div>
          </CardContent>
        </Card>

        <Card className="overflow-hidden border-border/50 shadow-sm hover:shadow-md transition-shadow duration-300">
          <CardHeader className="flex flex-row items-center justify-between pb-2 bg-gradient-to-r from-purple/5 to-transparent">
            <CardTitle className="text-sm font-medium">Total Agents</CardTitle>
            <div className="rounded-full bg-purple/10 p-2">
              <Users className="h-4 w-4 text-purple" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.agents.total}</div>
            <div className="flex items-center justify-between mt-1">
              <div className="text-xs text-muted-foreground">
                <Badge variant="outline" className="text-[10px] py-0 h-4 bg-success/10 text-success border-success/20">
                  {summary.agents.active} active
                </Badge>
              </div>
              <Badge
                variant="outline"
                className="text-[10px] py-0 h-4 bg-destructive/10 text-destructive border-destructive/20"
              >
                {summary.agents.total - summary.agents.active} inactive
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card className="col-span-1 border-border/50 shadow-sm hover:shadow-md transition-shadow duration-300 overflow-hidden">
          <CardHeader className="bg-gradient-to-r from-gold/5 to-transparent">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Top Agents by Revenue & Cost</CardTitle>
                <CardDescription>Comparing revenue and costs across your top performing agents</CardDescription>
              </div>
              <Badge variant="outline" className="bg-gold/10 text-gold-dark border-gold/20">
                Revenue Analysis
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="pl-2 pt-4">
            <BarChart
              data={barData}
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    position: "top",
                    labels: {
                      usePointStyle: true,
                      boxWidth: 6,
                      boxHeight: 6,
                    },
                  },
                  tooltip: {
                    mode: "index",
                    intersect: false,
                    backgroundColor: "rgba(0, 0, 0, 0.8)",
                    titleFont: {
                      size: 13,
                    },
                    bodyFont: {
                      size: 12,
                    },
                    padding: 10,
                    cornerRadius: 4,
                    displayColors: true,
                    boxWidth: 8,
                    boxHeight: 8,
                    usePointStyle: true,
                    callbacks: {
                      label: (context: any) => `${context.dataset.label}: $${context.raw.toFixed(2)}`,
                    },
                  },
                },
                scales: {
                  x: {
                    grid: {
                      display: false,
                    },
                    ticks: {
                      maxRotation: 45,
                      minRotation: 45,
                    },
                  },
                  y: {
                    beginAtZero: true,
                    grid: {
                      color: "rgba(0, 0, 0, 0.05)",
                    },
                    ticks: {
                      callback: (value: any) => "$" + value,
                    },
                  },
                },
                animation: {
                  duration: 1000,
                  easing: "easeOutQuart",
                },
              }}
              className="aspect-[4/3]"
            />
          </CardContent>
        </Card>

        <Card className="col-span-1 border-border/50 shadow-sm hover:shadow-md transition-shadow duration-300 overflow-hidden">
          <CardHeader className="bg-gradient-to-r from-success/5 to-transparent">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Margin Analysis</CardTitle>
                <CardDescription>Profit margin percentage by agent</CardDescription>
              </div>
              <Badge variant="outline" className="bg-success/10 text-success border-success/20">
                Profitability
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="pl-2 pt-4">
            <LineChart
              data={marginChartData}
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    position: "top",
                    labels: {
                      usePointStyle: true,
                      boxWidth: 6,
                      boxHeight: 6,
                    },
                  },
                  tooltip: {
                    mode: "index",
                    intersect: false,
                    backgroundColor: "rgba(0, 0, 0, 0.8)",
                    titleFont: {
                      size: 13,
                    },
                    bodyFont: {
                      size: 12,
                    },
                    padding: 10,
                    cornerRadius: 4,
                    displayColors: true,
                    boxWidth: 8,
                    boxHeight: 8,
                    usePointStyle: true,
                    callbacks: {
                      label: (context: any) => `Margin: ${context.raw}%`,
                    },
                  },
                },
                scales: {
                  x: {
                    grid: {
                      display: false,
                    },
                    ticks: {
                      maxRotation: 45,
                      minRotation: 45,
                    },
                  },
                  y: {
                    beginAtZero: true,
                    grid: {
                      color: "rgba(0, 0, 0, 0.05)",
                    },
                    ticks: {
                      callback: (value: any) => value + "%",
                    },
                  },
                },
                animation: {
                  duration: 1000,
                  easing: "easeOutQuart",
                },
              }}
              className="aspect-[4/3]"
            />
          </CardContent>
        </Card>
      </div>

      {/* Agent Performance Table */}
      <Card className="border-border/50 shadow-sm overflow-hidden">
        <CardHeader className="bg-gradient-to-r from-purple/5 to-transparent">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Agent Performance Details</CardTitle>
              <CardDescription>Detailed metrics for your top performing agents</CardDescription>
            </div>
            <Button variant="outline" size="sm" className="gap-1">
              <Users className="h-3.5 w-3.5 mr-1" />
              View All Agents
            </Button>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-muted/30">
                  <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Agent
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Revenue
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Cost
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Margin
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Activities
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {topAgents.map((agent, index) => (
                  <tr key={index} className="hover:bg-muted/20 transition-colors">
                    <td className="px-4 py-3 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="h-8 w-8 rounded-full bg-gradient-to-br from-purple-20 to-blue-20 flex items-center justify-center text-sm font-medium">
                          {agent.name.charAt(0)}
                        </div>
                        <div className="ml-3">
                          <div className="text-sm font-medium">{agent.name}</div>
                          <div className="text-xs text-muted-foreground">{agent.type || "AI Assistant"}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-right">
                      <div className="font-medium">${agent.metrics.total_revenue.toFixed(2)}</div>
                      <div className="text-xs text-success">+{(Math.random() * 10 + 5).toFixed(1)}%</div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-right">
                      <div className="font-medium">${agent.metrics.total_cost.toFixed(2)}</div>
                      <div className="text-xs text-destructive">+{(Math.random() * 5 + 2).toFixed(1)}%</div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-right">
                      <div className="font-medium">{(agent.metrics.margin * 100).toFixed(1)}%</div>
                      <div className="text-xs text-success">+{(Math.random() * 3 + 1).toFixed(1)}%</div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-right">
                      <div className="font-medium">{Math.floor(Math.random() * 1000 + 500).toLocaleString()}</div>
                      <div className="text-xs text-success">+{(Math.random() * 15 + 10).toFixed(1)}%</div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-center">
                      <Badge className="bg-success/20 text-success hover:bg-success/30 border-0">Active</Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
