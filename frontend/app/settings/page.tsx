"use client"

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { 
  AlertCircle, 
  Key, 
  Copy, 
  Plus, 
  Trash2, 
  User,
  Shield,
  Bell
} from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import api, { setAuthToken } from '@/utils/api'
import { useOrganization } from '@/contexts/OrganizationContext'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"

interface ApiKey {
  id: number
  name: string
  description?: string
  key_prefix: string
  is_active: boolean
  last_used?: string
  created_at: string
  expires_at?: string
  user?: {
    id: number
    email: string
    full_name?: string
  }
}

interface ApiKeyWithToken extends ApiKey {
  token: string
}

export default function SettingsPage() {
  const router = useRouter()
  const { data: session, status } = useSession()
  const { currentOrgId } = useOrganization()
  
  // API Keys State
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([])
  const [showTokens, setShowTokens] = useState<{[key: string]: boolean}>({})
  const [newKeyName, setNewKeyName] = useState('')
  const [newKeyDescription, setNewKeyDescription] = useState('')
  const [newKeyDialogOpen, setNewKeyDialogOpen] = useState(false)
  const [createdToken, setCreatedToken] = useState<string | null>(null)
  const [showAllOrgKeys, setShowAllOrgKeys] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // User Settings State
  const [userSettings, setUserSettings] = useState({
    email_notifications: true,
    push_notifications: false,
    auto_logout_minutes: 60,
    two_factor_enabled: false
  })

  useEffect(() => {
    if (status === 'authenticated' && session?.user?.accessToken) {
      setAuthToken(session.user.accessToken)
      fetchApiKeys()
      fetchUserSettings()
    }
  }, [status, session, showAllOrgKeys])  // Add showAllOrgKeys to dependencies

  const fetchApiKeys = async () => {
    try {
      setLoading(true)
      const endpoint = showAllOrgKeys ? '/api-keys/organization/all' : '/api-keys'
      const response = await api.get(endpoint)
      setApiKeys(response.data)
    } catch (error: any) {
      console.error('Failed to fetch API keys:', error)
      setError('Failed to load API keys')
    } finally {
      setLoading(false)
    }
  }

  const fetchUserSettings = async () => {
    try {
      // For now, we'll use default settings since the backend doesn't have this endpoint yet
      // In a real implementation, this would be: const response = await api.get('/user/settings')
    } catch (error: any) {
      console.error('Failed to fetch user settings:', error)
    }
  }

  const createApiKey = async () => {
    if (!newKeyName.trim()) {
      setError('API key name is required')
      return
    }

    try {
      setLoading(true)
      setError(null)
      
      const response = await api.post('/api-keys', {
        name: newKeyName,
        description: newKeyDescription || undefined
      })
      
      const newApiKey: ApiKeyWithToken = response.data
      
      // Add to the list for display (without token for security)
      setApiKeys(prev => [{
        id: newApiKey.id,
        name: newApiKey.name,
        description: newApiKey.description,
        key_prefix: newApiKey.key_prefix,
        is_active: newApiKey.is_active,
        last_used: newApiKey.last_used,
        created_at: newApiKey.created_at,
        expires_at: newApiKey.expires_at
      }, ...prev])
      
      setCreatedToken(newApiKey.token)
      setNewKeyName('')
      setNewKeyDescription('')
      setNewKeyDialogOpen(false)
      
    } catch (error: any) {
      console.error('Failed to create API key:', error)
      setError('Failed to create API key')
    } finally {
      setLoading(false)
    }
  }

  const deleteApiKey = async (apiKeyId: number) => {
    try {
      setLoading(true)
      
      await api.delete(`/api-keys/${apiKeyId}`)
      setApiKeys(prev => prev.filter(key => key.id !== apiKeyId))
      
    } catch (error: any) {
      console.error('Failed to delete API key:', error)
      setError('Failed to delete API key')
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const toggleTokenVisibility = (tokenId: string) => {
    setShowTokens(prev => ({
      ...prev,
      [tokenId]: !prev[tokenId]
    }))
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (status === 'loading') {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>
  }

  if (status === 'unauthenticated') {
    router.push('/login')
    return null
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-gray-600 mt-2">Manage your account settings and preferences</p>
      </div>

      <Tabs defaultValue="tokens" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="tokens" className="flex items-center gap-2">
            <Key className="h-4 w-4" />
            API Keys
          </TabsTrigger>
          <TabsTrigger value="profile" className="flex items-center gap-2">
            <User className="h-4 w-4" />
            Profile
          </TabsTrigger>
          <TabsTrigger value="security" className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Security
          </TabsTrigger>
          <TabsTrigger value="notifications" className="flex items-center gap-2">
            <Bell className="h-4 w-4" />
            Notifications
          </TabsTrigger>
        </TabsList>

        <TabsContent value="tokens" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Key className="h-5 w-5" />
                    API Keys
                  </CardTitle>
                  <CardDescription>
                    {showAllOrgKeys 
                      ? "Viewing all API keys in your organization. API keys provide access to all agents and resources within your organization."
                      : "Create and manage your API keys for the Xyra Client SDK and programmatic access. API keys provide access to all agents and resources within your organization."
                    }
                  </CardDescription>
                </div>
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <Label htmlFor="show-all-keys" className="text-sm">
                      Show all organization keys
                    </Label>
                    <Switch
                      id="show-all-keys"
                      checked={showAllOrgKeys}
                      onCheckedChange={setShowAllOrgKeys}
                    />
                  </div>
                  <Dialog open={newKeyDialogOpen} onOpenChange={setNewKeyDialogOpen}>
                    <DialogTrigger asChild>
                      <Button className="flex items-center gap-2">
                        <Plus className="h-4 w-4" />
                        Create API Key
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Create New API Key</DialogTitle>
                        <DialogDescription>
                          Create a new API key for programmatic access to your account.
                        </DialogDescription>
                      </DialogHeader>
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="key-name">API Key Name</Label>
                        <Input
                          id="key-name"
                          placeholder="e.g., Production API, Development"
                          value={newKeyName}
                          onChange={(e) => setNewKeyName(e.target.value)}
                        />
                      </div>
                      <div>
                        <Label htmlFor="key-description">Description (Optional)</Label>
                        <Input
                          id="key-description"
                          placeholder="Brief description of what this key is for"
                          value={newKeyDescription}
                          onChange={(e) => setNewKeyDescription(e.target.value)}
                        />
                      </div>
                      {error && (
                        <Alert variant="destructive">
                          <AlertCircle className="h-4 w-4" />
                          <AlertDescription>{error}</AlertDescription>
                        </Alert>
                      )}
                    </div>
                    <DialogFooter>
                      <Button
                        variant="outline"
                        onClick={() => {
                          setNewKeyDialogOpen(false)
                          setNewKeyName('')
                          setNewKeyDescription('')
                          setError(null)
                        }}
                      >
                        Cancel
                      </Button>
                      <Button onClick={createApiKey} disabled={loading}>
                        {loading ? 'Creating...' : 'Create API Key'}
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {loading && (
                <div className="text-center py-4">
                  <div className="text-sm text-gray-600">Loading API keys...</div>
                </div>
              )}
              
              {!loading && createdToken && (
                <Alert className="mb-6 border-green-200 bg-green-50">
                  <Key className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-800">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="font-semibold mb-2">API Key created successfully!</div>
                        <div className="font-mono text-sm bg-white p-2 rounded border flex items-center justify-between">
                          <span>{createdToken}</span>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => copyToClipboard(createdToken)}
                          >
                            <Copy className="h-4 w-4" />
                          </Button>
                        </div>
                        <div className="text-sm mt-2">
                          Make sure to copy your API key now. You won't be able to see it again!
                        </div>
                      </div>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => setCreatedToken(null)}
                        className="ml-2"
                      >
                        ×
                      </Button>
                    </div>
                  </AlertDescription>
                </Alert>
              )}

              {!loading && apiKeys.length === 0 ? (
                <div className="text-center py-8">
                  <Key className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {showAllOrgKeys ? "No API keys in organization" : "No API keys"}
                  </h3>
                  <p className="text-gray-600 mb-4">
                    {showAllOrgKeys 
                      ? "No one in your organization has created API keys yet"
                      : "Create your first organization API key to start using the Xyra Client SDK with your agents"
                    }
                  </p>
                </div>
              ) : !loading ? (
                <div className="space-y-4">
                  {apiKeys.map((apiKey) => (
                    <div key={apiKey.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-3">
                          <h3 className="font-semibold">{apiKey.name}</h3>
                          <Badge variant={apiKey.is_active ? "default" : "secondary"}>
                            {apiKey.is_active ? "Active" : "Inactive"}
                          </Badge>
                        </div>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => deleteApiKey(apiKey.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                      
                      {apiKey.description && (
                        <p className="text-sm text-gray-600 mb-2">{apiKey.description}</p>
                      )}
                      
                      <div className="space-y-2 text-sm text-gray-600">
                        <div>Created: {formatDate(apiKey.created_at)}</div>
                        {apiKey.user && showAllOrgKeys && (
                          <div>Owner: {apiKey.user.full_name || apiKey.user.email}</div>
                        )}
                        {apiKey.last_used && (
                          <div>Last used: {formatDate(apiKey.last_used)}</div>
                        )}
                        {apiKey.expires_at && (
                          <div>Expires: {formatDate(apiKey.expires_at)}</div>
                        )}
                      </div>

                      <div className="mt-3">
                        <Label className="text-xs text-gray-500">API Key Preview</Label>
                        <div className="flex items-center gap-2 mt-1">
                          <div className="font-mono text-sm bg-gray-50 p-2 rounded flex-1">
                            {apiKey.key_prefix}
                          </div>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => copyToClipboard(apiKey.key_prefix)}
                          >
                            <Copy className="h-4 w-4" />
                          </Button>
                        </div>
                        <p className="text-xs text-gray-500 mt-1">
                          This is only a preview. Use this API key with the Xyra Client SDK.
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : null}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="profile" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                Profile Information
              </CardTitle>
              <CardDescription>
                Update your profile information and preferences
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={session?.user?.email || ''}
                    disabled
                  />
                </div>
                <div>
                  <Label htmlFor="name">Name</Label>
                  <Input
                    id="name"
                    value={session?.user?.name || ''}
                    placeholder="Your name"
                  />
                </div>
              </div>
              <Button>Update Profile</Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Security Settings
              </CardTitle>
              <CardDescription>
                Manage your security preferences and authentication settings
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold">Two-Factor Authentication</h3>
                  <p className="text-sm text-gray-600">
                    Add an extra layer of security to your account
                  </p>
                </div>
                <Switch
                  checked={userSettings.two_factor_enabled}
                  onCheckedChange={(checked) =>
                    setUserSettings(prev => ({ ...prev, two_factor_enabled: checked }))
                  }
                />
              </div>
              
              <Separator />
              
              <div>
                <Label htmlFor="auto-logout">Auto-logout (minutes)</Label>
                <Input
                  id="auto-logout"
                  type="number"
                  value={userSettings.auto_logout_minutes}
                  onChange={(e) =>
                    setUserSettings(prev => ({ ...prev, auto_logout_minutes: parseInt(e.target.value) || 60 }))
                  }
                  className="w-32 mt-1"
                />
                <p className="text-sm text-gray-600 mt-1">
                  Automatically log out after this many minutes of inactivity
                </p>
              </div>
              
              <Button>Update Security Settings</Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5" />
                Notification Preferences
              </CardTitle>
              <CardDescription>
                Choose how and when you want to receive notifications
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold">Email Notifications</h3>
                  <p className="text-sm text-gray-600">
                    Receive notifications via email
                  </p>
                </div>
                <Switch
                  checked={userSettings.email_notifications}
                  onCheckedChange={(checked) =>
                    setUserSettings(prev => ({ ...prev, email_notifications: checked }))
                  }
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold">Push Notifications</h3>
                  <p className="text-sm text-gray-600">
                    Receive push notifications in your browser
                  </p>
                </div>
                <Switch
                  checked={userSettings.push_notifications}
                  onCheckedChange={(checked) =>
                    setUserSettings(prev => ({ ...prev, push_notifications: checked }))
                  }
                />
              </div>
              
              <Button>Update Notifications</Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
