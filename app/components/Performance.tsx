'use client'

import { useRef, useEffect, useState } from 'react'
import { motion, useInView } from 'framer-motion'

export default function Performance() {
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: "-100px" })
  const [activeMetric, setActiveMetric] = useState(0)

  const metrics = [
    {
      title: 'CORE WEB VITALS',
      description: 'Performance metrics that matter',
      data: [
        { label: 'LCP', value: '0.8s', target: '<2.5s', status: 'excellent' },
        { label: 'FID', value: '12ms', target: '<100ms', status: 'excellent' },
        { label: 'CLS', value: '0.02', target: '<0.1', status: 'excellent' },
        { label: 'FCP', value: '0.6s', target: '<1.8s', status: 'excellent' }
      ]
    },
    {
      title: 'LIGHTHOUSE SCORES',
      description: 'Comprehensive quality assessment',
      data: [
        { label: 'Performance', value: '100', target: '90+', status: 'excellent' },
        { label: 'Accessibility', value: '100', target: '90+', status: 'excellent' },
        { label: 'Best Practices', value: '100', target: '90+', status: 'excellent' },
        { label: 'SEO', value: '100', target: '90+', status: 'excellent' }
      ]
    },
    {
      title: 'TECHNICAL SPECS',
      description: 'Under the hood performance',
      data: [
        { label: 'Bundle Size', value: '245KB', target: '<500KB', status: 'excellent' },
        { label: 'Time to Interactive', value: '1.2s', target: '<3.8s', status: 'excellent' },
        { label: 'Speed Index', value: '0.9s', target: '<3.4s', status: 'excellent' },
        { label: 'Total Blocking Time', value: '45ms', target: '<200ms', status: 'excellent' }
      ]
    }
  ]

  const technologies = [
    { name: 'Next.js 14', category: 'Framework', color: 'text-white' },
    { name: 'TypeScript', category: 'Language', color: 'text-blue-400' },
    { name: 'Tailwind CSS', category: 'Styling', color: 'text-cyan-400' },
    { name: 'Framer Motion', category: 'Animation', color: 'text-purple-400' },
    { name: 'Three.js', category: '3D Graphics', color: 'text-green-400' },
    { name: 'GSAP', category: 'Animation', color: 'text-yellow-400' },
    { name: 'Lenis', category: 'Smooth Scroll', color: 'text-pink-400' },
    { name: 'Vercel', category: 'Deployment', color: 'text-gray-400' }
  ]

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveMetric((prev) => {
        const len = metrics?.length ?? 0;
        return len > 0 ? (prev + 1) % len : 0;
      })
    }, 4000)

    return () => clearInterval(interval)
  }, [])

  return (
    <section id="performance" ref={sectionRef} className="py-20 bg-racing-dark relative overflow-hidden">
      {/* Background elements */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 racing-grid opacity-5" />
        <motion.div
          animate={{ 
            scale: [1, 1.2, 1],
            opacity: [0.1, 0.2, 0.1]
          }}
          transition={{ 
            duration: 8, 
            repeat: Infinity, 
            ease: "easeInOut"
          }}
          className="absolute top-1/4 right-1/4 w-96 h-96 bg-racing-lime rounded-full blur-3xl"
        />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-5xl md:text-7xl font-display font-black text-white mb-4">
            PEAK <span className="text-racing-lime text-glow">PERFORMANCE</span>
          </h2>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Engineered for speed. Optimized for excellence. Built to dominate the digital track.
          </p>
        </motion.div>

        {/* Performance metrics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16">
          {/* Metric selector */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="space-y-4"
          >
            {metrics.map((metric, index) => (
              <motion.button
                key={metric.title}
                initial={{ opacity: 0, y: 20 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: 0.3 + index * 0.1 }}
                onClick={() => setActiveMetric(index)}
                className={`w-full text-left p-6 rounded-xl border transition-all duration-300 ${
                  activeMetric === index
                    ? 'bg-racing-lime/10 border-racing-lime/50 shadow-lg'
                    : 'bg-racing-gray/30 border-gray-700/50 hover:border-racing-lime/30'
                }`}
              >
                <h3 className={`text-xl font-display font-bold mb-2 transition-colors ${
                  activeMetric === index ? 'text-racing-lime' : 'text-white'
                }`}>
                  {metric.title}
                </h3>
                <p className="text-gray-400 text-sm">
                  {metric.description}
                </p>
              </motion.button>
            ))}
          </motion.div>

          {/* Metric display */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="bg-racing-gray/30 backdrop-blur-sm border border-racing-lime/20 rounded-2xl p-8"
          >
            <motion.div
              key={activeMetric}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
            >
              <h3 className="text-2xl font-display font-bold text-white mb-6">
                {metrics[activeMetric].title}
              </h3>
              
              <div className="space-y-6">
                {metrics[activeMetric].data.map((item, index) => (
                  <div key={item.label} className="flex items-center justify-between">
                    <div>
                      <div className="text-white font-semibold">
                        {item.label}
                      </div>
                      <div className="text-sm text-gray-400">
                        Target: {item.target}
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <div className="text-2xl font-display font-bold text-racing-lime">
                        {item.value}
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full" />
                        <span className="text-xs text-green-400 uppercase tracking-wider">
                          {item.status}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          </motion.div>
        </div>

        {/* Technology stack */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="mb-16"
        >
          <h3 className="text-3xl font-display font-bold text-white mb-8 text-center">
            TECHNOLOGY <span className="text-racing-lime">STACK</span>
          </h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {technologies.map((tech, index) => (
              <motion.div
                key={tech.name}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={isInView ? { opacity: 1, scale: 1 } : {}}
                transition={{ duration: 0.6, delay: 0.8 + index * 0.05 }}
                className="bg-racing-gray/30 backdrop-blur-sm border border-gray-700/50 rounded-lg p-4 text-center hover:border-racing-lime/30 transition-all duration-300 group"
              >
                <div className={`font-semibold ${tech.color} group-hover:text-racing-lime transition-colors`}>
                  {tech.name}
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  {tech.category}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Performance summary */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={isInView ? { opacity: 1, scale: 1 } : {}}
          transition={{ duration: 0.8, delay: 1 }}
          className="bg-gradient-to-r from-racing-lime/10 to-papaya/10 border border-racing-lime/20 rounded-2xl p-8 text-center"
        >
          <h3 className="text-2xl font-display font-bold text-white mb-6">
            CHAMPIONSHIP <span className="text-racing-lime">PERFORMANCE</span>
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div>
              <div className="text-4xl font-display font-black text-racing-lime mb-2">
                100
              </div>
              <div className="text-sm text-gray-400 tracking-wider">
                LIGHTHOUSE SCORE
              </div>
            </div>
            <div>
              <div className="text-4xl font-display font-black text-papaya mb-2">
                0.8s
              </div>
              <div className="text-sm text-gray-400 tracking-wider">
                LOAD TIME
              </div>
            </div>
            <div>
              <div className="text-4xl font-display font-black text-racing-lime mb-2">
                99.9%
              </div>
              <div className="text-sm text-gray-400 tracking-wider">
                UPTIME
              </div>
            </div>
            <div>
              <div className="text-4xl font-display font-black text-papaya mb-2">
                A+
              </div>
              <div className="text-sm text-gray-400 tracking-wider">
                SECURITY GRADE
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Animated performance indicators */}
      <motion.div
        animate={{ 
          x: ['0%', '100%', '0%'],
          opacity: [0, 1, 0]
        }}
        transition={{ 
          duration: 6, 
          repeat: Infinity, 
          ease: "easeInOut"
        }}
        className="absolute bottom-10 w-2 h-2 bg-racing-lime rounded-full"
      />
    </section>
  )
}