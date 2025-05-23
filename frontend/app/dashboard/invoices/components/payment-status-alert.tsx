"use client"

import { useEffect, useState } from "react"
import { AlertTriangle, CheckCircle } from "lucide-react"
import { useSearchParams } from "next/navigation"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

export default function PaymentStatusAlert() {
  const searchParams = useSearchParams()
  const paymentStatus = searchParams.get("payment_status")
  const [visible, setVisible] = useState(!!paymentStatus)
  
  // Hide the alert after 10 seconds
  useEffect(() => {
    if (paymentStatus) {
      const timer = setTimeout(() => {
        setVisible(false)
      }, 10000)
      
      return () => clearTimeout(timer)
    }
  }, [paymentStatus])
  
  if (!visible) return null
  
  if (paymentStatus === "success") {
    return (
      <Alert variant="default" className="bg-green-50 border-green-200 text-green-800 mb-6">
        <CheckCircle className="h-4 w-4 text-green-600" />
        <AlertTitle>Payment Successful</AlertTitle>
        <AlertDescription>
          Your payment has been processed successfully. Thank you for your payment!
        </AlertDescription>
      </Alert>
    )
  }
  
  if (paymentStatus === "cancelled") {
    return (
      <Alert variant="default" className="bg-amber-50 border-amber-200 text-amber-800 mb-6">
        <AlertTriangle className="h-4 w-4 text-amber-600" />
        <AlertTitle>Payment Cancelled</AlertTitle>
        <AlertDescription>
          Your payment process was cancelled. If you need assistance, please contact support.
        </AlertDescription>
      </Alert>
    )
  }
  
  return null
}
