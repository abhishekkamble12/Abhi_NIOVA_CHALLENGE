"use client";

import React from "react";
import useVoiceState from "../../hooks/useVoiceState";

export default function VoicePage() {
  const { state, startListening, stopListening } = useVoiceState();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white flex flex-col">
      <header className="px-4 py-4">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div className="font-semibold">SatyaSetu</div>
          <div className="text-sm bg-white/5 px-3 py-1 rounded-full">English • हिन्दी</div>
        </div>
      </header>

      <main className="flex-1 flex flex-col items-center justify-end pb-12">
        <div className="w-full max-w-md px-4">
          <div className="mb-6 p-4 rounded-2xl bg-white/5 backdrop-blur">
            <p className="text-lg">Namaste. I am listening. Tap the button to verify a message.</p>
          </div>
        </div>

        <div className="w-full flex justify-center px-4">
          <button
            onMouseDown={startListening}
            onMouseUp={stopListening}
            className="w-28 h-28 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 shadow-lg flex items-center justify-center"
            aria-label="Voice control"
          >
            <div className="text-black font-bold">{state === "listening" ? "●" : "🎤"}</div>
          </button>
        </div>
      </main>
    </div>
  );
}
'use client'

import { useState, useRef, useEffect } from 'react'
import Link from 'next/link'
import { Mic, MicOff, Volume2, ArrowLeft, Send, AlertCircle } from 'lucide-react'
import { apiClient, VoiceProcessResponse } from '../../lib/api'
import { LoadingSpinner, LoadingOverlay } from '../../components/LoadingSpinner'

interface VoiceState {
  isListening: boolean
  isProcessing: boolean
  hasAudio: boolean
  currentText: string
  response: string
  error: string | null
  isConnected: boolean
}

export default function VoicePage() {
  const [voiceState, setVoiceState] = useState<VoiceState>({
    isListening: false,
    isProcessing: false,
    hasAudio: false,
    currentText: '',
    response: '',
    error: null,
    isConnected: true
  })

  const [textInput, setTextInput] = useState('')
  const [conversationHistory, setConversationHistory] = useState<Array<{
    type: 'user' | 'assistant'
    text: string
    timestamp: string
    processingTime?: number
  }>>([])

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])

  // Check backend connection on mount
  useEffect(() => {
    checkConnection()
  }, [])

  const checkConnection = async () => {
    const isHealthy = await apiClient.checkHealth()
    setVoiceState(prev => ({ ...prev, isConnected: isHealthy }))
    
    if (!isHealthy) {
      setVoiceState(prev => ({ 
        ...prev, 
        error: 'Unable to connect to backend. Please ensure the server is running.' 
      }))
    }
  }

  const startListening = async () => {
    if (!voiceState.isConnected) {
      await checkConnection()
      return
    }

    setVoiceState(prev => ({ ...prev, isListening: true, error: null }))
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        }
      })
      
      audioChunksRef.current = []
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }
      
      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        await processAudioInput(audioBlob)
        
        // Stop all tracks to release microphone
        stream.getTracks().forEach(track => track.stop())
      }
      
      mediaRecorderRef.current.start()
      
      // Auto-stop after 30 seconds
      setTimeout(() => {
        if (voiceState.isListening && mediaRecorderRef.current?.state === 'recording') {
          stopListening()
        }
      }, 30000)
      
    } catch (error) {
      console.error('Microphone access error:', error)
      setVoiceState(prev => ({ 
        ...prev, 
        isListening: false, 
        error: 'Microphone access denied. Please allow microphone access and try again.' 
      }))
    }
  }

  const stopListening = () => {
    setVoiceState(prev => ({ ...prev, isListening: false, isProcessing: true }))
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop()
    }
  }

  const processAudioInput = async (audioBlob: Blob) => {
    try {
      const audioFile = new File([audioBlob], 'recording.webm', { type: 'audio/webm' })
      const result = await apiClient.processAudio(audioFile, 'voice_ui_user')
      handleProcessingResult(result)
    } catch (error) {
      console.error('Audio processing error:', error)
      setVoiceState(prev => ({
        ...prev,
        isProcessing: false,
        error: 'Failed to process audio. Please try again.'
      }))
    }
  }

  const processTextInput = async (text: string) => {
    if (!text.trim()) return
    
    setVoiceState(prev => ({ ...prev, isProcessing: true, currentText: text, error: null }))
    
    try {
      const result = await apiClient.processText(text, 'voice_ui_user', 'hi')
      handleProcessingResult(result, text)
    } catch (error) {
      console.error('Text processing error:', error)
      setVoiceState(prev => ({
        ...prev,
        isProcessing: false,
        error: 'Failed to process text. Please try again.'
      }))
    }
  }

  const handleProcessingResult = (result: VoiceProcessResponse, inputText?: string) => {
    if (result.success) {
      const userText = inputText || result.transcribed_text || 'Audio input'
      const assistantResponse = result.response || 'मुझे समझ नहीं आया।'
      
      setVoiceState(prev => ({
        ...prev,
        isProcessing: false,
        currentText: userText,
        response: assistantResponse,
        error: null
      }))

      // Add to conversation history
      setConversationHistory(prev => [
        ...prev,
        {
          type: 'user',
          text: userText,
          timestamp: new Date().toLocaleTimeString()
        },
        {
          type: 'assistant',
          text: assistantResponse,
          timestamp: new Date().toLocaleTimeString(),
          processingTime: result.processing_time
        }
      ])
    } else {
      setVoiceState(prev => ({
        ...prev,
        isProcessing: false,
        error: result.error || 'Processing failed. Please try again.'
      }))
    }
  }

  const handleTextSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (textInput.trim() && !voiceState.isProcessing) {
      processTextInput(textInput)
      setTextInput('')
    }
  }

  const clearError = () => {
    setVoiceState(prev => ({ ...prev, error: null }))
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-rural-green">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-md p-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center space-x-2 text-white hover:text-rural-gold transition-colors">
            <ArrowLeft className="h-5 w-5" />
            <span>Back to Home</span>
          </Link>
          <h1 className="text-2xl font-bold text-white">Voice Assistant</h1>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${voiceState.isConnected ? 'bg-safe-green' : 'bg-alert-red'} animate-pulse`}></div>
            <span className="text-sm text-white">{voiceState.isConnected ? 'Connected' : 'Disconnected'}</span>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto p-4 pt-8">
        {/* Connection Error */}
        {!voiceState.isConnected && (
          <div className="bg-alert-red/20 border border-alert-red rounded-xl p-4 mb-6">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-alert-red" />
              <span className="text-white font-semibold">Connection Error</span>
            </div>
            <p className="text-gray-200 mt-2">
              Unable to connect to the backend server. Please ensure the server is running on port 8000.
            </p>
            <button 
              onClick={checkConnection}
              className="mt-3 bg-alert-red hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
            >
              Retry Connection
            </button>
          </div>
        )}

        {/* Main Voice Interface */}
        <LoadingOverlay isLoading={voiceState.isProcessing} text="Processing your request...">
          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 mb-6">
            {/* Voice Status Display */}
            <div className="text-center mb-8">
              {voiceState.isListening && (
                <div className="text-rural-gold text-lg mb-4 animate-pulse">
                  🎤 Listening... Speak now
                  <br />
                  <span className="hindi-text">सुन रहा हूँ... अब बोलें</span>
                </div>
              )}
              
              {voiceState.isProcessing && (
                <div className="text-cyber-blue text-lg mb-4">
                  <LoadingSpinner size="md" text="Processing... प्रोसेसिंग..." />
                </div>
              )}

              {voiceState.error && (
                <div className="text-alert-red text-lg mb-4 bg-alert-red/10 rounded-lg p-4">
                  <div className="flex items-center justify-center space-x-2 mb-2">
                    <AlertCircle className="h-5 w-5" />
                    <span>Error</span>
                  </div>
                  <p className="text-sm">{voiceState.error}</p>
                  <button 
                    onClick={clearError}
                    className="mt-2 text-xs underline hover:no-underline"
                  >
                    Dismiss
                  </button>
                </div>
              )}
            </div>

            {/* Large Mic Control */}
            <div className="flex justify-center mb-8">
              <button
                onClick={voiceState.isListening ? stopListening : startListening}
                disabled={voiceState.isProcessing || !voiceState.isConnected}
                className={`
                  w-32 h-32 rounded-full flex items-center justify-center text-white text-4xl
                  transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed
                  ${voiceState.isListening 
                    ? 'bg-alert-red animate-pulse shadow-lg shadow-red-500/50' 
                    : voiceState.isProcessing
                    ? 'bg-gray-500 cursor-not-allowed'
                    : 'bg-rural-gold hover:bg-yellow-600 shadow-lg shadow-yellow-500/50'
                  }
                `}
              >
                {voiceState.isListening ? <MicOff /> : <Mic />}
              </button>
            </div>

            {/* Visual Voice Waves */}
            {voiceState.isListening && (
              <div className="flex justify-center space-x-1 mb-6">
                {[...Array(5)].map((_, i) => (
                  <div
                    key={i}
                    className="voice-wave bg-rural-gold w-2 h-8 rounded-full"
                    style={{ animationDelay: `${i * 0.1}s` }}
                  ></div>
                ))}
              </div>
            )}

            {/* Current Transcription */}
            {voiceState.currentText && (
              <div className="bg-black/20 rounded-lg p-4 mb-4">
                <h3 className="text-white font-semibold mb-2">You said:</h3>
                <p className="text-gray-200 hindi-text">{voiceState.currentText}</p>
              </div>
            )}

            {/* AI Response */}
            {voiceState.response && (
              <div className="bg-cyber-blue/20 rounded-lg p-4 mb-4">
                <h3 className="text-white font-semibold mb-2">SatyaSetu Response:</h3>
                <p className="text-gray-200 hindi-text">{voiceState.response}</p>
                <button className="mt-2 text-rural-gold hover:text-yellow-300 flex items-center space-x-1">
                  <Volume2 className="h-4 w-4" />
                  <span>Play Audio</span>
                </button>
              </div>
            )}
          </div>
        </LoadingOverlay>

        {/* Text Input Alternative */}
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 mb-6">
          <h3 className="text-white font-semibold mb-4">Or type your message:</h3>
          <form onSubmit={handleTextSubmit} className="flex space-x-2">
            <input
              type="text"
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Type in Hindi or English... हिंदी या अंग्रेजी में टाइप करें..."
              className="flex-1 bg-black/20 text-white placeholder-gray-400 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-rural-gold hindi-text"
              disabled={voiceState.isProcessing || !voiceState.isConnected}
              maxLength={1000}
            />
            <button
              type="submit"
              disabled={voiceState.isProcessing || !textInput.trim() || !voiceState.isConnected}
              className="bg-rural-gold hover:bg-yellow-600 disabled:bg-gray-500 disabled:cursor-not-allowed text-black px-6 py-3 rounded-lg font-semibold transition-colors flex items-center space-x-2"
            >
              <Send className="h-4 w-4" />
              <span>Send</span>
            </button>
          </form>
        </div>

        {/* Conversation History */}
        {conversationHistory.length > 0 && (
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
            <h3 className="text-white font-semibold mb-4">Conversation History</h3>
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {conversationHistory.map((message, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-lg ${
                    message.type === 'user' 
                      ? 'bg-rural-gold/20 ml-8' 
                      : 'bg-cyber-blue/20 mr-8'
                  }`}
                >
                  <div className="flex justify-between items-start mb-1">
                    <span className="text-sm font-semibold text-white">
                      {message.type === 'user' ? 'You' : 'SatyaSetu'}
                    </span>
                    <div className="text-xs text-gray-400">
                      {message.timestamp}
                      {message.processingTime && (
                        <span className="ml-2">({message.processingTime.toFixed(2)}s)</span>
                      )}
                    </div>
                  </div>
                  <p className="text-gray-200 hindi-text">{message.text}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="fixed bottom-4 right-4 space-y-2">
        <button 
          onClick={() => voiceState.response && alert('Audio playback not implemented yet')}
          className="bg-safe-green hover:bg-green-600 text-white p-3 rounded-full shadow-lg transition-colors"
          disabled={!voiceState.response}
        >
          <Volume2 className="h-5 w-5" />
        </button>
        <Link 
          href="/admin"
          className="bg-cyber-blue hover:bg-blue-600 text-white p-3 rounded-full shadow-lg transition-colors block"
        >
          📊
        </Link>
      </div>
    </div>
  )
}