"use client"

import type React from "react"
import { useState } from "react"
import { useRouter } from "next/navigation"
import api, { setAuthToken } from "@/utils/api"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { AlertCircle, Lock, Mail } from "lucide-react"
import Link from "next/link"

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)

    try {
      const params = new URLSearchParams()
      params.append("username", email)
      params.append("password", password)

      const res = await api.post("/auth/login", params, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      })

      const token = res.data.access_token
      localStorage.setItem("token", token)
      setAuthToken(token)
      router.push("/dashboard")
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-white to-gold-20 p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold">Business Engine</h1>
          <p className="text-gray-dark mt-2">Sign in to your account</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Sign In</CardTitle>
            <CardDescription>Enter your credentials to access your account</CardDescription>
          </CardHeader>
          <CardContent>
            {error && (
              <div className="bg-destructive/10 text-destructive rounded-lg p-3 flex items-start gap-2 mb-4">
                <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
                <p className="text-sm">{error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-dark" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="name@company.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="password">Password</Label>
                  <Link href="/forgot-password" className="text-xs text-primary hover:underline">
                    Forgot password?
                  </Link>
                </div>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-dark" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "Signing in..." : "Sign In"}
              </Button>
            </form>
          </CardContent>
          <CardFooter className="flex flex-col space-y-4">
            <div className="text-center text-sm">
              <span className="text-gray-dark">Don't have an account? </span>
              <Link href="/signup" className="text-primary font-medium hover:underline">
                Sign up
              </Link>
            </div>

            <div className="text-center text-xs text-gray-dark">
              By signing in, you agree to our
              <Link href="/terms" className="text-primary hover:underline mx-1">
                Terms of Service
              </Link>
              and
              <Link href="/privacy" className="text-primary hover:underline ml-1">
                Privacy Policy
              </Link>
            </div>
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}
