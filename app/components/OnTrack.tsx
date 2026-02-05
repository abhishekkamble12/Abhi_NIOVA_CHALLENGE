'use client'

import { useEffect, useRef } from 'react'
import { motion, useInView } from 'framer-motion'

export default function OnTrack() {
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: "-100px" })

  const stats = [
    { label: 'RACE WINS', value: '15', color: 'text-racing-lime' },
    { label: 'PODIUMS', value: '42', color: 'text-papaya' },
    { label: 'POLE POSITIONS', value: '8', color: 'text-racing-lime' },
    { label: 'FASTEST LAPS', value: '12', color: 'text-papaya' },
  ]

  const recentRaces = [
    { track: 'Monaco GP', position: '1st', points: '25', status: 'win' },
    { track: 'Spanish GP', position: '2nd', points: '18', status: 'podium' },
    { track: 'Miami GP', position: '3rd', points: '15', status: 'podium' },
    { track: 'Imola GP', position: '5th', points: '10', status: 'points' },
  ]

  return (
    <section id="ontrack" ref={sectionRef} className="py-20 bg-racing-black relative overflow-hidden">
      {/* Background elements */}
      <div className="absolute inset-0 racing-stripes opacity-5" />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-5xl md:text-7xl font-display font-black text-white mb-4">
            ON <span className="text-racing-lime text-glow">TRACK</span>
          </h2>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Performance metrics that matter. Every lap, every sector, every millisecond counts.
          </p>
        </motion.div>

        {/* Stats grid */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16"
        >
          {stats.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={isInView ? { opacity: 1, scale: 1 } : {}}
              transition={{ duration: 0.6, delay: 0.3 + index * 0.1 }}
              className="bg-racing-gray/50 backdrop-blur-sm border border-racing-lime/20 rounded-lg p-6 text-center hover:border-racing-lime/50 transition-all duration-300 group"
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={isInView ? { scale: 1 } : {}}
                transition={{ duration: 0.8, delay: 0.5 + index * 0.1, type: "spring" }}
                className={`text-4xl md:text-5xl font-display font-black ${stat.color} mb-2 group-hover:scale-110 transition-transform duration-300`}
              >
                {stat.value}
              </motion.div>
              <div className="text-sm text-gray-400 tracking-widest font-medium">
                {stat.label}
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Recent races */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="bg-racing-gray/30 backdrop-blur-sm border border-racing-lime/20 rounded-2xl p-8"
        >
          <h3 className="text-3xl font-display font-bold text-white mb-8 text-center">
            RECENT <span className="text-racing-lime">PERFORMANCE</span>
          </h3>
          
          <div className="space-y-4">
            {recentRaces.map((race, index) => (
              <motion.div
                key={race.track}
                initial={{ opacity: 0, x: -50 }}
                animate={isInView ? { opacity: 1, x: 0 } : {}}
                transition={{ duration: 0.6, delay: 0.6 + index * 0.1 }}
                className="flex items-center justify-between p-4 bg-racing-dark/50 rounded-lg border border-gray-700/50 hover:border-racing-lime/30 transition-all duration-300 group"
              >
                <div className="flex items-center space-x-4">
                  <div className={`w-3 h-3 rounded-full ${
                    race.status === 'win' ? 'bg-racing-lime glow-lime' :
                    race.status === 'podium' ? 'bg-papaya glow-papaya' :
                    'bg-gray-500'
                  }`} />
                  <div>
                    <div className="font-semibold text-white group-hover:text-racing-lime transition-colors">
                      {race.track}
                    </div>
                    <div className="text-sm text-gray-400">
                      Position: {race.position}
                    </div>
                  </div>
                </div>
                
                <div className="text-right">
                  <div className="font-bold text-racing-lime text-lg">
                    {race.points}
                  </div>
                  <div className="text-xs text-gray-400">
                    POINTS
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Championship position */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={isInView ? { opacity: 1, scale: 1 } : {}}
          transition={{ duration: 0.8, delay: 0.8 }}
          className="mt-12 text-center"
        >
          <div className="inline-flex items-center space-x-4 bg-gradient-to-r from-racing-lime/20 to-papaya/20 border border-racing-lime/30 rounded-full px-8 py-4">
            <div className="text-sm text-gray-300 tracking-widest">
              CHAMPIONSHIP POSITION
            </div>
            <div className="text-4xl font-display font-black text-racing-lime">
              P1
            </div>
            <div className="text-sm text-gray-300">
              342 PTS
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
          duration: 4, 
          repeat: Infinity, 
          repeatDelay: 2,
          ease: "easeInOut"
        }}
        className="absolute bottom-0 left-0 h-1 bg-gradient-to-r from-transparent via-racing-lime to-transparent w-full"
      />
    </section>
  )
}