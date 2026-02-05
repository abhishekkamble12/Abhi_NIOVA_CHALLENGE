'use client'

import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'

export default function OffTrack() {
  const sectionRef = useRef(null)
  const isInView = useInView(sectionRef, { once: true, margin: "-100px" })

  const activities = [
    {
      title: 'GAMING',
      description: 'Professional esports and streaming',
      icon: '🎮',
      color: 'from-purple-500 to-pink-500',
      stats: '2M+ Followers'
    },
    {
      title: 'PADEL',
      description: 'Training and competitive matches',
      icon: '🎾',
      color: 'from-green-500 to-teal-500',
      stats: 'Weekly Training'
    },
    {
      title: 'CHARITY',
      description: 'Supporting youth development',
      icon: '❤️',
      color: 'from-red-500 to-orange-500',
      stats: '$500K+ Raised'
    },
    {
      title: 'CONTENT',
      description: 'Behind-the-scenes and lifestyle',
      icon: '📸',
      color: 'from-blue-500 to-cyan-500',
      stats: '50M+ Views'
    }
  ]

  const campaigns = [
    {
      brand: 'McLaren',
      title: 'Future of Racing',
      type: 'Brand Campaign',
      image: 'bg-gradient-to-br from-papaya/30 to-racing-lime/30'
    },
    {
      brand: 'Quadrant',
      title: 'Gaming Revolution',
      type: 'Content Series',
      image: 'bg-gradient-to-br from-purple-500/30 to-pink-500/30'
    },
    {
      brand: 'Sustainability',
      title: 'Green Future',
      type: 'Environmental',
      image: 'bg-gradient-to-br from-green-500/30 to-teal-500/30'
    }
  ]

  return (
    <section id="offtrack" ref={sectionRef} className="py-20 bg-racing-dark relative overflow-hidden">
      {/* Background pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute inset-0" style={{
          backgroundImage: `radial-gradient(circle at 25% 25%, rgba(210, 255, 0, 0.1) 0%, transparent 50%),
                           radial-gradient(circle at 75% 75%, rgba(255, 128, 0, 0.1) 0%, transparent 50%)`
        }} />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-5xl md:text-7xl font-display font-black text-white mb-4">
            OFF <span className="text-papaya text-glow">TRACK</span>
          </h2>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Beyond the circuit. Exploring passions, building communities, making impact.
          </p>
        </motion.div>

        {/* Activities grid */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={isInView ? { opacity: 1 } : {}}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16"
        >
          {activities.map((activity, index) => (
            <motion.div
              key={activity.title}
              initial={{ opacity: 0, y: 50 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.3 + index * 0.1 }}
              className="group relative overflow-hidden rounded-2xl bg-racing-gray/30 backdrop-blur-sm border border-gray-700/50 hover:border-racing-lime/50 transition-all duration-500"
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${activity.color} opacity-0 group-hover:opacity-10 transition-opacity duration-500`} />
              
              <div className="relative p-6 h-full flex flex-col">
                <div className="text-4xl mb-4 group-hover:scale-110 transition-transform duration-300">
                  {activity.icon}
                </div>
                
                <h3 className="text-xl font-display font-bold text-white mb-2 group-hover:text-racing-lime transition-colors">
                  {activity.title}
                </h3>
                
                <p className="text-gray-400 text-sm mb-4 flex-grow">
                  {activity.description}
                </p>
                
                <div className="text-racing-lime font-semibold text-sm">
                  {activity.stats}
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Campaigns section */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="mb-16"
        >
          <h3 className="text-3xl font-display font-bold text-white mb-8 text-center">
            RECENT <span className="text-papaya">CAMPAIGNS</span>
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {campaigns.map((campaign, index) => (
              <motion.div
                key={campaign.title}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={isInView ? { opacity: 1, scale: 1 } : {}}
                transition={{ duration: 0.6, delay: 0.8 + index * 0.1 }}
                className="group relative overflow-hidden rounded-xl bg-racing-gray/30 backdrop-blur-sm border border-gray-700/50 hover:border-racing-lime/50 transition-all duration-500 cursor-pointer"
              >
                <div className={`aspect-video ${campaign.image} relative`}>
                  <div className="absolute inset-0 bg-black/20 group-hover:bg-black/10 transition-colors duration-300" />
                  <div className="absolute top-4 left-4">
                    <span className="px-3 py-1 bg-black/50 backdrop-blur-sm rounded-full text-xs text-white font-medium">
                      {campaign.type}
                    </span>
                  </div>
                </div>
                
                <div className="p-6">
                  <div className="text-sm text-racing-lime font-semibold mb-1">
                    {campaign.brand}
                  </div>
                  <h4 className="text-lg font-bold text-white group-hover:text-racing-lime transition-colors">
                    {campaign.title}
                  </h4>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Social stats */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 1 }}
          className="bg-gradient-to-r from-racing-lime/10 to-papaya/10 border border-racing-lime/20 rounded-2xl p-8 text-center"
        >
          <h3 className="text-2xl font-display font-bold text-white mb-6">
            SOCIAL <span className="text-racing-lime">IMPACT</span>
          </h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <div className="text-3xl font-display font-black text-racing-lime mb-1">
                15M+
              </div>
              <div className="text-sm text-gray-400 tracking-wider">
                TOTAL FOLLOWERS
              </div>
            </div>
            <div>
              <div className="text-3xl font-display font-black text-papaya mb-1">
                500M+
              </div>
              <div className="text-sm text-gray-400 tracking-wider">
                CONTENT VIEWS
              </div>
            </div>
            <div>
              <div className="text-3xl font-display font-black text-racing-lime mb-1">
                2.5M
              </div>
              <div className="text-sm text-gray-400 tracking-wider">
                ENGAGEMENT RATE
              </div>
            </div>
            <div>
              <div className="text-3xl font-display font-black text-papaya mb-1">
                95%
              </div>
              <div className="text-sm text-gray-400 tracking-wider">
                POSITIVE SENTIMENT
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Floating elements */}
      <motion.div
        animate={{ 
          y: [0, -20, 0],
          rotate: [0, 5, 0]
        }}
        transition={{ 
          duration: 6, 
          repeat: Infinity, 
          ease: "easeInOut"
        }}
        className="absolute top-1/4 right-10 w-4 h-4 bg-papaya rounded-full opacity-60"
      />
      
      <motion.div
        animate={{ 
          y: [0, 15, 0],
          rotate: [0, -3, 0]
        }}
        transition={{ 
          duration: 8, 
          repeat: Infinity, 
          ease: "easeInOut",
          delay: 2
        }}
        className="absolute bottom-1/4 left-10 w-3 h-3 bg-racing-lime rounded-full opacity-40"
      />
    </section>
  )
}