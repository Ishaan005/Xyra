'use client'

import { memo } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { AlertCircle } from 'lucide-react'

interface ErrorAlertProps {
  error: string
}

const ErrorAlert = memo(function ErrorAlert({ error }: ErrorAlertProps) {
  if (!error) return null

  return (
    <Card className="border-red-200 bg-red-50">
      <CardContent className="pt-6">
        <div className="flex items-center space-x-2 text-red-600">
          <AlertCircle className="w-4 h-4" />
          <span>{error}</span>
        </div>
      </CardContent>
    </Card>
  )
})

export default ErrorAlert
