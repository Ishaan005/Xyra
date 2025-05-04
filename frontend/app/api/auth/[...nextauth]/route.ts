import NextAuth from "next-auth"
import CredentialsProvider from "next-auth/providers/credentials"
import api, { setAuthToken } from "@/utils/api"

export const authOptions = {
  session: { strategy: "jwt" as const },
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        username: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      authorize: async (credentials) => {
        try {
          // request access token from backend
          const params = new URLSearchParams()
          params.append('username', credentials?.username || '')
          params.append('password', credentials?.password || '')
          const tokenRes = await api.post('/auth/login/access-token', params, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
          })
          const { access_token: accessToken } = tokenRes.data
          // set axios auth header for subsequent calls
          setAuthToken(accessToken)
          // fetch current user
          const userRes = await api.get('/auth/me')
          return { ...userRes.data, accessToken }
        } catch {
          return null
        }
      }
    })
  ],
  callbacks: {
    async jwt({ token, user }: { token: any; user?: any }) {
      if (user) token.accessToken = (user as any).accessToken
      return token
    },
    async session({ session, token }: { session: any; token: any }) {
      return { ...session, user: { ...session.user, accessToken: token.accessToken } }
    }
  },
  secret: process.env.NEXTAUTH_SECRET
}

const handler = NextAuth(authOptions)
export { handler as GET, handler as POST }