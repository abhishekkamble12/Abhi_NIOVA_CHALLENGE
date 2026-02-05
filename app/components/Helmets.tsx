'use client'

import { useRef, useState } from 'react'
import { motion, useInView } from 'framer-motion'

export default function Helmets() {
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: "-100px" })
  const [selectedHelmet, setSelectedHelmet] = useState(0)

  const helmets = [
    {
      name: 'CHROME EDITION',
      description: 'Mirror finish with racing stripes',
      color: 'from-gray-400 to-gray-600',
      accent: 'racing-lime',
      year: '2026'
    },
    {
      name: 'NEON NIGHTS',
      description: 'Glow-in-the-dark racing design',
      color: 'from-racing-lime to-green-400',
      accent: 'racing-lime',
      year: '2025'
    },
    {
      name: 'PAPAYA DREAM',
      description: 'Classic McLaren heritage',
      color: 'from-papaya to-red-500',
      accent: 'papaya',
      year: '2025'
    },
    {
      name: 'CARBON FIBER',
      description: 'Lightweight performance focus',
      color: 'from-gray-800 to-black',
      accent: 'white',
      year: '2024'
    },
    {
      name: 'ELECTRIC BLUE',
      description: 'Future of motorsport',
      color: 'from-blue-500 to-cyan-400',
      accent: 'cyan-400',
      year: '2024'
    }
  ]

  return (
    <section id="helmets" ref={sectionRef} className="py-20 bg-racing-black relative overflow-hidden">
      {/* Background grid */}
      <div className="absolute inset-0 racing-grid opacity-5" />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-5xl md:text-7xl font-display font-black text-white mb-4">
            SIGNATURE <span className="text-racing-lime text-glow">HELMETS</span>
          </h2>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Each design tells a story. Every helmet represents a moment in racing history.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Helmet display */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={isInView ? { opacity: 1, scale: 1 } : {}}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="relative"
          >
            {/* Main helmet visualization */}
            <div className="relative aspect-square max-w-md mx-auto">
              <motion.div
                key={selectedHelmet}
                initial={{ rotateY: 90, opacity: 0 }}
                animate={{ rotateY: 0, opacity: 1 }}
                transition={{ duration: 0.6, type: "spring" }}
                className={`absolute inset-0 rounded-full bg-gradient-to-br ${helmets[selectedHelmet].color} shadow-2xl`}
                style={{
                  boxShadow: `0 0 60px rgba(210, 255, 0, 0.3), inset 0 0 60px rgba(255, 255, 255, 0.1)`
                }}
              >
                {/* Helmet details */}
                <div className="absolute inset-4 rounded-full border-2 border-white/20" />
                <div className="absolute top-1/3 left-1/2 transform -translate-x-1/2 w-32 h-16 bg-black/30 rounded-full" />
                <div className="absolute bottom-1/4 left-1/2 transform -translate-x-1/2 w-24 h-8 bg-white/10 rounded-full" />
              </motion.div>

              {/* Glow effect */}
              <motion.div
                animate={{ 
                  scale: [1, 1.1, 1],
                  opacity: [0.3, 0.6, 0.3]
                }}
                transition={{ 
                  duration: 3, 
                  repeat: Infinity, 
                  ease: "easeInOut"
                }}
                className={`absolute inset-0 rounded-full bg-gradient-to-br ${helmets[selectedHelmet].color} blur-xl opacity-30`}
              />
            </div>

            {/* Helmet info */}
            <motion.div
              key={selectedHelmet}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.2 }}
              className="text-center mt-8"
            >
              <h3 className="text-2xl font-display font-bold text-white mb-2">
                {helmets[selectedHelmet].name}
              </h3>
              <p className="text-gray-400 mb-4">
                {helmets[selectedHelmet].description}
              </p>
              <span className="inline-block px-4 py-2 bg-racing-lime/20 border border-racing-lime/30 rounded-full text-racing-lime text-sm font-semibold">
                {helmets[selectedHelmet].year} SEASON
              </span>
            </motion.div>
          </motion.div>

          {/* Helmet selector */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={isInView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="space-y-4"
          >
            <h3 className="text-2xl font-display font-bold text-white mb-6">
              COLLECTION
            </h3>
            
            {helmets.map((helmet, index) => (
              <motion.button
                key={helmet.name}
                initial={{ opacity: 0, x: 30 }}
                animate={isInView ? { opacity: 1, x: 0 } : {}}
                transition={{ duration: 0.6, delay: 0.6 + index * 0.1 }}
                onClick={() => setSelectedHelmet(index)}
                className={`w-full text-left p-4 rounded-xl border transition-all duration-300 group ${
                  selectedHelmet === index
                    ? 'bg-racing-lime/10 border-racing-lime/50 shadow-lg'
                    : 'bg-racing-gray/30 border-gray-700/50 hover:border-racing-lime/30'
                }`}
              >
                <div className="flex items-center space-x-4">
                  <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${helmet.color} flex-shrink-0 group-hover:scale-110 transition-transform duration-300`} />
                  
                  <div className="flex-grow">
                    <div className={`font-semibold transition-colors ${
                      selectedHelmet === index ? 'text-racing-lime' : 'text-white group-hover:text-racing-lime'
                    }`}>
                      {helmet.name}
                    </div>
                    <div className="text-sm text-gray-400">
                      {helmet.description}
                    </div>
                  </div>
                  
                  <div className="text-xs text-gray-500">
                    {helmet.year}
                  </div>
                </div>
              </motion.button>
            ))}
          </motion.div>
        </div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 0.8 }}
          className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          <div className="text-center p-6 bg-racing-gray/30 backdrop-blur-sm border border-racing-lime/20 rounded-xl">
            <div className="text-3xl font-display font-black text-racing-lime mb-2">
              25+
            </div>
            <div className="text-sm text-gray-400 tracking-wider">
              UNIQUE DESIGNS
            </div>
          </div>
          
          <div className="text-center p-6 bg-racing-gray/30 backdrop-blur-sm border border-papaya/20 rounded-xl">
            <div className="text-3xl font-display font-black text-papaya mb-2">
              5
            </div>
            <div className="text-sm text-gray-400 tracking-wider">
              CHAMPIONSHIP HELMETS
            </div>
          </div>
          
          <div className="text-center p-6 bg-racing-gray/30 backdrop-blur-sm border border-racing-lime/20 rounded-xl">
            <div className="text-3xl font-display font-black text-racing-lime mb-2">
              1.2kg
            </div>
            <div className="text-sm text-gray-400 tracking-wider">
              AVERAGE WEIGHT
            </div>
          </div>
        </motion.div>
      </div>

      {/* Animated particles */}
      {[...Array(5)].map((_, i) => (
        <motion.div
          key={i}
          animate={{ 
            y: [0, -100, 0],
            x: [0, Math.sin(i) * 50, 0],
            opacity: [0, 1, 0]
          }}
          transition={{ 
            duration: 8 + i, 
            repeat: Infinity, 
            delay: i * 2,
            ease: "easeInOut"
          }}
          className="absolute w-1 h-1 bg-racing-lime rounded-full"
          style={{
            left: `${20 + i * 15}%`,
            top: `${30 + i * 10}%`
          }}
        />
      ))}
    </section>
  )
}