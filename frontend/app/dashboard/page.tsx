"use client"

import { useState, useEffect } from "react"
import { setAuthToken } from "@/utils/api"
import api from "@/utils/api"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { BarChart, LineChart } from "@/components/ui/chart"
import { Activity, CreditCard, DollarSign, Users, TrendingUp, TrendingDown, Percent } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"

export default function DashboardPage() {
  const orgId = 1 // TODO: obtain dynamically
  const [summary, setSummary] = useState<any>(null)
  const [topAgents, setTopAgents] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [period, setPeriod] = useState("month")

  useEffect(() => {
    // Load token from localStorage if present
    const token = localStorage.getItem("token")
    if (token) setAuthToken(token)

    Promise.all([
      api.get(`/analytics/organization/${orgId}/summary`),
      api.get(`/analytics/organization/${orgId}/top-agents?limit=5`), //TODO: add limit filter
    ])
      .then(([sumRes, topRes]) => {
        setSummary(sumRes.data)
        setTopAgents(topRes.data)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

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
        <p className="text-gray-dark mb-4">{error}</p>
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
        backgroundColor: "#FFB500",
        borderColor: "#AF6D04",
        borderWidth: 1,
      },
      {
        label: "Cost",
        data: costData,
        backgroundColor: "#B83C27",
        borderColor: "#8A2A1D",
        borderWidth: 1,
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

  return (
    <div className="p-4 md:p-8 space-y-8 max-w-[1400px]">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold">Organization Dashboard</h1>
          <p className="text-gray-dark">
            {formatDate(summary.period.start_date)} – {formatDate(summary.period.end_date)}
          </p>
        </div>

        <Tabs defaultValue="month" value={period} onValueChange={setPeriod} className="w-full md:w-auto">
          <TabsList className="grid grid-cols-3 w-full md:w-[300px]">
            <TabsTrigger value="week">Week</TabsTrigger>
            <TabsTrigger value="month">Month</TabsTrigger>
            <TabsTrigger value="quarter">Quarter</TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-gold-dark" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${summary.metrics.total_revenue.toFixed(2)}</div>
            <p className="text-xs text-gray-dark">+12.5% from previous period</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Cost</CardTitle>
            <CreditCard className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${summary.metrics.total_cost.toFixed(2)}</div>
            <p className="text-xs text-gray-dark">+8.1% from previous period</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Margin %</CardTitle>
            <Percent className="h-4 w-4 text-success" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(summary.metrics.margin * 100).toFixed(1)}%</div>
            <p className="text-xs text-gray-dark">+2.3% from previous period</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Activity Count</CardTitle>
            <Activity className="h-4 w-4 text-blue" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.metrics.activity_count.toLocaleString()}</div>
            <p className="text-xs text-gray-dark">+18.2% from previous period</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Agents</CardTitle>
            <Users className="h-4 w-4 text-purple" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.agents.total}</div>
            <p className="text-xs text-gray-dark">{summary.agents.active} active</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Growth Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-teal" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">+15.4%</div>
            <p className="text-xs text-gray-dark">Month over month</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Top Agents by Revenue & Cost</CardTitle>
            <CardDescription>Comparing revenue and costs across your top performing agents</CardDescription>
          </CardHeader>
          <CardContent className="pl-2">
            <BarChart
              data={barData}
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    position: "top",
                  },
                  tooltip: {
                    mode: "index",
                    intersect: false,
                  },
                },
                scales: {
                  x: {
                    grid: {
                      display: false,
                    },
                  },
                  y: {
                    beginAtZero: true,
                    grid: {
                      color: "rgba(0, 0, 0, 0.05)",
                    },
                  },
                },
              }}
              className="aspect-[4/3]"
            />
          </CardContent>
        </Card>

        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Margin Analysis</CardTitle>
            <CardDescription>Profit margin percentage by agent</CardDescription>
          </CardHeader>
          <CardContent className="pl-2">
            <LineChart
              data={marginChartData}
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    position: "top",
                  },
                  tooltip: {
                    mode: "index",
                    intersect: false,
                  },
                },
                scales: {
                  x: {
                    grid: {
                      display: false,
                    },
                  },
                  y: {
                    beginAtZero: true,
                    grid: {
                      color: "rgba(0, 0, 0, 0.05)",
                    },
                    ticks: {
                      callback: (value: string) => value + "%",
                    },
                  },
                },
              }}
              className="aspect-[4/3]"
            />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
