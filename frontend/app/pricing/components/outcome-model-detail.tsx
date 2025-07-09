"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Edit } from "lucide-react"
import toast from "react-hot-toast"
import api from "@/utils/api"
import OutcomeBasedForm from "./OutcomeBasedForm"

interface OutcomeModelDetailProps {
  modelId: number
  onBack: () => void
}

export default function OutcomeModelDetail({ modelId, onBack }: OutcomeModelDetailProps) {
  const [model, setModel] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [editMode, setEditMode] = useState(false)

  useEffect(() => {
    fetchModel()
  }, [modelId])

  const fetchModel = async () => {
    try {
      const response = await api.get(`/billing-models/${modelId}`)
      setModel(response.data)
    } catch (error) {
      console.error("Failed to fetch model:", error)
      toast.error("Failed to load model details")
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateModel = async (updatedData: any) => {
    try {
      const response = await api.put(`/billing-models/${modelId}`, updatedData)
      setModel(response.data)
      setEditMode(false)
      toast.success("Model updated successfully")
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to update model")
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading outcome model...</p>
        </div>
      </div>
    )
  }

  if (!model) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Model not found</p>
        <Button onClick={onBack} className="mt-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Models
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={onBack}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Models
          </Button>
          <div>
            <h1 className="text-2xl font-bold">{model.name}</h1>
            <p className="text-muted-foreground">{model.description}</p>
          </div>
        </div>
        <Button onClick={() => setEditMode(!editMode)}>
          <Edit className="h-4 w-4 mr-2" />
          {editMode ? 'Cancel Edit' : 'Edit Model'}
        </Button>
      </div>

      {editMode ? (
        <Card>
          <CardHeader>
            <CardTitle>Edit Outcome Billing Model</CardTitle>
          </CardHeader>
          <CardContent>
            <OutcomeBasedForm model={model} setModel={setModel} />
            <div className="flex justify-between mt-6 pt-4 border-t">
              <Button variant="outline" onClick={() => setEditMode(false)}>
                Cancel
              </Button>
              <Button onClick={() => handleUpdateModel(model)}>
                Save Changes
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>Outcome Model Details</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <strong>Model Type:</strong> {model.model_type}
              </div>
              <div>
                <strong>Status:</strong> {model.is_active ? 'Active' : 'Inactive'}
              </div>
              {model.outcome_config && model.outcome_config.length > 0 && (
                <div>
                  <strong>Outcome Configuration:</strong>
                  <pre className="bg-gray-100 p-2 rounded mt-2 text-sm">
                    {JSON.stringify(model.outcome_config[0], null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
