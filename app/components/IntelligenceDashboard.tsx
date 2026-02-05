'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface IntelligenceMetrics {
  system_status: string;
  intelligence_metrics: {
    content_engine: {
      prompts_optimized: number;
      engagement_prediction_accuracy: number;
      last_optimization: string;
      improvement_trend: string;
    };
    feed_pipeline: {
      user_profiles_active: number;
      recommendation_accuracy: number;
      click_through_improvement: string;
      last_model_update: string;
    };
    video_pipeline: {
      scenes_analyzed: number;
      editing_time_saved: string;
      thumbnail_ctr_improvement: string;
      last_cv_optimization: string;
    };
  };
  cross_module_insights: {
    shared_learnings: number;
    pattern_transfers: string[];
    intelligence_compound_rate: string;
  };
  next_optimization_cycle: string;
}

export default function IntelligenceDashboard() {
  const [metrics, setMetrics] = useState<IntelligenceMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [learningInProgress, setLearningInProgress] = useState(false);

  useEffect(() => {
    fetchIntelligenceStatus();
  }, []);

  const fetchIntelligenceStatus = async () => {
    try {
      await new Promise(resolve => setTimeout(resolve, 800));
      
      const mockMetrics: IntelligenceMetrics = {
        system_status: "learning",
        intelligence_metrics: {
          content_engine: {
            prompts_optimized: 47,
            engagement_prediction_accuracy: 0.89,
            last_optimization: "2024-02-03T14:30:00Z",
            improvement_trend: "+12% this week"
          },
          feed_pipeline: {
            user_profiles_active: 1247,
            recommendation_accuracy: 0.94,
            click_through_improvement: "+156%",
            last_model_update: "2024-02-03T12:15:00Z"
          },
          video_pipeline: {
            scenes_analyzed: 8934,
            editing_time_saved: "78%",
            thumbnail_ctr_improvement: "+89%",
            last_cv_optimization: "2024-02-03T11:45:00Z"
          }
        },
        cross_module_insights: {
          shared_learnings: 23,
          pattern_transfers: [
            "Video engagement patterns → Social caption optimization",
            "News topic trends → Brand content suggestions", 
            "User behavior signals → Cross-platform personalization"
          ],
          intelligence_compound_rate: "+34% monthly"
        },
        next_optimization_cycle: "2024-02-03T16:00:00Z"
      };
      
      setMetrics(mockMetrics);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch intelligence status:', error);
      setLoading(false);
    }
  };

  const triggerLearningCycle = async () => {
    setLearningInProgress(true);
    
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      await fetchIntelligenceStatus();
      
      setLearningInProgress(false);
    } catch (error) {
      console.error('Failed to trigger learning cycle:', error);
      setLearningInProgress(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full"
        />
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-red-400">Failed to load intelligence metrics</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent mb-2">
            🧠 AI Intelligence Dashboard
          </h1>
          <p className="text-gray-400 text-lg">
            Real-time learning metrics across all AI modules
          </p>
          
          <div className="flex items-center gap-4 mt-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
              <span className="text-green-400 font-semibold">System Status: {metrics.system_status}</span>
            </div>
            
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={triggerLearningCycle}
              disabled={learningInProgress}
              className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-semibold disabled:opacity-50"
            >
              {learningInProgress ? (
                <div className="flex items-center gap-2">
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    className="w-4 h-4 border-2 border-white border-t-transparent rounded-full"
                  />
                  Learning...
                </div>
              ) : (
                '🚀 Trigger Learning Cycle'
              )}
            </motion.button>
          </div>
        </motion.div>

        {/* Module Metrics Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Content Engine */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700/50"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg flex items-center justify-center">
                <span className="text-xl">📱</span>
              </div>
              <h3 className="text-xl font-bold text-white">Content Engine</h3>
            </div>
            
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Prompts Optimized</span>
                <span className="text-white font-semibold">{metrics.intelligence_metrics.content_engine.prompts_optimized}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Prediction Accuracy</span>
                <span className="text-green-400 font-semibold">
                  {(metrics.intelligence_metrics.content_engine.engagement_prediction_accuracy * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Improvement Trend</span>
                <span className="text-green-400 font-semibold">
                  {metrics.intelligence_metrics.content_engine.improvement_trend}
                </span>
              </div>
            </div>
          </motion.div>

          {/* Feed Pipeline */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700/50"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-lg flex items-center justify-center">
                <span className="text-xl">📰</span>
              </div>
              <h3 className="text-xl font-bold text-white">Feed Pipeline</h3>
            </div>
            
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Active Profiles</span>
                <span className="text-white font-semibold">{metrics.intelligence_metrics.feed_pipeline.user_profiles_active.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Recommendation Accuracy</span>
                <span className="text-green-400 font-semibold">
                  {(metrics.intelligence_metrics.feed_pipeline.recommendation_accuracy * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">CTR Improvement</span>
                <span className="text-green-400 font-semibold">
                  {metrics.intelligence_metrics.feed_pipeline.click_through_improvement}
                </span>
              </div>
            </div>
          </motion.div>

          {/* Video Pipeline */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700/50"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-r from-amber-600 to-orange-600 rounded-lg flex items-center justify-center">
                <span className="text-xl">🎬</span>
              </div>
              <h3 className="text-xl font-bold text-white">Video Pipeline</h3>
            </div>
            
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Scenes Analyzed</span>
                <span className="text-white font-semibold">{metrics.intelligence_metrics.video_pipeline.scenes_analyzed.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Time Saved</span>
                <span className="text-green-400 font-semibold">
                  {metrics.intelligence_metrics.video_pipeline.editing_time_saved}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Thumbnail CTR</span>
                <span className="text-green-400 font-semibold">
                  {metrics.intelligence_metrics.video_pipeline.thumbnail_ctr_improvement}
                </span>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Cross-Module Intelligence */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700/50 mb-8"
        >
          <h3 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
            <span className="text-3xl">🔗</span>
            Cross-Module Intelligence
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-lg font-semibold text-white mb-3">Shared Learnings</h4>
              <div className="text-3xl font-bold text-purple-400 mb-2">
                {metrics.cross_module_insights.shared_learnings}
              </div>
              <p className="text-gray-400">
                Intelligence compound rate: <span className="text-green-400 font-semibold">
                  {metrics.cross_module_insights.intelligence_compound_rate}
                </span>
              </p>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold text-white mb-3">Pattern Transfers</h4>
              <div className="space-y-2">
                {metrics.cross_module_insights.pattern_transfers.map((transfer, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 + index * 0.1 }}
                    className="bg-slate-700/50 rounded-lg p-3 text-sm text-gray-300"
                  >
                    {transfer}
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Learning Timeline */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-slate-700/50"
        >
          <h3 className="text-2xl font-bold text-white mb-4 flex items-center gap-3">
            <span className="text-3xl">📈</span>
            Learning Progression
          </h3>
          
          <div className="space-y-4">
            {[
              { date: "Feb 1", event: "Initial deployment", improvement: "Baseline established" },
              { date: "Feb 2", event: "First optimization cycle", improvement: "+23% engagement" },
              { date: "Feb 3", event: "Cross-module intelligence activated", improvement: "+34% overall" },
            ].map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 + index * 0.1 }}
                className="flex items-center gap-4 p-4 bg-slate-700/30 rounded-lg"
              >
                <div className="w-12 h-12 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full flex items-center justify-center text-white font-bold">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <div className="text-white font-semibold">{item.event}</div>
                  <div className="text-gray-400 text-sm">{item.date}</div>
                </div>
                <div className="text-green-400 font-semibold">{item.improvement}</div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}