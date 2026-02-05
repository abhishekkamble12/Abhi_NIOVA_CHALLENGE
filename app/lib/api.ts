'use client';

const API_BASE_URL = typeof window !== 'undefined' 
  ? (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1')
  : 'http://localhost:8000/api/v1';

export const apiClient = {
  // ==================== SOCIAL MEDIA ====================
  
  brand: {
    create: async (brandData: any) => {
      const res = await fetch(`${API_BASE_URL}/social/brands`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(brandData),
      });
      return res.json();
    },
    
    get: async (brandId: number) => {
      const res = await fetch(`${API_BASE_URL}/social/brands/${brandId}`);
      return res.json();
    },
    
    list: async () => {
      const res = await fetch(`${API_BASE_URL}/social/brands`);
      return res.json();
    },
  },
  
  content: {
    generate: async (brandId: number, platform: string) => {
      const res = await fetch(`${API_BASE_URL}/social/generate/content?brand_id=${brandId}&platform=${platform}`, {
        method: 'POST',
      });
      return res.json();
    },
    
    getPost: async (postId: number) => {
      const res = await fetch(`${API_BASE_URL}/social/posts/${postId}`);
      return res.json();
    },
    
    getBrandPosts: async (brandId: number) => {
      const res = await fetch(`${API_BASE_URL}/social/brand/${brandId}/posts`);
      return res.json();
    },
    
    publish: async (postId: number) => {
      const res = await fetch(`${API_BASE_URL}/social/posts/${postId}/publish`, {
        method: 'PUT',
      });
      return res.json();
    },
  },
  
  engagement: {
    track: async (postId: number, data: any) => {
      const res = await fetch(`${API_BASE_URL}/social/track/engagement/${postId}?likes=${data.likes}&comments=${data.comments}&shares=${data.shares}&impressions=${data.impressions}&ctr=${data.ctr}`, {
        method: 'POST',
      });
      return res.json();
    },
    
    getAnalytics: async (brandId: number) => {
      const res = await fetch(`${API_BASE_URL}/social/analytics/brand/${brandId}`);
      return res.json();
    },
    
    optimizePrompts: async (brandId: number) => {
      const res = await fetch(`${API_BASE_URL}/social/optimize/prompts/${brandId}`, {
        method: 'POST',
      });
      return res.json();
    },
  },
  
  // ==================== NEWS FEED ====================
  
  articles: {
    ingest: async (articleData: any) => {
      const res = await fetch(`${API_BASE_URL}/feed/articles/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(articleData),
      });
      return res.json();
    },
    
    get: async (articleId: number) => {
      const res = await fetch(`${API_BASE_URL}/feed/articles/${articleId}`);
      return res.json();
    },
  },
  
  feed: {
    // ========== OLD FEED METHODS ==========
    getPersonalized: async (userId: number, limit: number = 20) => {
      const res = await fetch(`${API_BASE_URL}/feed/feed/${userId}?limit=${limit}`);
      return res.json();
    },
    
    trackBehavior: async (behaviorData: any) => {
      const res = await fetch(`${API_BASE_URL}/feed/track/behavior`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(behaviorData),
      });
      return res.json();
    },
    
    tuneRecommendations: async (userId: number) => {
      const res = await fetch(`${API_BASE_URL}/feed/recommendations/tune/${userId}`, {
        method: 'POST',
      });
      return res.json();
    },

    // ========== REAL NEWS FEED METHODS ==========
    
    // Search news by keyword
    searchNews: async (keyword: string, sortBy: string = 'publishedAt', limit: number = 20, userId?: number) => {
      const params = new URLSearchParams({ keyword, sort_by: sortBy, limit: limit.toString() });
      if (userId) params.append('user_id', userId.toString());
      const res = await fetch(`${API_BASE_URL}/feed/real/search?${params}`);
      return res.json();
    },
    
    // Get trending news
    getTrendingNews: async (country: string = 'us', limit: number = 20, userId?: number) => {
      const params = new URLSearchParams({ country, limit: limit.toString() });
      if (userId) params.append('user_id', userId.toString());
      const res = await fetch(`${API_BASE_URL}/feed/real/trending?${params}`);
      return res.json();
    },
    
    // Get personalized feed based on user preferences
    getPersonalizedFeed: async (userId: number, limit: number = 20) => {
      const res = await fetch(`${API_BASE_URL}/feed/real/personalized/${userId}?limit=${limit}`);
      return res.json();
    },
    
    // Get news by category
    getNewsByCategory: async (category: string, limit: number = 20, userId?: number) => {
      const params = new URLSearchParams({ category, limit: limit.toString() });
      if (userId) params.append('user_id', userId.toString());
      const res = await fetch(`${API_BASE_URL}/feed/real/category/${category}?${params}`);
      return res.json();
    },
    
    // Summarize article
    summarizeArticle: async (summaryData: { article_url: string; article_title: string; article_content: string }) => {
      const res = await fetch(`${API_BASE_URL}/feed/real/summarize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(summaryData),
      });
      return res.json();
    },
    
    // User preferences
    getUserPreferences: async (userId: number) => {
      const res = await fetch(`${API_BASE_URL}/feed/real/preferences/${userId}`);
      if (!res.ok) throw new Error('Preferences not found');
      return res.json();
    },
    
    createUserPreferences: async (userId: number, preferences: any) => {
      const res = await fetch(`${API_BASE_URL}/feed/real/preferences/${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(preferences),
      });
      return res.json();
    },
    
    updateUserPreferences: async (userId: number, preferences: any) => {
      const res = await fetch(`${API_BASE_URL}/feed/real/preferences/${userId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(preferences),
      });
      return res.json();
    },
  },
  
  // ==================== VIDEO EDITOR ====================
  
  videos: {
    upload: async (formData: FormData) => {
      const res = await fetch(`${API_BASE_URL}/videos/videos/upload`, {
        method: 'POST',
        body: formData,
      });
      return res.json();
    },
    
    get: async (videoId: number) => {
      const res = await fetch(`${API_BASE_URL}/videos/videos/${videoId}`);
      return res.json();
    },
    
    detectScenes: async (videoId: number) => {
      const res = await fetch(`${API_BASE_URL}/videos/videos/${videoId}/detect-scenes`, {
        method: 'POST',
      });
      return res.json();
    },
    
    getScenes: async (videoId: number) => {
      const res = await fetch(`${API_BASE_URL}/videos/videos/${videoId}/scenes`);
      return res.json();
    },
    
    generateCaptions: async (videoId: number, language: string = 'en') => {
      const res = await fetch(`${API_BASE_URL}/videos/videos/${videoId}/generate-captions?language=${language}`, {
        method: 'POST',
      });
      return res.json();
    },
    
    getCaptions: async (videoId: number) => {
      const res = await fetch(`${API_BASE_URL}/videos/videos/${videoId}/captions`);
      return res.json();
    },
    
    editCaption: async (captionId: number, newText: string) => {
      const res = await fetch(`${API_BASE_URL}/videos/captions/${captionId}?new_text=${encodeURIComponent(newText)}`, {
        method: 'PUT',
      });
      return res.json();
    },
    
    selectThumbnail: async (videoId: number) => {
      const res = await fetch(`${API_BASE_URL}/videos/videos/${videoId}/select-thumbnail`, {
        method: 'POST',
      });
      return res.json();
    },
    
    getExportPresets: async () => {
      const res = await fetch(`${API_BASE_URL}/videos/export-presets`);
      return res.json();
    },
    
    export: async (videoId: number, exportData: any) => {
      const res = await fetch(`${API_BASE_URL}/videos/videos/${videoId}/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(exportData),
      });
      return res.json();
    },
    
    getSuggestions: async (videoId: number) => {
      const res = await fetch(`${API_BASE_URL}/videos/videos/${videoId}/suggestions`);
      return res.json();
    },
  },
};
