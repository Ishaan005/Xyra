import { useState, useEffect } from "react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { CheckCircle } from "lucide-react"

interface CopyToClipboardAlertProps {
  show: boolean;
  onClose: () => void;
  message?: string;
}

export function CopyToClipboardAlert({ 
  show, 
  onClose,
  message = "Copied to clipboard!"
}: CopyToClipboardAlertProps) {
  useEffect(() => {
    if (show) {
      const timer = setTimeout(() => {
        onClose();
      }, 3000);
      
      return () => clearTimeout(timer);
    }
  }, [show, onClose]);
  
  if (!show) return null;
  
  return (
    <Alert className="fixed bottom-4 right-4 w-auto max-w-md bg-green-50 border-green-200 text-green-800 shadow-lg z-50 flex items-center">
      <CheckCircle className="h-4 w-4 text-green-600 mr-2" />
      <AlertDescription>{message}</AlertDescription>
    </Alert>
  );
}
