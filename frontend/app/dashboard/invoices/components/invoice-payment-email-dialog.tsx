"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea" 
import { CheckCircle, Copy, Mail, AlertCircle, Download } from "lucide-react"
import api from "../../../../utils/api"
import { invoiceApi } from "../../../../utils/invoice-api"

interface InvoicePaymentEmailDialogProps {
  isOpen: boolean;
  onClose: () => void;
  invoiceNumber: string;
  recipientEmail?: string;
  paymentLink?: string;
  pdfUrl?: string;
  defaultMessage?: string;
  enableBulkSend?: boolean;
}

export default function InvoicePaymentEmailDialog({
  isOpen,
  onClose,
  invoiceNumber,
  recipientEmail,
  paymentLink,
  pdfUrl,
  defaultMessage,
  enableBulkSend = false
}: InvoicePaymentEmailDialogProps) {
  const [email, setEmail] = useState(recipientEmail || "")
  const [bulkEmails, setBulkEmails] = useState<string[]>([])
  const [customMessage, setCustomMessage] = useState(defaultMessage || "")
  const [isSending, setIsSending] = useState(false)
  const [isSent, setIsSent] = useState(false)
  const [error, setError] = useState("")
  const [isCopied, setIsCopied] = useState(false)
  const [bulkModeActive, setBulkModeActive] = useState(false)
  const [personalize, setPersonalize] = useState(false)
  // Reset dialog state when it's opened/closed
  useEffect(() => {
    if (!isOpen) {
      setIsSent(false)
      setError("")
      // Don't reset email in case the dialog is reopened
    } else {
      // When dialog opens, set the email if provided
      if (recipientEmail) {
        setEmail(recipientEmail)
      }
      // Reset custom message when dialog opens
      setCustomMessage(defaultMessage || "")
    }
  }, [isOpen, recipientEmail, defaultMessage])
  // Auto-hide copy confirmation after 2 seconds
  useEffect(() => {
    if (isCopied) {
      const timer = setTimeout(() => {
        setIsCopied(false)
      }, 2000)
      return () => clearTimeout(timer)
    }
  }, [isCopied])
    // Simple email validation function
  const isValidEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }
  
  const sendEmail = async () => {
    if (!email.trim()) {
      setError("Please provide an email address")
      return
    }
    
    if (!isValidEmail(email.trim())) {
      setError("Please provide a valid email address")
      return
    }
    
    if (!invoiceNumber) {
      setError("Invoice number is required")
      return
    }
      try {
      setIsSending(true)
      setError("")
      
      // Call backend API to send invoice email using our invoice-api utility
      await invoiceApi.sendInvoiceEmail(
        invoiceNumber, 
        email, 
        {
          paymentLink: paymentLink || undefined,
          includePdf: !!pdfUrl,
          message: customMessage || undefined
        }
      )
      
      setIsSent(true)
    } catch (err: any) {      // Handle different error cases with appropriate messages
      const errorMsg = err.response?.data?.detail || err.message || "Failed to send email. Please try again."
      
      if (err.response?.status === 404) {
        setError("Invoice not found. Please check the invoice number.")
      } else if (err.response?.status === 403) {
        setError("You don't have permission to send this invoice.")
      } else if (err.response?.status === 503) {
        setError("Email service is not configured. Please contact the administrator.")
      } else if (err.response?.status === 500 && errorMsg.includes("email")) {
        setError("Email service error. Please check email configuration or try again later.")
      } else if (err.response?.status === 400) {
        setError(`Invalid request: ${errorMsg}`)
      } else {
        setError(errorMsg)
      }
    } finally {
      setIsSending(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    setIsCopied(true)
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        {isCopied && (
          <div className="absolute top-2 right-2 bg-green-50 text-green-700 p-2 rounded text-xs flex items-center">
            <CheckCircle className="h-3 w-3 mr-1" />
            Copied!
          </div>
        )}
        <DialogHeader>
          <DialogTitle>Share Invoice {invoiceNumber}</DialogTitle>
          <DialogDescription>
            Send this invoice to your customer via email or share the payment link directly.
          </DialogDescription>
        </DialogHeader>

        {!isSent ? (          <>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="email">Email address</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="customer@example.com"
                  value={email}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="message">Message (optional)</Label>
                <Textarea
                  id="message"
                  placeholder="Add a personal message to include with this invoice..."
                  value={customMessage}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setCustomMessage(e.target.value)}
                  className="min-h-[80px]"
                />
              </div>

              {paymentLink && (
                <div className="grid gap-2">
                  <Label>Payment Link</Label>
                  <div className="flex items-center space-x-2">
                    <Input value={paymentLink} readOnly className="bg-muted/30" />
                    <Button
                      size="icon"
                      variant="outline"
                      onClick={() => copyToClipboard(paymentLink)}
                      title="Copy payment link"
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              )}

              {pdfUrl && (
                <div className="flex items-center gap-2 mt-2 p-2 bg-blue-50 rounded-md border border-blue-100 text-sm">
                  <div className="rounded-full bg-blue-100 p-1.5">
                    <Download className="h-3.5 w-3.5 text-blue-700" />
                  </div>
                  <p className="text-blue-800">The invoice PDF will be attached to the email.</p>
                </div>
              )}

              {error && (
                <div className="flex items-start gap-2 mt-2 p-2 bg-red-50 rounded-md border border-red-100 text-sm">
                  <AlertCircle className="h-4 w-4 text-red-500 mt-0.5" />
                  <p className="text-red-800">{error}</p>
                </div>
              )}
            </div>

            <DialogFooter className="sm:justify-between">
              <Button variant="outline" onClick={onClose}>
                Cancel
              </Button>
              <Button onClick={sendEmail} disabled={!email || isSending} className="gap-2">
                {isSending ? (
                  <>
                    <span className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full"></span>
                    <span>Sending...</span>
                  </>
                ) : (
                  <>
                    <Mail className="h-4 w-4" /> 
                    <span>Send Email</span>
                  </>
                )}
              </Button>
            </DialogFooter>
          </>        ) : (
          <div className="py-6 flex flex-col items-center justify-center">
            <div className="rounded-full bg-green-100 p-4 mb-4">
              <CheckCircle className="h-10 w-10 text-green-600" />
            </div>
            <h3 className="text-xl font-medium">Invoice Sent!</h3>
            <p className="text-center text-muted-foreground mt-2 mb-2">
              Invoice #{invoiceNumber} has been sent to {email}
            </p>
            
            {paymentLink && (
              <div className="mt-4 p-3 bg-blue-50 rounded-md border border-blue-100 text-sm max-w-xs text-center">
                <p className="text-blue-800 mb-2">Recipients can pay directly through the secure payment link included in the email.</p>
              </div>
            )}
            
            <Button onClick={onClose} className="mt-6">
              Close
            </Button>
          </div>
        )}

      </DialogContent>
    </Dialog>
  )
}
