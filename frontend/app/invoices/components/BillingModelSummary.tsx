'use client'

import React, { memo } from 'react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Activity, Target, Users, Workflow } from 'lucide-react'

interface BillingModelSummaryProps {
  lineItems?: Array<{
    item_type: string
    amount: number
    item_metadata?: {
      billing_model_id?: number
      outcome_type?: string
      activity_type?: string
      agent_tier?: string
      workflow_type?: string
    }
  }>
}

const BillingModelSummary = memo(function BillingModelSummary({ lineItems = [] }: BillingModelSummaryProps) {
  // Group line items by billing model type
  const modelSummary = lineItems.reduce((acc, item) => {
    const type = item.item_type
    if (!acc[type]) {
      acc[type] = {
        type,
        count: 0,
        totalAmount: 0,
        icon: getTypeIcon(type),
        color: getTypeColor(type),
        details: new Set()
      }
    }
    acc[type].count += 1
    acc[type].totalAmount += item.amount
    
    // Add specific details based on type
    if (item.item_metadata?.outcome_type) {
      acc[type].details.add(`Outcome: ${item.item_metadata.outcome_type}`)
    }
    if (item.item_metadata?.activity_type) {
      acc[type].details.add(`Activity: ${item.item_metadata.activity_type}`)
    }
    if (item.item_metadata?.agent_tier) {
      acc[type].details.add(`Tier: ${item.item_metadata.agent_tier}`)
    }
    if (item.item_metadata?.workflow_type) {
      acc[type].details.add(`Workflow: ${item.item_metadata.workflow_type}`)
    }
    
    return acc
  }, {} as Record<string, {
    type: string
    count: number
    totalAmount: number
    icon: React.ReactNode
    color: string
    details: Set<string>
  }>)

  function getTypeIcon(type: string) {
    switch (type) {
      case 'subscription':
        return <Users className="w-4 h-4" />
      case 'usage':
        return <Activity className="w-4 h-4" />
      case 'outcome':
        return <Target className="w-4 h-4" />
      case 'workflow':
        return <Workflow className="w-4 h-4" />
      default:
        return <Activity className="w-4 h-4" />
    }
  }

  function getTypeColor(type: string) {
    switch (type) {
      case 'subscription':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'usage':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'outcome':
        return 'bg-purple-100 text-purple-800 border-purple-200'
      case 'workflow':
        return 'bg-orange-100 text-orange-800 border-orange-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  if (Object.keys(modelSummary).length === 0) {
    return null
  }

  return (
    <Card className="h-fit">
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Billing Model Summary</CardTitle>
        <CardDescription>Breakdown by billing model type</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {Object.values(modelSummary).map((model) => (
          <div 
            key={model.type} 
            className={`p-3 rounded-lg border ${model.color} transition-all hover:shadow-sm`}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                {model.icon}
                <span className="font-medium capitalize text-sm">{model.type}</span>
                <Badge variant="secondary" className="text-xs">
                  {model.count}
                </Badge>
              </div>
              <span className="font-bold text-sm">${model.totalAmount.toFixed(2)}</span>
            </div>
            
            {model.details.size > 0 && (
              <div className="text-xs space-y-1 max-h-20 overflow-y-auto">
                {Array.from(model.details).slice(0, 4).map((detail, index) => (
                  <div key={index} className="opacity-75 truncate" title={detail}>
                    {detail}
                  </div>
                ))}
                {model.details.size > 4 && (
                  <div className="opacity-75 font-medium">+{model.details.size - 4} more details</div>
                )}
              </div>
            )}
          </div>
        ))}
      </CardContent>
    </Card>
  )
})

export default BillingModelSummary
