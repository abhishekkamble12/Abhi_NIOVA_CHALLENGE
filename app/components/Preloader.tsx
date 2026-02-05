'use client'

import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export default function Preloader() {
  const [loading, setLoading] = useState(true)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const timer = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(timer)
          setTimeout(() => setLoading(false), 500)
          return 100
        }
        return prev + Math.random() * 15
      })
    }, 100)

    return () => clearInterval(timer)
  }, [])

  return (
    <AnimatePresence>
      {loading && (
        <motion.div
          initial={{ opacity: 1 }}
          exit={{ opacity: 0, scale: 1.1 }}
          transition={{ duration: 0.8, ease: "easeInOut" }}
          className="fixed inset-0 z-50 bg-racing-dark flex items-center justify-center"
        >
          <div className="text-center">
            {/* Logo/Brand */}
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="mb-8"
            >
              <h1 className="text-6xl md:text-8xl font-display font-black text-racing-lime text-glow">
                DEMO
              </h1>
              <p className="text-lg text-gray-400 mt-2 tracking-widest">
                HIGH PERFORMANCE FRONTEND
              </p>
            </motion.div>

            {/* Progress Bar */}
            <div className="w-80 max-w-sm mx-auto">
              <div className="flex justify-between text-sm text-gray-400 mb-2">
                <span>LOADING</span>
                <span>{Math.round(progress)}%</span>
              </div>
              <div className="h-1 bg-racing-gray rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-racing-lime to-papaya"
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 0.3, ease: "easeOut" }}
                />
              </div>
            </div>

            {/* Racing elements */}
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              className="absolute top-1/4 left-1/4 w-2 h-2 bg-racing-lime rounded-full opacity-60"
            />
            <motion.div
              animate={{ rotate: -360 }}
              transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
              className="absolute bottom-1/4 right-1/4 w-3 h-3 bg-papaya rounded-full opacity-40"
            />
          </div>

          {/* Grid background */}
          <div className="absolute inset-0 racing-grid opacity-20" />
        </motion.div>
      )}
    </AnimatePresence>
  )
}