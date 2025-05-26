"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import api from "@/utils/api"
import toast from "react-hot-toast"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { AlertCircle, Zap, ArrowRight, Loader2, User, Mail, Lock, CheckCircle } from "lucide-react"
import Link from "next/link"

export default function SignupPage() {
  const router = useRouter()
  const [email, setEmail] = useState("")
  const [fullName, setFullName] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  // Password validation
  const [passwordFocus, setPasswordFocus] = useState(false)
  const passwordLength = password.length >= 8
  const passwordHasNumber = /\d/.test(password)
  const passwordHasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password)
  const passwordsMatch = password === confirmPassword && password !== ""

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Validate passwords match
    if (password !== confirmPassword) {
      setError("Passwords do not match")
      return
    }

    setError(null)
    setIsLoading(true)
    try {
      await api.post("/auth/signup", {
        email,
        full_name: fullName,
        password,
      })
      toast.success("Account created! Please sign in.")
      router.push("/login")
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message
      setError(msg)
      toast.error(msg)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-background to-muted/20 p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <div className="rounded-full bg-gold/10 p-3">
              <div className="rounded-md bg-gold p-2">
                <Zap className="h-6 w-6 text-white" />
              </div>
            </div>
          </div>
          <h1 className="text-3xl font-bold">Business Engine</h1>
          <p className="text-muted-foreground mt-2">Create your account to get started</p>
        </div>

        <Card className="border-border/8 ring-1 ring-border/5 shadow-sm overflow-hidden hover:ring-border/10 transition-all duration-300">
          <CardHeader className="bg-gradient-to-r from-muted/30 to-transparent">
            <CardTitle>Create Account</CardTitle>
            <CardDescription>Fill in your details to sign up</CardDescription>
          </CardHeader>

          <CardContent className="pt-6">
            {error && (
              <div className="bg-destructive/10 text-destructive rounded-lg p-3 flex items-start gap-2 mb-4">
                <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
                <p className="text-sm">{error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="fullName">Full Name</Label>
                <div className="relative">
                  <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="fullName"
                    placeholder="John Doe"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
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
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    onFocus={() => setPasswordFocus(true)}
                    onBlur={() => setPasswordFocus(false)}
                    className="pl-10"
                    required
                  />
                </div>

                {passwordFocus && (
                  <div className="mt-2 text-xs space-y-1 bg-muted/30 p-2 rounded-md border border-border/10 ring-1 ring-border/5">
                    <p className="flex items-center">
                      {passwordLength ? (
                        <CheckCircle className="h-3 w-3 text-success mr-1" />
                      ) : (
                        <AlertCircle className="h-3 w-3 text-muted-foreground mr-1" />
                      )}
                      At least 8 characters
                    </p>
                    <p className="flex items-center">
                      {passwordHasNumber ? (
                        <CheckCircle className="h-3 w-3 text-success mr-1" />
                      ) : (
                        <AlertCircle className="h-3 w-3 text-muted-foreground mr-1" />
                      )}
                      Contains a number
                    </p>
                    <p className="flex items-center">
                      {passwordHasSpecial ? (
                        <CheckCircle className="h-3 w-3 text-success mr-1" />
                      ) : (
                        <AlertCircle className="h-3 w-3 text-muted-foreground mr-1" />
                      )}
                      Contains a special character
                    </p>
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Confirm Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="confirmPassword"
                    type="password"
                    placeholder="••••••••"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className={`pl-10 ${confirmPassword && !passwordsMatch ? "border-destructive" : ""}`}
                    required
                  />
                  {confirmPassword && (
                    <div className="absolute right-3 top-3">
                      {passwordsMatch ? (
                        <CheckCircle className="h-4 w-4 text-success" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-destructive" />
                      )}
                    </div>
                  )}
                </div>
                {confirmPassword && !passwordsMatch && (
                  <p className="text-xs text-destructive mt-1">Passwords do not match</p>
                )}
              </div>

              <Button
                type="submit"
                className="w-full mt-6"
                disabled={isLoading || !passwordsMatch || !passwordLength || !passwordHasNumber || !passwordHasSpecial}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating account...
                  </>
                ) : (
                  <>
                    Create Account
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
            </form>
          </CardContent>

          <CardFooter className="flex flex-col space-y-4 border-t">
            <div className="text-center text-sm pt-4">
              <span className="text-muted-foreground">Already have an account? </span>
              <Link href="/login" className="text-primary font-medium hover:underline">
                Sign in
              </Link>
            </div>

            <div className="text-center text-xs text-muted-foreground">
              By signing up, you agree to our
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
