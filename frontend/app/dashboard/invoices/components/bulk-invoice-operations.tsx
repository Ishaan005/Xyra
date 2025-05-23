"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { ChevronDown, Trash, Mail, Ban, Download } from "lucide-react"
import { Invoice } from "../../../../types/invoice"
import { invoiceApi } from "../../../../utils/invoice-api"
import InvoicePaymentEmailDialog from "./invoice-payment-email-dialog"
import ConfirmationDialog from "./confirmation-dialog"

interface BulkInvoiceOperationsProps {
  selectedInvoices: Invoice[];
  onDeselectAll: () => void;
  onOperationComplete: () => void;
}

export default function BulkInvoiceOperations({
  selectedInvoices,
  onDeselectAll,
  onOperationComplete
}: BulkInvoiceOperationsProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  
  const [isConfirmCancelOpen, setIsConfirmCancelOpen] = useState(false);
  const [isConfirmDeleteOpen, setIsConfirmDeleteOpen] = useState(false);
  const [isEmailDialogOpen, setIsEmailDialogOpen] = useState(false);

  const canCancel = selectedInvoices.every(invoice => invoice.status === "pending");
  const hasValidEmails = selectedInvoices.length > 0;
  const pendingCount = selectedInvoices.filter(invoice => invoice.status === "pending").length;

  const handleBulkCancel = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const pendingInvoices = selectedInvoices.filter(invoice => invoice.status === "pending");
      const results = await Promise.allSettled(
        pendingInvoices.map(invoice => invoiceApi.cancelInvoice(invoice.id))
      );
      
      const successful = results.filter(result => result.status === "fulfilled").length;
      const failed = results.filter(result => result.status === "rejected").length;
      
      if (failed > 0) {
        setError(`${successful} invoices cancelled successfully, ${failed} failed.`);
      } else {
        setSuccessMessage(`${successful} invoices cancelled successfully.`);
        onDeselectAll();
        onOperationComplete();
      }
    } catch (err: any) {
      setError(err.message || "Failed to cancel invoices");
    } finally {
      setLoading(false);
      setIsConfirmCancelOpen(false);
    }
  };

  const handleBulkDownload = () => {
    // Open each invoice PDF in a new tab
    selectedInvoices.forEach(invoice => {
      const pdfUrl = invoiceApi.getInvoicePdfUrl(invoice.id);
      window.open(pdfUrl, '_blank');
    });
  };

  if (selectedInvoices.length === 0) {
    return null;
  }

  return (
    <div className="flex items-center gap-2 p-2 bg-muted rounded-md mb-4">
      <div className="flex-1">
        <span className="text-sm font-medium">{selectedInvoices.length} invoices selected</span>
        {pendingCount > 0 && (
          <span className="text-xs text-muted-foreground ml-2">({pendingCount} pending)</span>
        )}
      </div>
      
      <Button variant="ghost" size="sm" onClick={onDeselectAll}>
        Deselect All
      </Button>
      
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button size="sm" className="gap-1">
            Bulk Actions <ChevronDown className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuLabel>Invoice Operations</DropdownMenuLabel>
          <DropdownMenuSeparator />
          
          <DropdownMenuItem 
            onClick={() => setIsEmailDialogOpen(true)}
            disabled={!hasValidEmails}
          >
            <Mail className="mr-2 h-4 w-4" />
            <span>Email Selected</span>
          </DropdownMenuItem>
          
          <DropdownMenuItem onClick={handleBulkDownload}>
            <Download className="mr-2 h-4 w-4" />
            <span>Download PDFs</span>
          </DropdownMenuItem>
          
          <DropdownMenuSeparator />
          
          <DropdownMenuItem 
            onClick={() => setIsConfirmCancelOpen(true)}
            disabled={!canCancel}
            className="text-amber-600"
          >
            <Ban className="mr-2 h-4 w-4" />
            <span>Cancel Selected</span>
          </DropdownMenuItem>

          <DropdownMenuItem 
            onClick={() => setIsConfirmDeleteOpen(true)}
            className="text-red-600"
          >
            <Trash className="mr-2 h-4 w-4" />
            <span>Delete Selected</span>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
      
      {/* Confirmation dialogs */}
      <ConfirmationDialog
        isOpen={isConfirmCancelOpen}
        onClose={() => setIsConfirmCancelOpen(false)}
        onConfirm={handleBulkCancel}
        title="Cancel Multiple Invoices"
        description={`Are you sure you want to cancel ${selectedInvoices.length} invoices? This action cannot be undone.`}
        confirmLabel="Yes, Cancel Invoices"
        cancelLabel="No, Keep Invoices"
        variant="destructive"
      />
      
      {/* ToDo: Implement bulk email dialog */}
      
      {error && (
        <div className="mt-2 text-sm text-red-600">{error}</div>
      )}
      
      {successMessage && (
        <div className="mt-2 text-sm text-green-600">{successMessage}</div>
      )}
    </div>
  );
}
