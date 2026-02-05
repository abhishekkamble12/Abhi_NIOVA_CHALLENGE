'use client'

import { motion } from 'framer-motion'

export default function Footer() {
  const socialLinks = [
    { name: 'Instagram', href: '#', icon: '📸' },
    { name: 'Twitter', href: '#', icon: '🐦' },
    { name: 'YouTube', href: '#', icon: '📺' },
    { name: 'Twitch', href: '#', icon: '🎮' },
    { name: 'TikTok', href: '#', icon: '🎵' }
  ]

  const quickLinks = [
    { name: 'About', href: '#' },
    { name: 'Racing', href: '#ontrack' },
    { name: 'Lifestyle', href: '#offtrack' },
    { name: 'Helmets', href: '#helmets' },
    { name: 'Performance', href: '#performance' }
  ]

  const legalLinks = [
    { name: 'Privacy Policy', href: '#' },
    { name: 'Terms of Service', href: '#' },
    { name: 'Cookie Policy', href: '#' },
    { name: 'Contact', href: '#' }
  ]

  return (
    <footer className="bg-racing-black border-t border-racing-lime/20 relative overflow-hidden">
      {/* Background elements */}
      <div className="absolute inset-0 racing-grid opacity-5" />
      <motion.div
        animate={{ 
          scale: [1, 1.1, 1],
          opacity: [0.05, 0.1, 0.05]
        }}
        transition={{ 
          duration: 10, 
          repeat: Infinity, 
          ease: "easeInOut"
        }}
        className="absolute -top-1/2 -right-1/2 w-full h-full bg-racing-lime rounded-full blur-3xl"
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 relative z-10">
        {/* Main footer content */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
          {/* Brand section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="lg:col-span-2"
          >
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-12 h-12 bg-gradient-to-br from-racing-lime to-papaya rounded-xl flex items-center justify-center">
                <span className="text-2xl font-display font-black text-racing-dark">
                  D
                </span>
              </div>
              <div>
                <h3 className="text-2xl font-display font-black text-white">
                  DEMO RACING
                </h3>
                <p className="text-sm text-gray-400">
                  High-Performance Frontend
                </p>
              </div>
            </div>
            
            <p className="text-gray-400 mb-6 max-w-md">
              Pushing the boundaries of web performance and user experience. 
              Built with cutting-edge technology and motorsport precision.
            </p>
            
            {/* Social links */}
            <div className="flex space-x-4">
              {socialLinks.map((social) => (
                <motion.a
                  key={social.name}
                  href={social.href}
                  whileHover={{ scale: 1.1, y: -2 }}
                  whileTap={{ scale: 0.95 }}
                  className="w-10 h-10 bg-racing-gray/50 hover:bg-racing-lime/20 border border-gray-700/50 hover:border-racing-lime/50 rounded-lg flex items-center justify-center transition-all duration-300 group"
                  aria-label={social.name}
                >
                  <span className="text-lg group-hover:scale-110 transition-transform">
                    {social.icon}
                  </span>
                </motion.a>
              ))}
            </div>
          </motion.div>

          {/* Quick links */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <h4 className="text-lg font-display font-bold text-white mb-6">
              QUICK LINKS
            </h4>
            <ul className="space-y-3">
              {quickLinks.map((link) => (
                <li key={link.name}>
                  <motion.a
                    href={link.href}
                    whileHover={{ x: 5 }}
                    className="text-gray-400 hover:text-racing-lime transition-colors duration-200 text-sm"
                  >
                    {link.name}
                  </motion.a>
                </li>
              ))}
            </ul>
          </motion.div>

          {/* Legal links */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <h4 className="text-lg font-display font-bold text-white mb-6">
              LEGAL
            </h4>
            <ul className="space-y-3">
              {legalLinks.map((link) => (
                <li key={link.name}>
                  <motion.a
                    href={link.href}
                    whileHover={{ x: 5 }}
                    className="text-gray-400 hover:text-racing-lime transition-colors duration-200 text-sm"
                  >
                    {link.name}
                  </motion.a>
                </li>
              ))}
            </ul>
          </motion.div>
        </div>

        {/* Newsletter signup */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="bg-racing-gray/30 backdrop-blur-sm border border-racing-lime/20 rounded-2xl p-8 mb-12"
        >
          <div className="text-center mb-6">
            <h4 className="text-2xl font-display font-bold text-white mb-2">
              STAY IN THE <span className="text-racing-lime">FAST LANE</span>
            </h4>
            <p className="text-gray-400">
              Get the latest updates on performance optimizations and racing insights.
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
            <input
              type="email"
              placeholder="Enter your email"
              className="flex-1 px-4 py-3 bg-racing-dark/50 border border-gray-700/50 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-racing-lime/50 transition-colors"
            />
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-6 py-3 bg-racing-lime text-racing-dark font-bold rounded-lg hover:bg-racing-lime/90 transition-colors"
            >
              SUBSCRIBE
            </motion.button>
          </div>
        </motion.div>

        {/* Bottom bar */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="flex flex-col md:flex-row items-center justify-between pt-8 border-t border-gray-700/50"
        >
          <div className="text-gray-400 text-sm mb-4 md:mb-0">
            © 2026 Demo Racing. All rights reserved. Built with ⚡ and passion.
          </div>
          
          <div className="flex items-center space-x-6 text-sm text-gray-400">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span>All systems operational</span>
            </div>
            <div>
              Version 2.0.1
            </div>
          </div>
        </motion.div>
      </div>

      {/* Animated racing line */}
      <motion.div
        animate={{ 
          scaleX: [0, 1, 0],
          opacity: [0, 1, 0]
        }}
        transition={{ 
          duration: 6, 
          repeat: Infinity, 
          repeatDelay: 4,
          ease: "easeInOut"
        }}
        className="absolute bottom-0 left-0 h-1 bg-gradient-to-r from-transparent via-racing-lime to-transparent w-full"
      />
    </footer>
  )
}