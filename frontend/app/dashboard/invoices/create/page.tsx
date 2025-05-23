"use client"

import { useState, useEffect } from "react"
import { useSession } from "next-auth/react"
import { useRouter } from "next/navigation"
import { setAuthToken } from "../../../../utils/api"
import api from "../../../../utils/api"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from "@/components/ui/table"
import { ArrowLeft, Plus, Trash2, Save } from "lucide-react"
import { format } from "date-fns"

interface LineItem {
  id?: number;
  description: string;
  quantity: number;
  unit_price: number;
  amount: number;
  item_type: string;
  reference_id?: number | null;
  reference_type?: string | null;
  item_metadata?: any;
}

interface CreateInvoiceForm {
  organization_id: number;
  due_date: string;
  notes: string;
  items: LineItem[];
  currency: string;
}

export default function CreateInvoicePage() {
  const router = useRouter()
  const { data: session, status } = useSession()
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  
  // Get today's date in YYYY-MM-DD format
  const today = new Date().toISOString().split('T')[0]
  // Set default due date as 30 days from now
  const thirtyDaysFromNow = new Date()
  thirtyDaysFromNow.setDate(thirtyDaysFromNow.getDate() + 30)
  const defaultDueDate = thirtyDaysFromNow.toISOString().split('T')[0]
  
  const [form, setForm] = useState<CreateInvoiceForm>({
    organization_id: 1, // TODO: Get from context
    due_date: defaultDueDate,
    notes: "",
    items: [
      {
        description: "",
        quantity: 1,
        unit_price: 0,
        amount: 0,
        item_type: "service"
      }
    ],
    currency: "USD"
  })

  useEffect(() => {
    if (status === "loading") return
    if (status === "unauthenticated") return router.push("/login")
    if (status === "authenticated" && session?.user?.accessToken) {
      setAuthToken(session.user.accessToken)
      setLoading(false)
    }
  }, [status, session, router])

  const updateLineItem = (index: number, field: keyof LineItem, value: any) => {
    const updatedItems = [...form.items]
    updatedItems[index] = {
      ...updatedItems[index],
      [field]: value
    }
    
    // Recalculate amount if quantity or unit_price changed
    if (field === 'quantity' || field === 'unit_price') {
      updatedItems[index].amount = 
        Number(updatedItems[index].quantity) * Number(updatedItems[index].unit_price)
    }
    
    setForm({ ...form, items: updatedItems })
  }

  const addLineItem = () => {
    setForm({
      ...form,
      items: [
        ...form.items,
        {
          description: "",
          quantity: 1,
          unit_price: 0,
          amount: 0,
          item_type: "service"
        }
      ]
    })
  }

  const removeLineItem = (index: number) => {
    if (form.items.length > 1) {
      const updatedItems = [...form.items]
      updatedItems.splice(index, 1)
      setForm({ ...form, items: updatedItems })
    }
  }

  const calculateTotal = () => {
    return form.items.reduce((sum, item) => sum + item.amount, 0)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validate form
    if (!form.due_date) {
      setError("Due date is required")
      return
    }
    
    if (form.items.some(item => !item.description || item.amount <= 0)) {
      setError("All line items must have a description and valid amount")
      return
    }
    
    try {
      setSubmitting(true)
      setError(null)
      
      const response = await api.post('/invoices/', form)
      
      setSuccess(true)
      // Redirect to the newly created invoice after a short delay
      setTimeout(() => {
        router.push(`/dashboard/invoices/${response.data.id}`)
      }, 1500)
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || "Failed to create invoice"
      setError(errorMsg)
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <div className="p-8">Loading...</div>

  return (
    <div className="p-8">
      <Button 
        variant="ghost" 
        onClick={() => router.back()}
        className="mb-6"
      >
        <ArrowLeft className="h-4 w-4 mr-2" /> Back to Invoices
      </Button>
      
      <Card>
        <form onSubmit={handleSubmit}>
          <CardHeader>
            <CardTitle>Create New Invoice</CardTitle>
            <CardDescription>
              Create a new invoice to send to your customer
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Basic Invoice Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="due_date">Due Date</Label>
                <Input 
                  id="due_date" 
                  type="date" 
                  value={form.due_date}
                  min={today}
                  onChange={(e) => setForm({ ...form, due_date: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="currency">Currency</Label>
                <select 
                  id="currency"
                  className="w-full border border-gray-300 rounded-md h-10 px-3"
                  value={form.currency}
                  onChange={(e) => setForm({ ...form, currency: e.target.value })}
                >
                  <option value="USD">USD - US Dollar</option>
                  <option value="EUR">EUR - Euro</option>
                  <option value="GBP">GBP - British Pound</option>
                  <option value="CAD">CAD - Canadian Dollar</option>
                  <option value="AUD">AUD - Australian Dollar</option>
                  <option value="JPY">JPY - Japanese Yen</option>
                </select>
              </div>
            </div>
            
            {/* Line Items */}
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium">Line Items</h3>
                <Button 
                  type="button" 
                  variant="outline"
                  onClick={addLineItem}
                  className="h-8"
                >
                  <Plus className="h-4 w-4 mr-1" /> Add Item
                </Button>
              </div>
              
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[40%]">Description</TableHead>
                    <TableHead className="w-[15%]">Quantity</TableHead>
                    <TableHead className="w-[15%]">Price</TableHead>
                    <TableHead className="w-[15%]">Amount</TableHead>
                    <TableHead className="w-[15%]"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {form.items.map((item, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <Input 
                          placeholder="Item description"
                          value={item.description}
                          onChange={(e) => updateLineItem(index, 'description', e.target.value)}
                        />
                      </TableCell>
                      <TableCell>
                        <Input 
                          type="number"
                          min="0.01"
                          step="0.01"
                          value={item.quantity}
                          onChange={(e) => updateLineItem(index, 'quantity', Number(e.target.value))}
                        />
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center">
                          <span className="mr-1">{form.currency}</span>
                          <Input 
                            type="number"
                            min="0.01"
                            step="0.01"
                            value={item.unit_price}
                            onChange={(e) => updateLineItem(index, 'unit_price', Number(e.target.value))}
                          />
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center">
                          <span className="mr-1">{form.currency}</span>
                          <Input 
                            type="number"
                            readOnly
                            value={item.amount.toFixed(2)}
                          />
                        </div>
                      </TableCell>
                      <TableCell>
                        <Button 
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => removeLineItem(index)}
                          disabled={form.items.length === 1}
                          className="h-8 w-8 p-0"
                        >
                          <Trash2 className="h-4 w-4 text-red-500" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                  <TableRow>
                    <TableCell colSpan={3} className="text-right font-bold">
                      Total:
                    </TableCell>
                    <TableCell className="font-bold">
                      {form.currency} {calculateTotal().toFixed(2)}
                    </TableCell>
                    <TableCell></TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
            
            {/* Notes */}
            <div className="space-y-2">
              <Label htmlFor="notes">Notes (Optional)</Label>
              <Textarea 
                id="notes"
                placeholder="Add any additional information for your customer..."
                value={form.notes}
                onChange={(e) => setForm({ ...form, notes: e.target.value })}
                rows={3}
              />
            </div>
            
            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}
            
            {/* Success Message */}
            {success && (
              <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
                Invoice created successfully! Redirecting to invoice page...
              </div>
            )}
          </CardContent>
          <CardFooter className="justify-between">
            <Button 
              type="button" 
              variant="outline" 
              onClick={() => router.push('/dashboard/invoices')}
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={submitting}
              className="gap-2"
            >
              {submitting ? (
                <>
                  <span className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full"></span>
                  <span>Creating...</span>
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-1" />
                  Create Invoice
                </>
              )}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  )
}
