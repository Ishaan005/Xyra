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
  const orgId = 1 //TODO: obtain dynamically

  useEffect(() => {
    if (status === "loading") return
    if (status === "unauthenticated") return router.push("/login")
    if (status === "authenticated" && session?.user?.accessToken) setAuthToken(session.user.accessToken)
  }, [status, session, router])

  const [summary, setSummary] = useState<any>(null)
  const [previousSummary, setPreviousSummary] = useState<any>(null)
  const [topAgents, setTopAgents] = useState<any[]>([])
  const [previousTopAgents, setPreviousTopAgents] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [period, setPeriod] = useState("month")

  // Calculate date ranges for current and previous periods
  const getDateRanges = (period: string) => {
    const now = new Date()
    let currentStart: Date, currentEnd: Date, previousStart: Date, previousEnd: Date

    switch (period) {
      case "week":
        currentEnd = now
        currentStart = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
        previousEnd = new Date(currentStart.getTime() - 1000) // 1ms before current start
        previousStart = new Date(previousEnd.getTime() - 7 * 24 * 60 * 60 * 1000)
        break
      case "quarter":
        currentEnd = now
        currentStart = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000)
        previousEnd = new Date(currentStart.getTime() - 1000)
        previousStart = new Date(previousEnd.getTime() - 90 * 24 * 60 * 60 * 1000)
        break
      default: // month
        currentEnd = now
        currentStart = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
        previousEnd = new Date(currentStart.getTime() - 1000)
        previousStart = new Date(previousEnd.getTime() - 30 * 24 * 60 * 60 * 1000)
        break
    }

    return {
      current: { start: currentStart, end: currentEnd },
      previous: { start: previousStart, end: previousEnd }
    }
  }

  // Fetch analytics after authentication
  useEffect(() => {
    if (status !== 'authenticated') return
    const token = session.user.accessToken ?? ""
    setAuthToken(token)
    setLoading(true)
    
    const dateRanges = getDateRanges(period)
    
    Promise.all([
      api.get(`/analytics/organization/${orgId}/summary`, {
        params: {
          start_date: dateRanges.current.start.toISOString(),
          end_date: dateRanges.current.end.toISOString()
        }
      }),
      api.get(`/analytics/organization/${orgId}/summary`, {
        params: {
          start_date: dateRanges.previous.start.toISOString(),
          end_date: dateRanges.previous.end.toISOString()
        }
      }),
      api.get(`/analytics/organization/${orgId}/top-agents?limit=5`, {
        params: {
          start_date: dateRanges.current.start.toISOString(),
          end_date: dateRanges.current.end.toISOString()
        }
      }),
      api.get(`/analytics/organization/${orgId}/top-agents?limit=5`, {
        params: {
          start_date: dateRanges.previous.start.toISOString(),
          end_date: dateRanges.previous.end.toISOString()
        }
      }),
    ])
      .then(([sumRes, prevSumRes, topRes, prevTopRes]) => {
        setSummary(sumRes.data)
        setPreviousSummary(prevSumRes.data)
        setTopAgents(topRes.data)
        setPreviousTopAgents(prevTopRes.data)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [status, session, period])

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

  if (error || !summary) {
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

  const calculatePercentageChange = (current: number, previous: number): number => {
    if (previous === 0) return current > 0 ? 100 : 0
    return ((current - previous) / previous) * 100
  }

  const getPreviousAgentData = (agentId: number, metric: string) => {
    const previousAgent = previousTopAgents.find(agent => agent.agent_id === agentId)
    if (!previousAgent) return null
    
    switch (metric) {
      case 'revenue':
        return previousAgent.metrics.total_revenue
      case 'cost':
        return previousAgent.metrics.total_cost
      case 'margin':
        return previousAgent.metrics.margin
      case 'activity':
        return previousAgent.metrics.activity_count
      default:
        return null
    }
  }

  const getAgentChangeIndicator = (agentId: number, currentValue: number, metric: string) => {
    const previousValue = getPreviousAgentData(agentId, metric)
    if (previousValue === null) {
      return <div className="text-xs text-muted-foreground">No prev. data</div>
    }
    
    const change = calculatePercentageChange(currentValue, previousValue)
    if (change > 0) {
      return <div className="text-xs text-success">+{change.toFixed(1)}%</div>
    } else if (change < 0) {
      return <div className="text-xs text-destructive">{change.toFixed(1)}%</div>
    }
    return <div className="text-xs text-muted-foreground">0%</div>
  }

  const getChangeIndicator = (change: number) => {
    if (change > 0) {
      return (
        <div className="flex items-center text-success text-xs font-medium">
          <ArrowUpRight className="h-3 w-3 mr-1" />+{change.toFixed(1)}%
        </div>
      )
    } else if (change < 0) {
      return (
        <div className="flex items-center text-destructive text-xs font-medium">
          <ArrowDownRight className="h-3 w-3 mr-1" />
          {change.toFixed(1)}%
        </div>
      )
    }
    return <div className="flex items-center text-muted-foreground text-xs font-medium">0%</div>
  }

  return (
    <div className="p-8 md:p-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between md:items-center bg-gradient-to-r from-background to-muted/20 p-6 rounded-xl border border-border/10 shadow-sm ring-1 ring-border/5 backdrop-blur-sm">
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
          className="w-full md:w-auto bg-background/80 backdrop-blur-sm rounded-lg p-1 border border-border/8 shadow-sm ring-1 ring-border/5"
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
        <Card className="overflow-hidden border-border/8 shadow-sm hover:shadow-md hover:border-border/15 transition-all duration-300 ring-1 ring-border/5 hover:ring-border/10">
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
                Previous: ${previousSummary ? previousSummary.metrics.total_revenue.toFixed(2) : '0.00'}
              </p>
              {getChangeIndicator(
                previousSummary 
                  ? calculatePercentageChange(summary.metrics.total_revenue, previousSummary.metrics.total_revenue)
                  : 0
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="overflow-hidden border-border/8 shadow-sm hover:shadow-md hover:border-border/15 transition-all duration-300 ring-1 ring-border/5 hover:ring-border/10">
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
                Previous: ${previousSummary ? previousSummary.metrics.total_cost.toFixed(2) : '0.00'}
              </p>
              {getChangeIndicator(
                previousSummary 
                  ? calculatePercentageChange(summary.metrics.total_cost, previousSummary.metrics.total_cost)
                  : 0
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="overflow-hidden border-border/8 shadow-sm hover:shadow-md hover:border-border/15 transition-all duration-300 ring-1 ring-border/5 hover:ring-border/10">
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
                Previous: {previousSummary ? (previousSummary.metrics.margin * 100).toFixed(1) : '0.0'}%
              </p>
              {getChangeIndicator(
                previousSummary 
                  ? calculatePercentageChange(summary.metrics.margin * 100, previousSummary.metrics.margin * 100)
                  : 0
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="overflow-hidden border-border/8 shadow-sm hover:shadow-md hover:border-border/15 transition-all duration-300 ring-1 ring-border/5 hover:ring-border/10">
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
                Previous: {previousSummary ? previousSummary.metrics.activity_count.toLocaleString() : '0'}
              </p>
              {getChangeIndicator(
                previousSummary 
                  ? calculatePercentageChange(summary.metrics.activity_count, previousSummary.metrics.activity_count)
                  : 0
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="overflow-hidden border-border/8 shadow-sm hover:shadow-md hover:border-border/15 transition-all duration-300 ring-1 ring-border/5 hover:ring-border/10">
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
                <Badge variant="outline" className="text-[10px] py-0 h-4 bg-success/10 text-success border-success/8">
                  {summary.agents.active} active
                </Badge>
              </div>
              <Badge
                variant="outline"
                className="text-[10px] py-0 h-4 bg-destructive/10 text-destructive border-destructive/8"
              >
                {summary.agents.total - summary.agents.active} inactive
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card className="col-span-1 border-border/8 shadow-sm hover:shadow-md hover:border-border/15 transition-all duration-300 overflow-hidden ring-1 ring-border/5 hover:ring-border/10">
          <CardHeader className="bg-gradient-to-r from-gold/5 to-transparent">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Top Agents by Revenue & Cost</CardTitle>
                <CardDescription>Comparing revenue and costs across your top performing agents</CardDescription>
              </div>
              <Badge variant="outline" className="bg-gold/10 text-gold-dark border-gold/15">
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

        <Card className="col-span-1 border-border/8 shadow-sm hover:shadow-md hover:border-border/15 transition-all duration-300 overflow-hidden ring-1 ring-border/5 hover:ring-border/10">
          <CardHeader className="bg-gradient-to-r from-success/5 to-transparent">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Margin Analysis</CardTitle>
                <CardDescription>Profit margin percentage by agent</CardDescription>
              </div>
              <Badge variant="outline" className="bg-success/10 text-success border-success/15">
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
      <Card className="border-border/8 shadow-sm hover:shadow-md hover:border-border/15 transition-all duration-300 overflow-hidden ring-1 ring-border/5 hover:ring-border/10">
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
              <tbody className="divide-y divide-border/20">
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
                      {getAgentChangeIndicator(agent.agent_id, agent.metrics.total_revenue, 'revenue')}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-right">
                      <div className="font-medium">${agent.metrics.total_cost.toFixed(2)}</div>
                      {getAgentChangeIndicator(agent.agent_id, agent.metrics.total_cost, 'cost')}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-right">
                      <div className="font-medium">{(agent.metrics.margin * 100).toFixed(1)}%</div>
                      {getAgentChangeIndicator(agent.agent_id, agent.metrics.margin, 'margin')}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-right">
                      <div className="font-medium">{agent.metrics.activity_count.toLocaleString()}</div>
                      {getAgentChangeIndicator(agent.agent_id, agent.metrics.activity_count, 'activity')}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-center">
                      <Badge className={agent.is_active ? "bg-success/20 text-success hover:bg-success/25 border-0" : "bg-destructive/20 text-destructive hover:bg-destructive/25 border-0"}>
                        {agent.is_active ? "Active" : "Inactive"}
                      </Badge>
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
