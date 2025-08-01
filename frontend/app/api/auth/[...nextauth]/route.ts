import NextAuth from "next-auth"
import CredentialsProvider from "next-auth/providers/credentials"
import axios from "axios"

// Create a server-side API instance that uses the internal backend URL
const serverApi = axios.create({
  baseURL: process.env.INTERNAL_BACKEND_URL 
    ? `${process.env.INTERNAL_BACKEND_URL}/api/v1`
    : 'http://127.0.0.1:8000/api/v1'
});

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
          console.log('NextAuth authorize: Attempting login with backend URL:', serverApi.defaults.baseURL)
          
          // request access token from backend
          const params = new URLSearchParams()
          params.append('username', credentials?.username || '')
          params.append('password', credentials?.password || '')
          const tokenRes = await serverApi.post('/auth/login/access-token', params, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
          })
          const { access_token: accessToken } = tokenRes.data
          
          console.log('NextAuth authorize: Successfully obtained access token')
          
          // set auth header for subsequent calls
          serverApi.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`
          
          // fetch current user
          const userRes = await serverApi.get('/auth/me')
          console.log('NextAuth authorize: Successfully fetched user data')
          
          return { ...userRes.data, accessToken }
        } catch (error: any) {
          console.error('NextAuth authorize error:', error.message)
          if (error.response) {
            console.error('Response status:', error.response.status)
            console.error('Response data:', error.response.data)
          }
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