"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog"
import { toast } from "react-hot-toast"
import api from "@/utils/api"

// --- API Service ---
async function fetchConnectors() {
  const res = await api.get("/integration/connectors")
  return res.data
}
async function createConnector(data: any) {
  const res = await api.post("/integration/connectors", data)
  return res.data
}
async function updateConnector(id: string, data: any) {
  const res = await api.put(`/integration/connectors/${id}`, data)
  return res.data
}
async function deleteConnector(id: string) {
  await api.delete(`/integration/connectors/${id}`)
}
async function testConnector(id: string) {
  const res = await api.post(`/integration/connectors/${id}/test`)
  return res.data
}
async function extractData(id: string, extractionConfig: any) {
  const res = await api.post(`/integration/connectors/${id}/extract`, extractionConfig)
  return res.data
}

export default function IntegrationConnectorsPage() {
  const [connectors, setConnectors] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [showDialog, setShowDialog] = useState(false)
  const [form, setForm] = useState<any>({
    // Remove connector_id from user input
    name: "",
    connector_type: "rest_api",
    config: { base_url: "", timeout: 30, verify_ssl: true, auth: { type: "none" } },
    description: "",
  })
  const [advanced, setAdvanced] = useState(false)
  const [selected, setSelected] = useState<any>(null)
  const [extractResult, setExtractResult] = useState<any>(null)
  const [extractConfig, setExtractConfig] = useState<any>({})
  const [extractLoading, setExtractLoading] = useState(false)

  useEffect(() => {
    setLoading(true)
    fetchConnectors()
      .then(setConnectors)
      .catch(() => toast.error("Failed to load connectors"))
      .finally(() => setLoading(false))
  }, [])

  const handleFormChange = (field: string, value: any) => {
    setForm((f: any) => ({ ...f, [field]: value }))
  }
  const handleConfigChange = (field: string, value: any) => {
    setForm((f: any) => ({ ...f, config: { ...f.config, [field]: value } }))
  }
  const handleAuthChange = (field: string, value: any) => {
    setForm((f: any) => ({ ...f, config: { ...f.config, auth: { ...f.config.auth, [field]: value } } }))
  }

  const handleSave = async () => {
    try {
      if (selected) {
        await updateConnector(selected.connector_id, form)
        toast.success("Connector updated")
      } else {
        await createConnector(form)
        toast.success("Connector created")
      }
      setShowDialog(false)
      setSelected(null)
      setForm({ name: "", connector_type: "rest_api", config: { base_url: "", timeout: 30, verify_ssl: true, auth: { type: "none" } }, description: "" })
      setLoading(true)
      fetchConnectors().then(setConnectors).finally(() => setLoading(false))
    } catch (e: any) {
      toast.error(e.message)
    }
  }

  const handleDelete = async (id: string) => {
    if (!window.confirm("Delete this connector?")) return
    try {
      await deleteConnector(id)
      toast.success("Connector deleted")
      setLoading(true)
      fetchConnectors().then(setConnectors).finally(() => setLoading(false))
    } catch (e: any) {
      toast.error(e.message)
    }
  }

  const handleTest = async (id: string) => {
    try {
      const res = await testConnector(id)
      toast.success(res.is_healthy ? "Connection healthy" : res.error_message || "Connection failed")
    } catch (e: any) {
      toast.error(e.message)
    }
  }

  const handleExtract = async () => {
    if (!selected) return
    setExtractLoading(true)
    try {
      const res = await extractData(selected.connector_id, extractConfig)
      setExtractResult(res)
      toast.success("Data extracted")
    } catch (e: any) {
      toast.error(e.message)
    } finally {
      setExtractLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto py-10">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Integration Connectors</h1>
        <Button onClick={() => { setShowDialog(true); setSelected(null); }}>New Connector</Button>
      </div>
      <Separator />
      <div className="grid gap-4 mt-6">
        {loading ? <div>Loading...</div> : connectors.length === 0 ? <div>No connectors found.</div> : connectors.map((c) => (
          <Card key={c.connector_id} className="p-4 flex flex-col md:flex-row md:items-center md:justify-between gap-2">
            <div>
              <div className="font-semibold text-lg">{c.name} <span className="text-xs text-gray-500">({c.connector_type})</span></div>
              <div className="text-xs text-gray-500">{c.description}</div>
              <div className="text-xs mt-1">Status: <span className={c.status === "active" ? "text-green-600" : "text-red-600"}>{c.status}</span></div>
            </div>
            <div className="flex gap-2 mt-2 md:mt-0">
              <Button size="sm" variant="outline" onClick={() => { setSelected(c); setForm(c); setShowDialog(true); }}>Edit</Button>
              <Button size="sm" variant="outline" onClick={() => handleTest(c.connector_id)}>Test</Button>
              <Button size="sm" variant="destructive" onClick={() => handleDelete(c.connector_id)}>Delete</Button>
              <Button size="sm" variant="secondary" onClick={() => { setSelected(c); setExtractResult(null); }}>Extract</Button>
            </div>
          </Card>
        ))}
      </div>
      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent className="max-w-lg">
          <DialogTitle>{selected ? "Edit Connector" : "New Connector"}</DialogTitle>
          <div className="grid gap-3 mt-4">
            {/* Remove Connector ID input */}
            <Input placeholder="Name" value={form.name} onChange={e => handleFormChange("name", e.target.value)} />
            <select className="border rounded px-2 py-1" value={form.connector_type} onChange={e => handleFormChange("connector_type", e.target.value)}>
              <option value="rest_api">REST API</option>
              <option value="graphql">GraphQL</option>
              <option value="file_system">File System</option>
              <option value="custom">Custom</option>
            </select>
            <Input placeholder="Base URL" value={form.config.base_url || ""} onChange={e => handleConfigChange("base_url", e.target.value)} />
            <Input placeholder="Description" value={form.description} onChange={e => handleFormChange("description", e.target.value)} />
            <Button variant="link" className="justify-start px-0" onClick={() => setAdvanced(a => !a)}>{advanced ? "Hide" : "Show"} Advanced Options</Button>
            {advanced && (
              <div className="grid gap-2 border rounded p-2 bg-gray-50">
                <Input type="number" placeholder="Timeout (seconds)" value={form.config.timeout} onChange={e => handleConfigChange("timeout", Number(e.target.value))} />
                <label className="flex items-center gap-2"><input type="checkbox" checked={form.config.verify_ssl} onChange={e => handleConfigChange("verify_ssl", e.target.checked)} /> Verify SSL</label>
                <select className="border rounded px-2 py-1" value={form.config.auth.type} onChange={e => handleAuthChange("type", e.target.value)}>
                  <option value="none">No Auth</option>
                  <option value="api_key">API Key</option>
                  <option value="bearer_token">Bearer Token</option>
                  <option value="basic">Basic Auth</option>
                  <option value="oauth2">OAuth2</option>
                </select>
                {form.config.auth.type === "api_key" && (
                  <Input placeholder="API Key" value={form.config.auth.key || ""} onChange={e => handleAuthChange("key", e.target.value)} />
                )}
                {form.config.auth.type === "bearer_token" && (
                  <Input placeholder="Bearer Token" value={form.config.auth.token || ""} onChange={e => handleAuthChange("token", e.target.value)} />
                )}
                {form.config.auth.type === "basic" && (
                  <>
                    <Input placeholder="Username" value={form.config.auth.username || ""} onChange={e => handleAuthChange("username", e.target.value)} />
                    <Input placeholder="Password" type="password" value={form.config.auth.password || ""} onChange={e => handleAuthChange("password", e.target.value)} />
                  </>
                )}
                {form.config.auth.type === "oauth2" && (
                  <>
                    <Input placeholder="Client ID" value={form.config.auth.client_id || ""} onChange={e => handleAuthChange("client_id", e.target.value)} />
                    <Input placeholder="Client Secret" value={form.config.auth.client_secret || ""} onChange={e => handleAuthChange("client_secret", e.target.value)} />
                    <Input placeholder="Token URL" value={form.config.auth.token_url || ""} onChange={e => handleAuthChange("token_url", e.target.value)} />
                  </>
                )}
              </div>
            )}
            <div className="flex gap-2 mt-2">
              <Button onClick={handleSave}>{selected ? "Update" : "Create"}</Button>
              <Button variant="outline" onClick={() => setShowDialog(false)}>Cancel</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
      {/* Extraction Dialog */}
      <Dialog open={!!selected && extractResult === null} onOpenChange={open => { if (!open) setSelected(null) }}>
        <DialogContent className="max-w-lg">
          <DialogTitle>Extract Data</DialogTitle>
          <div className="grid gap-3 mt-4">
            <Input placeholder="Extraction Endpoint or Query" value={extractConfig.endpoint || extractConfig.query || ""} onChange={e => setExtractConfig((cfg: any) => ({ ...cfg, [form.connector_type === "graphql" ? "query" : "endpoint"]: e.target.value }))} />
            <Button onClick={handleExtract} disabled={extractLoading}>{extractLoading ? "Extracting..." : "Extract"}</Button>
            {extractResult && (
              <div className="mt-2 text-xs whitespace-pre-wrap bg-gray-100 p-2 rounded max-h-60 overflow-auto">{JSON.stringify(extractResult, null, 2)}</div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
