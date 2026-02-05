'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { apiClient } from '@/lib/api';

interface NewsArticle {
  id: number;
  title: string;
  description: string;
  content: string;
  source: string;
  category: string;
  url: string;
  image_url?: string;
  author?: string;
  published_at?: string;
  topics?: string[];
  relevance_score: number;
  summary?: string;
  trending: boolean;
}

interface UserPreferences {
  keywords: string[];
  categories: string[];
}

export default function PersonalizedNewsFeed() {
  const [feed, setFeed] = useState<NewsArticle[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [userId] = useState(1);
  const [preferences, setPreferences] = useState<UserPreferences>({
    keywords: [],
    categories: [],
  });
  const [newKeyword, setNewKeyword] = useState('');
  const [expandedArticleId, setExpandedArticleId] = useState<number | null>(null);
  const [selectedArticleSummary, setSelectedArticleSummary] = useState<string | null>(null);
  const [showPreferencesPanel, setShowPreferencesPanel] = useState(false);
  const [showTrendingOnly, setShowTrendingOnly] = useState(false);
  const [activeTab, setActiveTab] = useState<'personalized' | 'trending' | 'search'>('personalized');
  const [searchKeyword, setSearchKeyword] = useState('');
  const [articleBeingSummarized, setArticleBeingSummarized] = useState<number | null>(null);

  // Load preferences on mount
  useEffect(() => {
    loadPreferences();
    loadPersonalizedFeed();
  }, []);

  const loadPreferences = async () => {
    try {
      const prefs = await apiClient.feed.getUserPreferences(userId);
      setPreferences(prefs);
    } catch (error) {
      console.log('No preferences found, using defaults');
    }
  };

  const loadPersonalizedFeed = async () => {
    setLoading(true);
    try {
      const articles = await apiClient.feed.getPersonalizedFeed(userId, 20);
      setFeed(articles);
    } catch (error) {
      console.error('Failed to load personalized feed:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadTrendingNews = async () => {
    setLoading(true);
    try {
      const articles = await apiClient.feed.getTrendingNews('us', 20, userId);
      setFeed(articles);
    } catch (error) {
      console.error('Failed to load trending news:', error);
    } finally {
      setLoading(false);
    }
  };

  const searchNews = async () => {
    if (!searchKeyword.trim()) return;
    
    setLoading(true);
    try {
      const articles = await apiClient.feed.searchNews(searchKeyword, 'publishedAt', 20, userId);
      setFeed(articles);
    } catch (error) {
      console.error('Failed to search news:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCategoryNews = async (category: string) => {
    setLoading(true);
    try {
      const articles = await apiClient.feed.getNewsByCategory(category, 20, userId);
      setFeed(articles);
    } catch (error) {
      console.error('Failed to load category news:', error);
    } finally {
      setLoading(false);
    }
  };

  const addKeywordPreference = async () => {
    if (!newKeyword.trim()) return;

    const updatedKeywords = [...preferences.keywords, newKeyword];
    setPreferences({ ...preferences, keywords: updatedKeywords });
    
    try {
      await apiClient.feed.updateUserPreferences(userId, {
        keywords: updatedKeywords,
        categories: preferences.categories,
      });
      setNewKeyword('');
      await loadPersonalizedFeed();
    } catch (error) {
      console.error('Failed to update preferences:', error);
    }
  };

  const removeKeywordPreference = async (keyword: string) => {
    const updatedKeywords = preferences.keywords.filter(k => k !== keyword);
    setPreferences({ ...preferences, keywords: updatedKeywords });
    
    try {
      await apiClient.feed.updateUserPreferences(userId, {
        keywords: updatedKeywords,
        categories: preferences.categories,
      });
    } catch (error) {
      console.error('Failed to update preferences:', error);
    }
  };

  const generateSummary = async (article: NewsArticle) => {
    setArticleBeingSummarized(article.id);
    try {
      const response = await apiClient.feed.summarizeArticle({
        article_url: article.url,
        article_title: article.title,
        article_content: article.content || article.description,
      });
      setSelectedArticleSummary(response.summary);
      setExpandedArticleId(article.id);
    } catch (error) {
      console.error('Failed to generate summary:', error);
    } finally {
      setArticleBeingSummarized(null);
    }
  };

  const trackArticleClick = async (article: NewsArticle) => {
    try {
      await apiClient.feed.trackBehavior({
        article_id: article.id,
        action: 'click',
        read_time: 0,
        scroll_depth: 0,
      });
    } catch (error) {
      console.error('Failed to track behavior:', error);
    }
    
    // Open article in new tab
    window.open(article.url, '_blank');
  };

  const handleTabChange = (tab: 'personalized' | 'trending' | 'search') => {
    setActiveTab(tab);
    if (tab === 'personalized') {
      loadPersonalizedFeed();
    } else if (tab === 'trending') {
      loadTrendingNews();
    }
  };

  const filteredFeed = selectedCategory
    ? feed.filter(item => item.category?.toLowerCase() === selectedCategory.toLowerCase())
    : showTrendingOnly
    ? feed.filter(item => item.trending)
    : feed;

  const categories = Array.from(new Set(feed.map(item => item.category))).slice(0, 8);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-2">
            📰 Real-Time News Feed
          </h1>
          <p className="text-blue-300">
            AI-powered news discovery with personalization & smart summaries
          </p>
        </motion.div>

        {/* Tab Navigation */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mb-6 flex gap-3 border-b border-blue-500/20"
        >
          {(['personalized', 'trending', 'search'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => handleTabChange(tab)}
              className={`px-6 py-3 font-semibold transition capitalize ${
                activeTab === tab
                  ? 'text-blue-400 border-b-2 border-blue-400'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              {tab === 'personalized' && '⭐ Personalized'}
              {tab === 'trending' && '🔥 Trending'}
              {tab === 'search' && '🔍 Search'}
            </button>
          ))}
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar - Preferences & Filters */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="lg:col-span-1 space-y-4"
          >
            {/* Preferences Panel */}
            <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl p-4 border border-blue-500/20">
              <button
                onClick={() => setShowPreferencesPanel(!showPreferencesPanel)}
                className="w-full text-left font-semibold text-white hover:text-blue-300 transition flex items-center justify-between mb-3"
              >
                <span>⚙️ Preferences</span>
                <span className="text-sm">{showPreferencesPanel ? '▼' : '▶'}</span>
              </button>

              {showPreferencesPanel && (
                <div className="space-y-3">
                  {/* Add Keyword */}
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newKeyword}
                      onChange={(e) => setNewKeyword(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && addKeywordPreference()}
                      placeholder="Add interest..."
                      className="flex-1 bg-slate-700 text-white px-3 py-2 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      onClick={addKeywordPreference}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg text-sm transition"
                    >
                      +
                    </button>
                  </div>

                  {/* User Keywords */}
                  <div className="space-y-2">
                    <p className="text-gray-400 text-xs font-semibold">Your Interests:</p>
                    <div className="flex flex-wrap gap-2">
                      {preferences.keywords.map(keyword => (
                        <motion.button
                          key={keyword}
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          whileHover={{ scale: 1.05 }}
                          onClick={() => removeKeywordPreference(keyword)}
                          className="bg-blue-600/20 text-blue-300 hover:bg-red-600/20 hover:text-red-300 px-3 py-1 rounded-full text-xs transition flex items-center gap-1"
                        >
                          {keyword} ✕
                        </motion.button>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Category Filter */}
            <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl p-4 border border-blue-500/20">
              <p className="text-gray-300 text-sm font-semibold mb-3">Categories:</p>
              <div className="space-y-2">
                <button
                  onClick={() => setSelectedCategory(null)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm transition ${
                    selectedCategory === null
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-700 text-gray-300 hover:bg-slate-600'
                  }`}
                >
                  📋 All News
                </button>
                {categories.map(category => (
                  <button
                    key={category}
                    onClick={() => setSelectedCategory(category)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-sm transition ${
                      selectedCategory === category
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-700 text-gray-300 hover:bg-slate-600'
                    }`}
                  >
                    {category}
                  </button>
                ))}
              </div>
            </div>

            {/* Filters */}
            <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl p-4 border border-blue-500/20 space-y-2">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showTrendingOnly}
                  onChange={(e) => setShowTrendingOnly(e.target.checked)}
                  className="w-4 h-4 rounded"
                />
                <span className="text-gray-300 text-sm">🔥 Trending Only</span>
              </label>
            </div>
          </motion.div>

          {/* Main Content Area */}
          <div className="lg:col-span-3 space-y-4">
            {/* Search Bar */}
            {activeTab === 'search' && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex gap-3"
              >
                <input
                  type="text"
                  value={searchKeyword}
                  onChange={(e) => setSearchKeyword(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && searchNews()}
                  placeholder="Search news..."
                  className="flex-1 bg-slate-800/50 text-white px-4 py-3 rounded-lg border border-blue-500/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={searchNews}
                  disabled={loading}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition disabled:opacity-50"
                >
                  {loading ? '⏳' : '🔍'} Search
                </button>
              </motion.div>
            )}

            {/* News Articles */}
            <div className="space-y-4">
              <AnimatePresence>
                {filteredFeed.map((article, index) => (
                  <motion.div
                    key={article.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <motion.div
                      whileHover={{ scale: 1.01 }}
                      onClick={() => trackArticleClick(article)}
                      className="bg-slate-800/50 backdrop-blur-lg rounded-xl border border-blue-500/20 cursor-pointer hover:border-blue-500/50 hover:shadow-lg hover:shadow-blue-500/10 transition overflow-hidden"
                    >
                      <div className="p-6">
                        {/* Header */}
                        <div className="flex items-start justify-between gap-4 mb-3">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <span className="text-sm text-gray-400 font-semibold">
                                {article.source}
                              </span>
                              <span className="text-xs bg-blue-500/20 text-blue-300 px-2 py-1 rounded">
                                {article.category}
                              </span>
                              {article.trending && (
                                <span className="text-xs bg-red-500/20 text-red-300 px-2 py-1 rounded">
                                  🔥 Trending
                                </span>
                              )}
                            </div>
                            <h3 className="text-lg font-bold text-white hover:text-blue-300 transition line-clamp-2">
                              {article.title}
                            </h3>
                          </div>

                          {/* Relevance Score Badge */}
                          <div className="text-right flex-shrink-0">
                            <div className="text-2xl font-bold text-blue-400">
                              {Math.round(article.relevance_score * 100)}%
                            </div>
                            <div className="text-xs text-gray-400">relevance</div>
                          </div>
                        </div>

                        {/* Image and Description */}
                        <div className="flex gap-4 mb-4">
                          {article.image_url && (
                            <img
                              src={article.image_url}
                              alt={article.title}
                              className="hidden sm:block w-32 h-32 object-cover rounded-lg flex-shrink-0"
                            />
                          )}
                          <p className="text-gray-300 text-sm line-clamp-3">
                            {article.description}
                          </p>
                        </div>

                        {/* Summary Section */}
                        <AnimatePresence>
                          {expandedArticleId === article.id && selectedArticleSummary && (
                            <motion.div
                              initial={{ opacity: 0, height: 0 }}
                              animate={{ opacity: 1, height: 'auto' }}
                              exit={{ opacity: 0, height: 0 }}
                              className="bg-blue-500/10 rounded-lg p-4 mb-4 border border-blue-500/20"
                            >
                              <div className="flex items-start justify-between gap-3 mb-2">
                                <h4 className="font-semibold text-blue-300">🤖 AI Summary:</h4>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setExpandedArticleId(null);
                                    setSelectedArticleSummary(null);
                                  }}
                                  className="text-gray-400 hover:text-white text-sm"
                                >
                                  ✕
                                </button>
                              </div>
                              <p className="text-gray-300 text-sm leading-relaxed">
                                {selectedArticleSummary}
                              </p>
                            </motion.div>
                          )}
                        </AnimatePresence>

                        {/* Meta Info */}
                        <div className="flex items-center justify-between pt-3 border-t border-slate-700/50 text-xs text-gray-400">
                          <div className="space-x-3">
                            {article.author && <span>✍️ {article.author}</span>}
                            {article.published_at && (
                              <span>📅 {new Date(article.published_at).toLocaleDateString()}</span>
                            )}
                          </div>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              generateSummary(article);
                            }}
                            disabled={articleBeingSummarized === article.id}
                            className="text-blue-400 hover:text-blue-300 transition disabled:opacity-50"
                          >
                            {articleBeingSummarized === article.id ? '⏳' : '📄'} Summary
                          </button>
                        </div>
                      </div>
                    </motion.div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>

            {/* Loading State */}
            {loading && (
              <div className="flex justify-center items-center py-12">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ repeat: Infinity, duration: 2 }}
                  className="text-4xl"
                >
                  ⏳
                </motion.div>
              </div>
            )}

            {/* Empty State */}
            {filteredFeed.length === 0 && !loading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="bg-slate-800/50 backdrop-blur-lg rounded-xl p-12 border border-blue-500/20 text-center"
              >
                <p className="text-gray-400 mb-4">
                  No articles found. Try adjusting your filters or search terms.
                </p>
                <button
                  onClick={() => activeTab === 'personalized' ? loadPersonalizedFeed() : loadTrendingNews()}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition"
                >
                  🔄 Refresh
                </button>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
