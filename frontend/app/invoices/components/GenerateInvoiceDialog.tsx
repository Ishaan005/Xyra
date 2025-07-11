'use client'

import { useState, memo } from 'react'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import type { GenerateInvoiceForm } from '../types'

interface GenerateInvoiceDialogProps {
  isOpen: boolean
  onClose: () => void
  onGenerate: (form: GenerateInvoiceForm) => Promise<void>
  generating: boolean
}

const GenerateInvoiceDialog = memo(function GenerateInvoiceDialog({
  isOpen,
  onClose,
  onGenerate,
  generating
}: GenerateInvoiceDialogProps) {
  const [generateForm, setGenerateForm] = useState<GenerateInvoiceForm>({
    month: new Date().getMonth() + 1,
    year: new Date().getFullYear()
  })

  const handleGenerate = async () => {
    await onGenerate(generateForm)
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Generate Monthly Invoice</DialogTitle>
          <DialogDescription>
            Generate a new invoice based on agent usage for the specified month
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium">Month</label>
              <Select
                value={generateForm.month.toString()}
                onValueChange={(value) => setGenerateForm({...generateForm, month: parseInt(value)})}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Array.from({length: 12}, (_, i) => (
                    <SelectItem key={i + 1} value={(i + 1).toString()}>
                      {new Date(0, i).toLocaleString('default', { month: 'long' })}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <label className="text-sm font-medium">Year</label>
              <Input
                type="number"
                value={generateForm.year}
                onChange={(e) => setGenerateForm({...generateForm, year: parseInt(e.target.value)})}
                min="2020"
                max="2030"
              />
            </div>
          </div>
          
          <div className="flex justify-end space-x-2">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button onClick={handleGenerate} disabled={generating}>
              {generating ? 'Generating...' : 'Generate Invoice'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
})

export default GenerateInvoiceDialog
