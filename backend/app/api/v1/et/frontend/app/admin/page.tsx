"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function AdminRedirect() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/admin_dashboard");
  }, [router]);

  return <div className="min-h-screen flex items-center justify-center">Redirecting to admin dashboard...</div>;
}
'use client'

import { useState, useEffect, useRef } from 'react'
import Link from 'next/link'
import { ArrowLeft, Activity, Users, Shield, AlertTriangle, CheckCircle, XCircle } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts'

interface TelemetryEvent {
  type: string
  timestamp: string
  data: any
}

interface SystemStats {
  uptime: string
  total_requests: number
  active_connections: number
  recent_events: TelemetryEvent[]
  ai_pipeline_stats: any
}

export default function AdminPage() {
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null)
  const [telemetryEvents, setTelemetryEvents] = useState<TelemetryEvent[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [pipelineStatus, setPipelineStatus] = useState<any>(null)
  const wsRef = useRef<WebSocket | null>(null)

  // Mock data for charts
  const requestsData = [
    { time: '10:00', requests: 12, threats: 2 },
    { time: '10:15', requests: 19, threats: 1 },
    { time: '10:30', requests: 15, threats: 3 },
    { time: '10:45', requests: 22, threats: 0 },
    { time: '11:00', requests: 18, threats: 1 },
    { time: '11:15', requests: 25, threats: 2 },
  ]

  const languageData = [
    { name: 'Hindi', value: 65, color: '#DAA520' },
    { name: 'English', value: 25, color: '#0066CC' },
    { name: 'Bengali', value: 7, color: '#059669' },
    { name: 'Others', value: 3, color: '#DC2626' },
  ]

  const intentData = [
    { intent: 'Cybersecurity Education', count: 45 },
    { intent: 'Threat Report', count: 23 },
    { intent: 'General Query', count: 18 },
    { intent: 'Emergency', count: 8 },
  ]

  useEffect(() => {
    // Fetch initial system stats
    fetchSystemStats()
    fetchPipelineStatus()

    // Setup WebSocket connection for real-time telemetry
    connectWebSocket()

    // Cleanup on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  const fetchSystemStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/admin/stats')
      const data = await response.json()
      setSystemStats(data)
    } catch (error) {
      console.error('Failed to fetch system stats:', error)
      // Use mock data for demo
      setSystemStats({
        uptime: new Date().toISOString(),
        total_requests: 156,
        active_connections: 3,
        recent_events: [],
        ai_pipeline_stats: {
          total_processed: 42,
          avg_processing_time: 1.2,
          success_rate: 0.95,
          most_common_intent: 'cybersecurity_education'
        }
      })
    }
  }

  const fetchPipelineStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/admin/pipeline-status')
      const data = await response.json()
      setPipelineStatus(data)
    } catch (error) {
      console.error('Failed to fetch pipeline status:', error)
      // Mock pipeline status
      setPipelineStatus({
        components: {
          safety_check: { status: 'healthy' },
          intent_router: { status: 'healthy' },
          retrieve_context: { status: 'degraded' },
          generate_response: { status: 'healthy' },
          post_process: { status: 'healthy' }
        },
        external_services: {
          vector_db: { status: 'mock' },
          redis_cache: { status: 'mock' },
          stt_service: { status: 'mock' },
          tts_service: { status: 'mock' }
        }
      })
    }
  }

  const connectWebSocket = () => {
    try {
      wsRef.current = new WebSocket('ws://localhost:8000/ws/telemetry')
      
      wsRef.current.onopen = () => {
        setIsConnected(true)
        console.log('WebSocket connected')
      }

      wsRef.current.onmessage = (event) => {
        const telemetryEvent = JSON.parse(event.data)
        setTelemetryEvents(prev => [telemetryEvent, ...prev.slice(0, 49)]) // Keep last 50 events
      }

      wsRef.current.onclose = () => {
        setIsConnected(false)
        console.log('WebSocket disconnected')
        // Attempt to reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000)
      }

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error)
        setIsConnected(false)
      }
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
      setIsConnected(false)
      // Use mock events for demo
      const mockEvents = [
        { type: 'voice_processing_started', timestamp: new Date().toISOString(), data: { user_id: 'user123' } },
        { type: 'node_safety_check_completed', timestamp: new Date().toISOString(), data: { status: 'safe' } },
        { type: 'node_intent_router_completed', timestamp: new Date().toISOString(), data: { intent: 'cybersecurity_education' } },
      ]
      setTelemetryEvents(mockEvents)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle className="h-5 w-5 text-safe-green" />
      case 'degraded': return <AlertTriangle className="h-5 w-5 text-rural-gold" />
      case 'error': return <XCircle className="h-5 w-5 text-alert-red" />
      default: return <Activity className="h-5 w-5 text-gray-400" />
    }
  }

  const triggerTestEvent = async () => {
    try {
      await fetch('http://localhost:8000/api/admin/trigger-test-event', { method: 'POST' })
    } catch (error) {
      console.error('Failed to trigger test event:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-rural-green">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-md p-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center space-x-2 text-white hover:text-rural-gold transition-colors">
            <ArrowLeft className="h-5 w-5" />
            <span>Back to Home</span>
          </Link>
          <h1 className="text-2xl font-bold text-white">Admin Dashboard</h1>
          <div className="flex items-center space-x-4">
            <div className={`flex items-center space-x-2 ${isConnected ? 'text-safe-green' : 'text-alert-red'}`}>
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-safe-green' : 'bg-alert-red'} animate-pulse`}></div>
              <span className="text-sm">{isConnected ? 'Live' : 'Disconnected'}</span>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-4 pt-8">
        {/* System Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">Total Requests</p>
                <p className="text-2xl font-bold text-white">{systemStats?.total_requests || 0}</p>
              </div>
              <Activity className="h-8 w-8 text-cyber-blue" />
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">Active Connections</p>
                <p className="text-2xl font-bold text-white">{systemStats?.active_connections || 0}</p>
              </div>
              <Users className="h-8 w-8 text-safe-green" />
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">Success Rate</p>
                <p className="text-2xl font-bold text-white">{((systemStats?.ai_pipeline_stats?.success_rate || 0.95) * 100).toFixed(1)}%</p>
              </div>
              <Shield className="h-8 w-8 text-rural-gold" />
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">Avg Response Time</p>
                <p className="text-2xl font-bold text-white">{systemStats?.ai_pipeline_stats?.avg_processing_time || 1.2}s</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-alert-red" />
            </div>
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Requests Over Time */}
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
            <h3 className="text-white font-semibold mb-4">Requests & Threats Over Time</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={requestsData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="time" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1F2937', 
                    border: 'none', 
                    borderRadius: '8px',
                    color: '#F3F4F6'
                  }} 
                />
                <Line type="monotone" dataKey="requests" stroke="#0066CC" strokeWidth={2} />
                <Line type="monotone" dataKey="threats" stroke="#DC2626" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Language Distribution */}
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
            <h3 className="text-white font-semibold mb-4">Language Distribution</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={languageData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}%`}
                >
                  {languageData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Intent Analysis */}
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 mb-8">
          <h3 className="text-white font-semibold mb-4">Intent Analysis</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={intentData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="intent" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1F2937', 
                  border: 'none', 
                  borderRadius: '8px',
                  color: '#F3F4F6'
                }} 
              />
              <Bar dataKey="count" fill="#DAA520" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Pipeline Status & Live Telemetry */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* AI Pipeline Status */}
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-white font-semibold">AI Pipeline Status</h3>
              <button 
                onClick={triggerTestEvent}
                className="bg-rural-gold hover:bg-yellow-600 text-black px-3 py-1 rounded text-sm font-medium transition-colors"
              >
                Test Event
              </button>
            </div>
            
            {pipelineStatus && (
              <div className="space-y-3">
                <h4 className="text-gray-300 font-medium">Core Components</h4>
                {Object.entries(pipelineStatus.components).map(([name, info]: [string, any]) => (
                  <div key={name} className="flex items-center justify-between">
                    <span className="text-gray-200 capitalize">{name.replace('_', ' ')}</span>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(info.status)}
                      <span className="text-sm text-gray-300 capitalize">{info.status}</span>
                    </div>
                  </div>
                ))}
                
                <h4 className="text-gray-300 font-medium mt-4">External Services</h4>
                {Object.entries(pipelineStatus.external_services).map(([name, info]: [string, any]) => (
                  <div key={name} className="flex items-center justify-between">
                    <span className="text-gray-200 capitalize">{name.replace('_', ' ')}</span>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(info.status)}
                      <span className="text-sm text-gray-300 capitalize">{info.status}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Live Telemetry Feed */}
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
            <h3 className="text-white font-semibold mb-4">Live Telemetry Feed</h3>
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {telemetryEvents.map((event, index) => (
                <div key={index} className="bg-black/20 rounded p-3 text-sm">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-rural-gold font-medium">{event.type}</span>
                    <span className="text-gray-400 text-xs">
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="text-gray-300">
                    {JSON.stringify(event.data, null, 2)}
                  </div>
                </div>
              ))}
              
              {telemetryEvents.length === 0 && (
                <div className="text-center text-gray-400 py-8">
                  {isConnected ? 'Waiting for telemetry events...' : 'Disconnected from telemetry feed'}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}