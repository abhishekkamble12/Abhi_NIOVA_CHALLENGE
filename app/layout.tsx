import type { Metadata, Viewport } from 'next'
import './globals.css'

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
}

export const metadata: Metadata = {
  title: 'Racing Demo | High-Performance Frontend',
  description: 'Motorsport-inspired demo with advanced animations and 3D effects',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-racing-dark text-white font-racing antialiased">
        {children}
      </body>
    </html>
  )
}