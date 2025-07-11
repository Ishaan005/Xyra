'use client'

import { memo } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { DollarSign, TrendingUp, Users, Calendar, BarChart3 } from 'lucide-react'
import type { Invoice, InvoiceLineItem } from '../types'

interface InvoiceAnalyticsProps {
  invoices: Invoice[]
}

const InvoiceAnalytics = memo(function InvoiceAnalytics({ invoices }: InvoiceAnalyticsProps) {
  // Calculate analytics data
  const totalRevenue = invoices.reduce((sum, inv) => sum + inv.total_amount, 0)
  const paidInvoices = invoices.filter(inv => inv.status === 'paid')
  const pendingInvoices = invoices.filter(inv => inv.status === 'pending')
  const paidRevenue = paidInvoices.reduce((sum, inv) => sum + inv.total_amount, 0)
  const pendingRevenue = pendingInvoices.reduce((sum, inv) => sum + inv.total_amount, 0)

  // Revenue by billing type
  const billingTypeData = invoices.reduce((acc, invoice) => {
    invoice.line_items?.forEach(item => {
      const type = item.item_type
      if (!acc[type]) {
        acc[type] = { name: type, value: 0, count: 0 }
      }
      acc[type].value += item.amount
      acc[type].count += 1
    })
    return acc
  }, {} as Record<string, { name: string, value: number, count: number }>)

  // Payment method breakdown
  const paymentMethods = paidInvoices.reduce((acc, invoice) => {
    const method = invoice.payment_method || 'Unknown'
    if (!acc[method]) {
      acc[method] = { method, count: 0, amount: 0 }
    }
    acc[method].count += 1
    acc[method].amount += invoice.total_amount
    return acc
  }, {} as Record<string, { method: string, count: number, amount: number }>)

  // Monthly revenue trend (simplified)
  const monthlyData = invoices.reduce((acc, invoice) => {
    const month = new Date(invoice.issue_date).toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short' 
    })
    if (!acc[month]) {
      acc[month] = { month, revenue: 0, count: 0 }
    }
    acc[month].revenue += invoice.total_amount
    acc[month].count += 1
    return acc
  }, {} as Record<string, { month: string, revenue: number, count: number }>)

  const avgInvoiceAmount = invoices.length > 0 ? totalRevenue / invoices.length : 0
  const collectionRate = invoices.length > 0 ? (paidInvoices.length / invoices.length) * 100 : 0

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <DollarSign className="w-4 h-4 text-green-600" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Revenue</p>
                <p className="text-2xl font-bold">${totalRevenue.toFixed(2)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <TrendingUp className="w-4 h-4 text-blue-600" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">Avg Invoice</p>
                <p className="text-2xl font-bold">${avgInvoiceAmount.toFixed(2)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <Calendar className="w-4 h-4 text-purple-600" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">Collection Rate</p>
                <p className="text-2xl font-bold">{collectionRate.toFixed(1)}%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <Users className="w-4 h-4 text-orange-600" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">Pending Revenue</p>
                <p className="text-2xl font-bold text-orange-600">${pendingRevenue.toFixed(2)}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Monthly Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <BarChart3 className="w-5 h-5" />
            <span>Monthly Revenue</span>
          </CardTitle>
          <CardDescription>Revenue breakdown by month</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {Object.values(monthlyData)
              .sort((a, b) => new Date(b.month).getTime() - new Date(a.month).getTime())
              .slice(0, 6)
              .map((data) => (
                <div key={data.month} className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <p className="font-medium">{data.month}</p>
                    <p className="text-sm text-muted-foreground">{data.count} invoices</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold">${data.revenue.toFixed(2)}</p>
                    <div className="w-24 bg-gray-200 rounded-full h-2 mt-1">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ 
                          width: `${Math.min((data.revenue / Math.max(...Object.values(monthlyData).map(d => d.revenue))) * 100, 100)}%` 
                        }}
                      />
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </CardContent>
      </Card>

      {/* Billing Model Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Billing Model Performance</CardTitle>
          <CardDescription>Detailed breakdown by billing type</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Object.entries(billingTypeData).map(([type, data]) => (
              <div key={type} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-3">
                  <Badge variant="outline" className="capitalize">
                    {type}
                  </Badge>
                  <div>
                    <p className="font-medium capitalize">{type} Billing</p>
                    <p className="text-sm text-muted-foreground">{data.count} line items</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-bold">${data.value.toFixed(2)}</p>
                  <p className="text-sm text-muted-foreground">
                    {totalRevenue > 0 ? ((data.value / totalRevenue) * 100).toFixed(1) : '0'}% of total
                  </p>
                  <div className="w-16 bg-gray-200 rounded-full h-2 mt-1">
                    <div 
                      className="bg-green-600 h-2 rounded-full" 
                      style={{ 
                        width: `${totalRevenue > 0 ? (data.value / totalRevenue) * 100 : 0}%` 
                      }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Payment Methods */}
      {Object.keys(paymentMethods).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Payment Methods</CardTitle>
            <CardDescription>How customers are paying</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.values(paymentMethods).map((method) => (
                <div key={method.method} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center space-x-2">
                    <Badge variant="secondary">{method.method}</Badge>
                    <span className="text-sm text-muted-foreground">
                      {method.count} invoices
                    </span>
                  </div>
                  <span className="font-medium">${method.amount.toFixed(2)}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
})

export default InvoiceAnalytics
