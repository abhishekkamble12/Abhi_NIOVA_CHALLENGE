'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface OrchestratorStep {
  name: string
  status: 'pending' | 'running' | 'complete' | 'blocked'
  description: string
}

interface TelemetryEvent {
  event_type: string
  timestamp: string
  payload: Record<string, any>
}

export default function OrchestratorDemo() {
  const [query, setQuery] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [steps, setSteps] = useState<OrchestratorStep[]>([
    { name: 'Parse Input', status: 'pending', description: 'Detect intent & normalize' },
    { name: 'Safety Check', status: 'pending', description: 'Guardrail validation' },
    { name: 'Context Retrieval', status: 'pending', description: 'Load user data' },
    { name: 'Reasoning', status: 'pending', description: 'LLM thinks' },
    { name: 'Execute Action', status: 'pending', description: 'Call service' },
    { name: 'Filter Output', status: 'pending', description: 'Validate & format' },
    { name: 'Cache Decision', status: 'pending', description: 'Prepare response' },
  ])
  const [tokens, setTokens] = useState<string[]>([])
  const [telemetry, setTelemetry] = useState<TelemetryEvent[]>([])
  const [finalResponse, setFinalResponse] = useState('')
  const [requestId, setRequestId] = useState('')
  const wsRef = useRef<WebSocket | null>(null)
  const tokensEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll tokens to bottom
  useEffect(() => {
    tokensEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [tokens])

  const startProcessing = async () => {
    if (!query.trim()) return

    setIsProcessing(true)
    setTokens([])
    setTelemetry([])
    setFinalResponse('')
    setSteps(steps.map(s => ({ ...s, status: 'pending' })))

    try {
      const uri = `ws://localhost:8000/api/v1/orchestrator/stream`
      const ws = new WebSocket(uri)
      wsRef.current = ws

      ws.onopen = () => {
        setIsConnected(true)
        ws.send(JSON.stringify({
          user_id: 'demo_user',
          input_text: query,
          input_type: 'text',
        }))
      }

      ws.onmessage = (event) => {
        const message = JSON.parse(event.data)

        if (message.type === 'telemetry') {
          const ev = message.payload as TelemetryEvent
          setTelemetry(prev => [...prev, ev])

          // Update step status based on telemetry event
          updateStepFromEvent(ev)
        } else if (message.type === 'token') {
          setTokens(prev => [...prev, message.payload])
          setFinalResponse(prev => prev + ' ' + message.payload)
        } else if (message.type === 'done') {
          setRequestId(message.payload.request_id || 'unknown')
          ws.close()
          setIsConnected(false)
          setIsProcessing(false)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setIsConnected(false)
        setIsProcessing(false)
      }

      ws.onclose = () => {
        setIsConnected(false)
        setIsProcessing(false)
      }
    } catch (error) {
      console.error('Failed to connect:', error)
      setIsProcessing(false)
    }
  }

  const updateStepFromEvent = (event: TelemetryEvent) => {
    const stepMap: Record<string, number> = {
      parse_input: 0,
      safety_check: 1,
      context_retrieved: 2,
      reasoning_complete: 3,
      content_generated: 4,
      news_fetched: 4,
      video_analyzed: 4,
      action_executed: 4,
      output_filtered: 5,
      cache_decision: 6,
    }

    const stepIndex = stepMap[event.event_type]
    if (stepIndex !== undefined) {
      setSteps(prev => {
        const updated = [...prev]
        updated[stepIndex].status = 'complete'
        // Mark next step as running if not the last one
        if (stepIndex < updated.length - 1) {
          updated[stepIndex + 1].status = 'running'
        }
        return updated
      })
    }

    // Check for safety block
    if (event.event_type === 'safety_block') {
      setSteps(prev => {
        const updated = [...prev]
        updated[1].status = 'blocked'
        return updated
      })
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <h1 className="text-4xl font-bold text-white mb-2">
            🚀 AI Orchestrator Demo
          </h1>
          <p className="text-gray-400">
            Watch the LangGraph orchestrator process your request in real-time
          </p>
        </motion.div>

        {/* Input Section */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="bg-white/10 backdrop-blur border border-white/20 rounded-lg p-6 mb-8"
        >
          <label className="block text-sm font-semibold text-white mb-3">
            Your Query
          </label>
          <div className="flex gap-3">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && startProcessing()}
              placeholder="e.g., Generate an Instagram post about AI"
              className="flex-1 bg-slate-800/50 border border-white/20 rounded px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
              disabled={isProcessing}
            />
            <button
              onClick={startProcessing}
              disabled={isProcessing || !query.trim()}
              className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold rounded hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              {isProcessing ? 'Processing...' : 'Send'}
            </button>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Orchestrator Flow */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white/10 backdrop-blur border border-white/20 rounded-lg p-6"
          >
            <h2 className="text-lg font-bold text-white mb-4">
              📊 Orchestrator Flow
            </h2>
            <div className="space-y-3">
              <AnimatePresence>
                {steps.map((step, idx) => (
                  <motion.div
                    key={`step-${idx}`}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    className={`p-3 rounded border transition-all ${
                      step.status === 'complete'
                        ? 'bg-green-500/20 border-green-500/50'
                        : step.status === 'running'
                          ? 'bg-blue-500/20 border-blue-500/50 ring-1 ring-blue-500'
                          : step.status === 'blocked'
                            ? 'bg-red-500/20 border-red-500/50'
                            : 'bg-slate-800/30 border-white/10'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className="flex-shrink-0">
                        {step.status === 'complete' && (
                          <span className="text-green-400">✓</span>
                        )}
                        {step.status === 'running' && (
                          <motion.span
                            animate={{ rotate: 360 }}
                            transition={{
                              duration: 1,
                              repeat: Infinity,
                              ease: 'linear',
                            }}
                            className="text-blue-400 inline-block"
                          >
                            ⚙️
                          </motion.span>
                        )}
                        {step.status === 'blocked' && <span className="text-red-400">⛔</span>}
                        {step.status === 'pending' && <span className="text-gray-400">○</span>}
                      </div>
                      <div className="flex-1">
                        <p className="text-white font-medium">{step.name}</p>
                        <p className="text-gray-400 text-xs">{step.description}</p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>

            {requestId && (
              <div className="mt-4 pt-4 border-t border-white/10">
                <p className="text-xs text-gray-400">
                  Request ID: <span className="text-purple-400">{requestId}</span>
                </p>
              </div>
            )}
          </motion.div>

          {/* Telemetry Log */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white/10 backdrop-blur border border-white/20 rounded-lg p-6"
          >
            <h2 className="text-lg font-bold text-white mb-4">
              📡 Telemetry Events
            </h2>
            <div className="h-64 overflow-y-auto space-y-2 bg-slate-900/50 rounded p-3">
              {telemetry.length === 0 ? (
                <p className="text-gray-500 text-sm">Waiting for events...</p>
              ) : (
                telemetry.map((event, idx) => (
                  <motion.div
                    key={`telemetry-${idx}`}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="text-xs text-gray-300 font-mono bg-slate-800/50 p-2 rounded border border-white/5"
                  >
                    <span className="text-purple-400">{event.event_type}</span>
                    {event.payload.success === false && (
                      <span className="ml-2 text-red-400">❌ failed</span>
                    )}
                  </motion.div>
                ))
              )}
              <div ref={tokensEndRef} />
            </div>
          </motion.div>
        </div>

        {/* Token Stream & Final Response */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-8 bg-white/10 backdrop-blur border border-white/20 rounded-lg p-6"
        >
          <h2 className="text-lg font-bold text-white mb-4">
            ✨ Response Stream
          </h2>
          <div className="min-h-24 bg-slate-900/50 rounded p-4 space-y-4">
            {tokens.length > 0 ? (
              <>
                <div>
                  <p className="text-xs text-gray-400 mb-2">Tokens:</p>
                  <div className="flex flex-wrap gap-2">
                    <AnimatePresence>
                      {tokens.map((token, idx) => (
                        <motion.span
                          key={`token-${idx}`}
                          initial={{ opacity: 0, scale: 0.8 }}
                          animate={{ opacity: 1, scale: 1 }}
                          className="inline-block px-2 py-1 bg-gradient-to-r from-purple-500/50 to-pink-500/50 text-white text-sm rounded"
                        >
                          {token}
                        </motion.span>
                      ))}
                    </AnimatePresence>
                  </div>
                </div>
                {finalResponse && (
                  <div>
                    <p className="text-xs text-gray-400 mb-2">Full Response:</p>
                    <p className="text-white text-sm leading-relaxed">
                      {finalResponse.trim()}
                    </p>
                  </div>
                )}
              </>
            ) : (
              <p className="text-gray-500 text-sm">Send a query to see the response...</p>
            )}
          </div>
        </motion.div>

        {/* Status Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="mt-8 text-center text-sm text-gray-400"
        >
          <p>
            Status:{' '}
            <span
              className={`font-semibold ${
                isConnected ? 'text-green-400' : 'text-gray-500'
              }`}
            >
              {isConnected ? '🟢 Connected' : '⚪ Disconnected'}
            </span>
          </p>
        </motion.div>
      </div>
    </div>
  )
}
