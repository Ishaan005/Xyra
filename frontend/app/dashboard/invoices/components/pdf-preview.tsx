"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Loader2, Download, X } from "lucide-react"

interface PdfPreviewProps {
  isOpen: boolean;
  onClose: () => void;
  pdfUrl: string;
  title: string;
  downloadUrl?: string;
}

export default function PdfPreview({ 
  isOpen, 
  onClose, 
  pdfUrl, 
  title,
  downloadUrl 
}: PdfPreviewProps) {
  const [isLoading, setIsLoading] = useState(true);
  const effectiveDownloadUrl = downloadUrl || pdfUrl;
  
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl w-[90vw] h-[80vh] flex flex-col">
        <DialogHeader className="flex flex-row items-center justify-between pb-2">
          <DialogTitle>{title}</DialogTitle>
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() => window.open(effectiveDownloadUrl, '_blank')}
            >
              <Download className="h-4 w-4 mr-2" />
              Download
            </Button>
            <Button
              size="sm"
              variant="ghost"
              className="h-8 w-8 p-0"
              onClick={onClose}
            >
              <X className="h-4 w-4" />
              <span className="sr-only">Close</span>
            </Button>
          </div>
        </DialogHeader>
        
        <div className="relative flex-1 bg-muted rounded overflow-hidden">
          {isLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-background/80">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          )}
          <iframe
            src={`${pdfUrl}#toolbar=0`}
            className="w-full h-full border-0"
            onLoad={() => setIsLoading(false)}
            title="PDF Preview"
          />
        </div>
      </DialogContent>
    </Dialog>
  );
}
