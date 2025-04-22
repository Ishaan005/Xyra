import { Github, Mail, Twitter } from "lucide-react"
import Link from "next/link"

export function Footer() {
  return (
    <footer className="bg-gray-dark text-white py-12">
      <div className="container mx-auto px-4 md:px-6">
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          <div>
            <h3 className="text-xl font-bold mb-4">Business Engine</h3>
            <p className="text-gray-40">The plug-and-play monetization layer for AI SaaS platforms.</p>
          </div>

          <div>
            <h4 className="font-bold mb-4">Product</h4>
            <ul className="space-y-2">
              <li>
                <Link href="#" className="hover:text-gold transition-colors">
                  Features
                </Link>
              </li>
              <li>
                <Link href="#" className="hover:text-gold transition-colors">
                  Pricing
                </Link>
              </li>
              <li>
                <Link href="#" className="hover:text-gold transition-colors">
                  Documentation
                </Link>
              </li>
              <li>
                <Link href="#" className="hover:text-gold transition-colors">
                  API Reference
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="font-bold mb-4">Company</h4>
            <ul className="space-y-2">
              <li>
                <Link href="#" className="hover:text-gold transition-colors">
                  About
                </Link>
              </li>
              <li>
                <Link href="#" className="hover:text-gold transition-colors">
                  Blog
                </Link>
              </li>
              <li>
                <Link href="#" className="hover:text-gold transition-colors">
                  Careers
                </Link>
              </li>
              <li>
                <Link href="#" className="hover:text-gold transition-colors">
                  Contact
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="font-bold mb-4">Connect</h4>
            <div className="flex gap-4">
              <Link href="#" className="hover:text-gold transition-colors">
                <Github className="h-6 w-6" />
                <span className="sr-only">GitHub</span>
              </Link>
              <Link href="#" className="hover:text-gold transition-colors">
                <Twitter className="h-6 w-6" />
                <span className="sr-only">Twitter</span>
              </Link>
              <Link href="#" className="hover:text-gold transition-colors">
                <Mail className="h-6 w-6" />
                <span className="sr-only">Email</span>
              </Link>
            </div>
          </div>
        </div>

        <div className="mt-12 border-t border-gray-80 pt-8 text-center text-sm text-gray-60">
          <p>© {new Date().getFullYear()} Business Engine. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}
