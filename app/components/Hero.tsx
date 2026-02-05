'use client'

import { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import * as THREE from 'three'

export default function Hero() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const sceneRef = useRef<THREE.Scene>()
  const rendererRef = useRef<THREE.WebGLRenderer>()
  const cameraRef = useRef<THREE.PerspectiveCamera>()
  const helmetRef = useRef<THREE.Mesh>()

  useEffect(() => {
    if (!canvasRef.current) return

    // Scene setup
    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000)
    const renderer = new THREE.WebGLRenderer({ 
      canvas: canvasRef.current, 
      alpha: true,
      antialias: true 
    })

    renderer.setSize(window.innerWidth, window.innerHeight)
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))

    // Create helmet geometry (simplified)
    const geometry = new THREE.SphereGeometry(1, 32, 32)
    const material = new THREE.MeshPhongMaterial({ 
      color: 0xD2FF00,
      shininess: 100,
      transparent: true,
      opacity: 0.8
    })
    const helmet = new THREE.Mesh(geometry, material)
    scene.add(helmet)

    // Lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 0.6)
    scene.add(ambientLight)

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1)
    directionalLight.position.set(5, 5, 5)
    scene.add(directionalLight)

    const pointLight = new THREE.PointLight(0xD2FF00, 1, 100)
    pointLight.position.set(0, 0, 10)
    scene.add(pointLight)

    camera.position.z = 5

    // Store refs
    sceneRef.current = scene
    rendererRef.current = renderer
    cameraRef.current = camera
    helmetRef.current = helmet

    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate)
      
      if (helmetRef.current) {
        helmetRef.current.rotation.y += 0.01
        helmetRef.current.rotation.x += 0.005
      }
      
      renderer.render(scene, camera)
    }
    animate()

    // Handle resize
    const handleResize = () => {
      if (cameraRef.current && rendererRef.current) {
        cameraRef.current.aspect = window.innerWidth / window.innerHeight
        cameraRef.current.updateProjectionMatrix()
        rendererRef.current.setSize(window.innerWidth, window.innerHeight)
      }
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      renderer.dispose()
    }
  }, [])

  const textVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: (i: number) => ({
      opacity: 1,
      y: 0,
      transition: {
        delay: 2.5 + i * 0.2,
        duration: 0.8,
        ease: "easeOut"
      }
    })
  }

  return (
    <section className="relative h-screen flex items-center justify-center overflow-hidden">
      {/* 3D Canvas Background */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full"
        style={{ background: 'transparent' }}
      />

      {/* Grid overlay */}
      <div className="absolute inset-0 racing-grid opacity-10" />

      {/* Content */}
      <div className="relative z-10 text-center px-4 max-w-6xl mx-auto">
        <motion.div
          initial="hidden"
          animate="visible"
          className="space-y-6"
        >
          {/* Main headline */}
          <motion.h1
            custom={0}
            variants={textVariants}
            className="hero-text font-display font-black text-6xl md:text-8xl lg:text-9xl leading-none"
          >
            <span className="text-white">REDEFINING</span>
            <br />
            <span className="text-racing-lime text-glow">LIMITS</span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            custom={1}
            variants={textVariants}
            className="text-xl md:text-2xl text-gray-300 max-w-3xl mx-auto leading-relaxed"
          >
            High-performance frontend engineering meets motorsport precision.
            <br />
            <span className="text-racing-lime">Built for speed. Designed for impact.</span>
          </motion.p>

          {/* Stats */}
          <motion.div
            custom={2}
            variants={textVariants}
            className="flex flex-wrap justify-center gap-8 md:gap-16 mt-12"
          >
            <div className="text-center">
              <div className="text-3xl md:text-4xl font-display font-bold text-racing-lime">
                <motion.span
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 3.5, duration: 2 }}
                >
                  99.9%
                </motion.span>
              </div>
              <div className="text-sm text-gray-400 tracking-wider">UPTIME</div>
            </div>
            <div className="text-center">
              <div className="text-3xl md:text-4xl font-display font-bold text-papaya">
                <motion.span
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 3.7, duration: 2 }}
                >
                  &lt;100ms
                </motion.span>
              </div>
              <div className="text-sm text-gray-400 tracking-wider">RESPONSE</div>
            </div>
            <div className="text-center">
              <div className="text-3xl md:text-4xl font-display font-bold text-racing-lime">
                <motion.span
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 3.9, duration: 2 }}
                >
                  100
                </motion.span>
              </div>
              <div className="text-sm text-gray-400 tracking-wider">LIGHTHOUSE</div>
            </div>
          </motion.div>

          {/* CTA */}
          <motion.div
            custom={3}
            variants={textVariants}
            className="pt-8"
          >
            <motion.button
              whileHover={{ scale: 1.05, boxShadow: "0 0 30px rgba(210, 255, 0, 0.5)" }}
              whileTap={{ scale: 0.95 }}
              className="px-8 py-4 bg-racing-lime text-racing-dark font-bold text-lg tracking-wider rounded-none border-2 border-racing-lime hover:bg-transparent hover:text-racing-lime transition-all duration-300"
            >
              EXPLORE PERFORMANCE
            </motion.button>
          </motion.div>
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 4, duration: 1 }}
        className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
      >
        <div className="flex flex-col items-center text-gray-400">
          <span className="text-xs tracking-widest mb-2">SCROLL</span>
          <motion.div
            animate={{ y: [0, 10, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="w-px h-8 bg-racing-lime"
          />
        </div>
      </motion.div>

      {/* Racing elements */}
      <motion.div
        animate={{ 
          x: ['-100vw', '100vw'],
          opacity: [0, 1, 1, 0]
        }}
        transition={{ 
          duration: 8, 
          repeat: Infinity, 
          repeatDelay: 5,
          ease: "easeInOut"
        }}
        className="absolute top-1/4 w-2 h-2 bg-racing-lime rounded-full"
      />
    </section>
  )
}