'use client';

import { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { apiClient } from '@/lib/api';

interface VideoState {
  id?: number;
  title: string;
  duration: number;
  processing_status: string;
}

interface Scene {
  id: number;
  start_time: number;
  end_time: number;
  scene_type: string;
  confidence: number;
}

interface Caption {
  id: number;
  text: string;
  start_time: number;
  end_time: number;
}

export default function VideoEditor() {
  const [video, setVideo] = useState<VideoState | null>(null);
  const [scenes, setScenes] = useState<Scene[]>([]);
  const [captions, setCaptions] = useState<Caption[]>([]);
  const [suggestions, setSuggestions] = useState<any>(null);
  const [thumbnail, setThumbnail] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState<'upload' | 'process' | 'edit' | 'export'>('upload');
  const [exportPresets, setExportPresets] = useState<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleVideoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('title', file.name);
      formData.append('file', file);

      const uploadedVideo = await apiClient.videos.upload(formData);
      setVideo(uploadedVideo);
      setCurrentStep('process');

      // Auto-start scene detection
      setTimeout(() => detectScenes(uploadedVideo.id), 1000);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to upload video');
    } finally {
      setLoading(false);
    }
  };

  const detectScenes = async (videoId: number): Promise<void> => {
    setLoading(true);
    try {
      const result = await apiClient.videos.detectScenes(videoId);
      setScenes(result.scenes ?? []);

      // Get suggestions
      const sug = await apiClient.videos.getSuggestions(videoId);
      setSuggestions(sug);

      // Generate captions
      setTimeout(() => generateCaptions(videoId), 1000);
    } catch (error) {
      console.error('Scene detection failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateCaptions = async (videoId: number): Promise<void> => {
    setLoading(true);
    try {
      const result = await apiClient.videos.generateCaptions(videoId);
      setCaptions(result.captions ?? []);

      // Select thumbnail
      setTimeout(() => selectThumbnail(videoId), 500);
    } catch (error) {
      console.error('Caption generation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const selectThumbnail = async (videoId: number): Promise<void> => {
    try {
      const result = await apiClient.videos.selectThumbnail(videoId);
      setThumbnail(result);
      setCurrentStep('edit');
    } catch (error) {
      console.error('Thumbnail selection failed:', error);
    }
  };

  const handleEditCaption = async (captionId: number, newText: string): Promise<void> => {
    try {
      await apiClient.videos.editCaption(captionId, newText);
      const updated = captions.map(c =>
        c.id === captionId ? { ...c, text: newText } : c
      );
      setCaptions(updated);
    } catch (error) {
      console.error('Failed to edit caption:', error);
    }
  };

  const handleExport = async (platform: string): Promise<void> => {
    if (!video?.id) return;

    setLoading(true);
    try {
      const presets = await apiClient.videos.getExportPresets();
      const preset = presets.presets[
        Object.keys(presets.presets)[0]
      ];

      const result = await apiClient.videos.export(video.id, {
        preset: {
          platform,
          aspect_ratio: preset.aspect_ratio,
          resolution: preset.resolution,
        },
        apply_captions: true,
      });

      alert(`Export started for ${platform}!\n${result.estimated_time}`);
      setCurrentStep('export');
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-amber-900 to-slate-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-2">
            🎬 AI-Assisted Video Editor
          </h1>
          <p className="text-amber-300">
            Automated scene detection, captions, and optimization
          </p>
        </motion.div>

        {/* Step Indicator */}
        <div className="flex gap-2 mb-8 justify-center">
          {(['upload', 'process', 'edit', 'export'] as const).map((step: string, index: number) => (
            <motion.div
              key={step}
              className={`flex items-center ${
                index < 3 ? 'after:content-["→"] after:mx-2 after:text-gray-400' : ''
              }`}
            >
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center font-bold transition ${
                  currentStep === step
                    ? 'bg-amber-600 text-white'
                    : currentStep > step
                      ? 'bg-green-600 text-white'
                      : 'bg-slate-700 text-gray-400'
                }`}
              >
                {index + 1}
              </div>
              <span className="text-gray-400 ml-2 text-sm hidden sm:inline">
                {step}
              </span>
            </motion.div>
          ))}
        </div>

        {/* Upload Step */}
        {currentStep === 'upload' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-slate-800/50 backdrop-blur-lg rounded-xl p-12 border border-amber-500/20 text-center"
          >
            <div className="mb-6">
              <div className="text-6xl mb-4">🎥</div>
              <h2 className="text-2xl font-bold text-white mb-2">Upload Your Video</h2>
              <p className="text-gray-400">
                Drag & drop or click to select your raw footage
              </p>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              onChange={handleVideoUpload}
              className="hidden"
            />

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => fileInputRef.current?.click()}
              disabled={loading}
              className="bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700 text-white px-8 py-4 rounded-lg font-semibold text-lg transition disabled:opacity-50"
            >
              {loading ? '⏳ Uploading...' : '+ Choose Video'}
            </motion.button>
          </motion.div>
        )}

        {/* Processing Step */}
        {currentStep === 'process' && video && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Video Info */}
            <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-amber-500/20">
              <h3 className="text-xl font-bold text-white mb-4">📹 Video Information</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="bg-slate-700/50 p-4 rounded-lg">
                  <div className="text-gray-400 text-sm">Title</div>
                  <div className="text-lg font-semibold text-white">{video.title}</div>
                </div>
                <div className="bg-slate-700/50 p-4 rounded-lg">
                  <div className="text-gray-400 text-sm">Duration</div>
                  <div className="text-lg font-semibold text-white">
                    {Math.floor(video.duration / 60)}:{String(Math.floor(video.duration % 60)).padStart(2, '0')}
                  </div>
                </div>
                <div className="bg-slate-700/50 p-4 rounded-lg">
                  <div className="text-gray-400 text-sm">Status</div>
                  <div className="text-lg font-semibold text-amber-400">
                    {loading ? '⏳ Processing' : '✓ Ready'}
                  </div>
                </div>
              </div>
            </div>

            {/* Scenes Timeline */}
            {(scenes?.length ?? 0) > 0 && (
              <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-amber-500/20">
                <h3 className="text-xl font-bold text-white mb-4">🎞️ Detected Scenes ({scenes?.length ?? 0})</h3>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {scenes.map((scene: Scene) => (
                    <motion.div
                      key={scene.id}
                      whileHover={{ scale: 1.02 }}
                      className="bg-slate-700/50 p-3 rounded-lg border border-amber-400/20 flex items-center justify-between"
                    >
                      <div>
                        <div className="font-semibold text-white">
                          {scene.scene_type.toUpperCase()}
                        </div>
                        <div className="text-sm text-gray-400">
                          {scene.start_time.toFixed(2)}s - {scene.end_time.toFixed(2)}s
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-amber-400 font-bold">
                          {Math.round(scene.confidence * 100)}%
                        </div>
                        <div className="text-xs text-gray-400">confidence</div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {/* Suggestions */}
            {suggestions && (
              <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-blue-500/20">
                <h3 className="text-xl font-bold text-white mb-4">💡 AI Suggestions</h3>
                <div className="space-y-2">
                  {suggestions.editing_tips?.map((tip: string, i: number) => (
                    <div
                      key={i}
                      className="bg-blue-500/10 border border-blue-500/30 text-blue-200 p-3 rounded-lg text-sm"
                    >
                      ✓ {tip}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <button
              onClick={() => setCurrentStep('edit')}
              className="w-full bg-green-600 hover:bg-green-700 text-white py-3 rounded-lg font-semibold transition"
            >
              ✓ Continue to Editing
            </button>
          </motion.div>
        )}

        {/* Editing Step */}
        {currentStep === 'edit' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Thumbnail */}
            {thumbnail && (
              <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-amber-500/20">
                <h3 className="text-xl font-bold text-white mb-4">🖼️ Thumbnail Preview</h3>
                <div className="bg-slate-900 rounded-lg p-4 text-center">
                  <div className="text-6xl mb-4">{thumbnail.frame_time}s</div>
                  <div className="text-gray-400">
                    Optimal frame selected for maximum CTR
                  </div>
                </div>
              </div>
            )}

            {/* Captions Editor */}
            {(captions?.length ?? 0) > 0 && (
              <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-amber-500/20">
                <h3 className="text-xl font-bold text-white mb-4">📝 Edit Captions ({captions?.length ?? 0})</h3>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {captions.map((caption: Caption) => (
                    <div
                      key={caption.id}
                      className="bg-slate-700/50 p-4 rounded-lg border border-amber-400/20"
                    >
                      <div className="text-gray-400 text-sm mb-2">
                        {caption.start_time.toFixed(2)}s - {caption.end_time.toFixed(2)}s
                      </div>
                      <input
                        type="text"
                        defaultValue={caption.text}
                        onBlur={(e) =>
                          handleEditCaption(caption.id, e.target.value)
                        }
                        className="w-full bg-slate-800 text-white border border-amber-400/30 rounded px-3 py-2"
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}

            <button
              onClick={() => setCurrentStep('export')}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg font-semibold transition"
            >
              ✓ Continue to Export
            </button>
          </motion.div>
        )}

        {/* Export Step */}
        {currentStep === 'export' && video && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-slate-800/50 backdrop-blur-lg rounded-xl p-6 border border-amber-500/20"
          >
            <h2 className="text-2xl font-bold text-white mb-6">📤 Export for Platforms</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {['instagram_reels', 'youtube_shorts', 'tiktok', 'linkedin'].map(
                (platform) => (
                  <motion.button
                    key={platform}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() =>
                      handleExport(platform.replace('_', ' '))
                    }
                    disabled={loading}
                    className="bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700 text-white py-4 rounded-lg font-semibold transition disabled:opacity-50"
                  >
                    {loading ? '⏳' : '📱'} {platform.toUpperCase()}
                  </motion.button>
                )
              )}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
