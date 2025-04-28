"use client"

import { useState, useEffect } from "react"
import api, { setAuthToken } from "@/utils/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Zap } from "lucide-react"

interface Agent {
  id: number
  name: string
  description?: string
  config?: Record<string, any>
  is_active: boolean
  external_id?: string
  billing_model_id?: number
}

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [newAgent, setNewAgent] = useState({
    name: "",
    description: "",
    external_id: "",
    billing_model_id: "",
  })

  const [editAgentId, setEditAgentId] = useState<number | null>(null)
  const [editData, setEditData] = useState({
    name: "",
    description: "",
    external_id: "",
    billing_model_id: "",
    is_active: true,
  })

  // fetch list
  const fetchAgents = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem("token")
      if (token) setAuthToken(token)
      const res = await api.get<Agent[]>("/agents", {
        params: { org_id: 1 },
      })
      setAgents(res.data)
    } catch (e: any) {
      setError(e.message || "Failed to load agents")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAgents()
  }, [])

  // create new
  const handleCreate = async () => {
    if (!newAgent.name) return
    try {
      await api.post("/agents", {
        name: newAgent.name,
        description: newAgent.description,
        external_id: newAgent.external_id || undefined,
        billing_model_id: newAgent.billing_model_id ? Number(newAgent.billing_model_id) : undefined,
        organization_id: 1,
      })
      setNewAgent({ name: "", description: "", external_id: "", billing_model_id: "" })
      fetchAgents()
    } catch (e: any) {
      setError(e.message || "Failed to create agent")
    }
  }

  // update existing
  const handleSave = async (id: number) => {
    try {
      await api.put(`/agents/${id}`, {
        ...editData,
        billing_model_id: editData.billing_model_id ? Number(editData.billing_model_id) : undefined,
      })
      setEditAgentId(null)
      fetchAgents()
    } catch (e: any) {
      setError(e.message || "Failed to update agent")
    }
  }

  // delete
  const handleDelete = async (id: number) => {
    if (!confirm("Delete this agent?")) return
    try {
      await api.delete(`/agents/${id}`)
      fetchAgents()
    } catch (e: any) {
      setError(e.message || "Failed to delete agent")
    }
  }

  return (
    <div className="p-4 md:p-8 space-y-6">
      <h1 className="text-2xl font-bold flex items-center gap-2">
        <Zap className="h-6 w-6 text-gold" />
        Manage Agents
      </h1>
      {error && <div className="text-red-600">{error}</div>}

      <section className="bg-background p-4 rounded shadow-sm space-y-2">
        <h2 className="text-lg font-semibold">Create New Agent</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Input
            placeholder="Name"
            value={newAgent.name}
            onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })}
          />
          <Input
            placeholder="Description"
            value={newAgent.description}
            onChange={(e) => setNewAgent({ ...newAgent, description: e.target.value })}
          />
          <Input
            placeholder="External ID"
            value={newAgent.external_id}
            onChange={(e) => setNewAgent({ ...newAgent, external_id: e.target.value })}
          />
          <Input
            type="number"
            placeholder="Billing Model ID"
            value={newAgent.billing_model_id}
            onChange={(e) => setNewAgent({ ...newAgent, billing_model_id: e.target.value })}
          />
        </div>
        <Button className="mt-3" onClick={handleCreate}>
          Create Agent
        </Button>
      </section>

      <section className="bg-background p-4 rounded shadow-sm">
        <h2 className="text-lg font-semibold mb-2">Existing Agents</h2>
        {loading ? (
          <div>Loading...</div>
        ) : (
          <table className="w-full table-auto">
            <thead>
              <tr className="text-left border-b">
                <th className="px-2 py-1">Name</th>
                <th className="px-2 py-1">Description</th>
                <th className="px-2 py-1">External ID</th>
                <th className="px-2 py-1">Active</th>
                <th className="px-2 py-1">Actions</th>
              </tr>
            </thead>
            <tbody>
              {agents.map((agent) => (
                <>
                  <tr key={agent.id} className="border-b">
                    <td className="px-2 py-1">{agent.name}</td>
                    <td className="px-2 py-1">{agent.description}</td>
                    <td className="px-2 py-1">{agent.external_id}</td>
                    <td className="px-2 py-1">{agent.is_active ? 'Yes' : 'No'}</td>
                    <td className="px-2 py-1 space-x-2">
                      <Button size="sm" variant="outline" onClick={() => {
                        setEditAgentId(agent.id)
                        setEditData({
                          name: agent.name || '',
                          description: agent.description || '',
                          external_id: agent.external_id || '',
                          billing_model_id: agent.billing_model_id?.toString() || '',
                          is_active: agent.is_active,
                        })
                      }}>
                        Edit
                      </Button>
                      <Button size="sm" variant="destructive" onClick={() => handleDelete(agent.id)}>
                        Delete
                      </Button>
                    </td>
                  </tr>
                  {editAgentId === agent.id && (
                    <tr>
                      <td colSpan={5} className="bg-muted p-3">
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                          <Input
                            placeholder="Name"
                            value={editData.name}
                            onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                          />
                          <Input
                            placeholder="Description"
                            value={editData.description}
                            onChange={(e) => setEditData({ ...editData, description: e.target.value })}
                          />
                          <Input
                            placeholder="External ID"
                            value={editData.external_id}
                            onChange={(e) => setEditData({ ...editData, external_id: e.target.value })}
                          />
                          <Input
                            type="number"
                            placeholder="Billing Model ID"
                            value={editData.billing_model_id}
                            onChange={(e) => setEditData({ ...editData, billing_model_id: e.target.value })}
                          />
                        </div>
                        <div className="mt-3 flex gap-2">
                          <Button size="sm" onClick={() => handleSave(agent.id)}>
                            Save
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => setEditAgentId(null)}>
                            Cancel
                          </Button>
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  )
}