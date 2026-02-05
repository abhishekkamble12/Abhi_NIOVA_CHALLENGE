'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { apiClient } from '@/lib/api';

interface Brand {
  id: number;
  name: string;
  keywords: string[];
  platforms: string[];
}

interface GeneratedPost {
  id: number;
  caption: string;
  hashtags: string[];
  cta: string;
  platform: string;
  published: boolean;
}

export default function SocialMediaDashboard() {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [selectedBrand, setSelectedBrand] = useState<Brand | null>(null);
  const [generatedPosts, setGeneratedPosts] = useState<GeneratedPost[]>([]);
  const [loading, setLoading] = useState(false);
  const [showBrandForm, setShowBrandForm] = useState(false);
  const [analytics, setAnalytics] = useState<any>(null);

  useEffect(() => {
    loadBrands();
  }, []);

  const loadBrands = async () => {
    try {
      const data = await apiClient.brand.list();
      setBrands(data);
    } catch (error) {
      console.error('Failed to load brands:', error);
    }
  };

  const handleSelectBrand = async (brand: Brand): Promise<void> => {
    setSelectedBrand(brand);
    setLoading(true);
    try {
      const posts = await apiClient.content.getBrandPosts(brand.id);
      setGeneratedPosts(posts);
      const analyticData = await apiClient.engagement.getAnalytics(brand.id);
      setAnalytics(analyticData);
    } catch (error) {
      console.error('Failed to load brand data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateContent = async (platform: string) => {
    if (!selectedBrand) return;
    
    setLoading(true);
    try {
      const newPost = await apiClient.content.generate(selectedBrand.id, platform);
      setGeneratedPosts([newPost, ...generatedPosts]);
    } catch (error) {
      console.error('Failed to generate content:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePublishPost = async (postId: number) => {
    try {
      await apiClient.content.publish(postId);
      const updated = generatedPosts.map(p => 
        p.id === postId ? { ...p, published: true } : p
      );
      setGeneratedPosts(updated);
    } catch (error) {
      console.error('Failed to publish post:', error);
    }
  };

  const handleOptimizePrompts = async () => {
    if (!selectedBrand) return;
    
    setLoading(true);
    try {
      const result = await apiClient.engagement.optimizePrompts(selectedBrand.id);
      console.log('Optimization complete:', result);
      alert('Prompts optimized! Next generation will be even better.');
    } catch (error) {
      console.error('Failed to optimize prompts:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-2">
            🚀 Automated Social Media Engine
          </h1>
          <p className="text-purple-300">
            AI-powered content generation with feedback loops
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Brands Panel */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="lg:col-span-1"
          >
            <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-purple-500/20">
              <h2 className="text-xl font-bold text-white mb-4">Your Brands</h2>
              
              <button
                onClick={() => setShowBrandForm(true)}
                className="w-full bg-purple-600 hover:bg-purple-700 text-white py-2 rounded-lg mb-4 transition"
              >
                + New Brand
              </button>

              <div className="space-y-2">
                {brands.map((brand: Brand) => (
                  <motion.button
                    key={brand.id}
                    whileHover={{ scale: 1.02 }}
                    onClick={() => handleSelectBrand(brand)}
                    className={`w-full p-3 rounded-lg text-left transition ${
                      selectedBrand?.id === brand.id
                        ? 'bg-purple-600 text-white'
                        : 'bg-slate-700/50 text-gray-300 hover:bg-slate-700'
                    }`}
                  >
                    <div className="font-semibold">{brand.name}</div>
                    <div className="text-xs mt-1">
                      {brand.platforms.join(', ')}
                    </div>
                  </motion.button>
                ))}
              </div>
            </div>
          </motion.div>

          {/* Main Content */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="lg:col-span-2"
          >
            {selectedBrand ? (
              <div className="space-y-6">
                {/* Generation Controls */}
                <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-purple-500/20">
                  <h3 className="text-lg font-bold text-white mb-4">
                    Generate Content for: {selectedBrand.name}
                  </h3>
                  
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
                    {['instagram', 'linkedin', 'x'].map((platform: string) => (
                      <motion.button
                        key={platform}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => handleGenerateContent(platform)}
                        disabled={loading}
                        className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white py-3 rounded-lg font-semibold transition disabled:opacity-50"
                      >
                        {loading ? '⏳' : '✨'} {platform}
                      </motion.button>
                    ))}
                  </div>

                  <button
                    onClick={handleOptimizePrompts}
                    disabled={loading || generatedPosts.length === 0}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg disabled:opacity-50 transition"
                  >
                    🔄 Optimize Prompts (Feedback Loop)
                  </button>
                </div>

                {/* Analytics Panel */}
                {analytics && (
                  <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-green-500/20">
                    <h3 className="text-lg font-bold text-white mb-4">📊 Analytics</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="bg-slate-700/50 p-4 rounded-lg">
                        <div className="text-gray-400 text-sm">Posts</div>
                        <div className="text-2xl font-bold text-white">
                          {analytics.total_posts}
                        </div>
                      </div>
                      <div className="bg-slate-700/50 p-4 rounded-lg">
                        <div className="text-gray-400 text-sm">Likes</div>
                        <div className="text-2xl font-bold text-pink-400">
                          {analytics.total_likes}
                        </div>
                      </div>
                      <div className="bg-slate-700/50 p-4 rounded-lg">
                        <div className="text-gray-400 text-sm">Shares</div>
                        <div className="text-2xl font-bold text-blue-400">
                          {analytics.total_shares}
                        </div>
                      </div>
                      <div className="bg-slate-700/50 p-4 rounded-lg">
                        <div className="text-gray-400 text-sm">Avg CTR</div>
                        <div className="text-2xl font-bold text-green-400">
                          {analytics.average_ctr}%
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Generated Posts */}
                <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-purple-500/20">
                  <h3 className="text-lg font-bold text-white mb-4">
                    📝 Generated Posts ({generatedPosts.length})
                  </h3>
                  
                  <div className="space-y-4">
                    {generatedPosts.map((post: GeneratedPost) => (
                      <motion.div
                        key={post.id}
                        whileHover={{ scale: 1.02 }}
                        className="bg-slate-700/50 p-4 rounded-lg border border-purple-400/20"
                      >
                        <div className="flex justify-between items-start mb-2">
                          <span className="text-purple-400 font-semibold">
                            {post.platform.toUpperCase()}
                          </span>
                          <span
                            className={`text-xs px-2 py-1 rounded ${
                              post.published
                                ? 'bg-green-500/20 text-green-300'
                                : 'bg-yellow-500/20 text-yellow-300'
                            }`}
                          >
                            {post.published ? '✓ Published' : '⏳ Scheduled'}
                          </span>
                        </div>
                        
                        <p className="text-white mb-3">{post.caption}</p>
                        
                        <div className="flex flex-wrap gap-2 mb-3">
                          {post.hashtags.slice(0, 5).map((tag: string, i: number) => (
                            <span
                              key={i}
                              className="text-purple-300 text-sm bg-purple-500/20 px-2 py-1 rounded"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>

                        <div className="text-gray-400 text-sm mb-3">{post.cta}</div>
                        
                        {!post.published && (
                          <button
                            onClick={() => handlePublishPost(post.id)}
                            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded transition"
                          >
                            📤 Publish Now
                          </button>
                        )}
                      </motion.div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl p-12 border border-purple-500/20 text-center">
                <p className="text-gray-400 mb-4">Select a brand to get started</p>
                <button
                  onClick={() => setShowBrandForm(true)}
                  className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg"
                >
                  Create Your First Brand
                </button>
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  );
}
