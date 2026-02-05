# 🚀 QUICK START - News Feed Feature

## What You Got

A **complete, AI-powered real-time news feed** with:
- ✅ Real-time news search by user keywords
- ✅ Trending news worldwide
- ✅ AI-powered article summaries (read on platform)
- ✅ Link to read original articles
- ✅ Personalized recommendations based on user interests
- ✅ Smart relevance scoring

---

## ⚡ Quick Setup (5 minutes)

### Step 1: Get FREE NewsAPI Key

1. Go to: https://newsapi.org
2. Click "Get Started" (or "Register")
3. Sign up with email
4. You get FREE API key instantly
5. Copy the key

### Step 2: Add to Configuration

Open file: `backend/.env`

Add this line (paste your API key):
```
NEWS_API_KEY=your_api_key_here
```

Save the file.

### Step 3: Restart Backend

Press Ctrl+C in backend terminal to stop it.

Then run:
```bash
cd backend
python run.py
```

Wait for: `INFO: Application startup complete`

---

## 🎯 How to Use

### Go to News Feed

1. Open http://localhost:3000
2. Navigate to "News Feed" page

### Add Your Interests

1. Click **"⚙️ Preferences"** in sidebar
2. Type an interest (e.g., "Formula 1")
3. Click "+" button
4. Feed updates automatically ✅

### Search for News

1. Click **"🔍 Search"** tab
2. Type keyword
3. Click "Search"
4. See results

### View Trending

1. Click **"🔥 Trending"** tab
2. See what's trending globally
3. Personalized to your interests

### Read Summary

1. Find an article
2. Click **"📄 Summary"** button
3. AI generates summary in seconds
4. Read summary on platform

### Read Full Article

1. Click **"Read More"** link
2. Original article opens in new tab
3. Read full content

---

## 🎨 Features

| Feature | How to Use |
|---------|-----------|
| **Add Interests** | Click ⚙️ → Type keyword → Click + |
| **Search News** | Click 🔍 Search → Type → Search |
| **View Trending** | Click 🔥 Trending |
| **Filter Category** | Select category in sidebar |
| **Get Summary** | Click 📄 Summary button |
| **Read Full Article** | Click "Read More" link |

---

## 📊 What's Happening Behind the Scenes

```
When you add "Formula 1":

1. Interest saved to database
2. Frontend fetches personalized news
3. Backend searches NewsAPI for "Formula 1"
4. Gets 20 latest articles
5. Calculates relevance score for each
6. Sorts by relevance (highest first)
7. Generates AI summaries
8. Returns to frontend
9. You see personalized feed!

When you click "📄 Summary":

1. Article content sent to backend
2. AI BART model processes text
3. Creates 2-3 sentence summary
4. Returns summary
5. You see it on platform instantly!
```

---

## ✨ Cool Features

1. **AI Summaries** - Read without clicking "Read More"
2. **Personalized** - Feed learns your interests
3. **Relevance Score** - See how relevant each article is (%)
4. **Real Data** - From 30,000+ news sources
5. **Works Offline** - App falls back to mock data if API down
6. **Mobile Friendly** - Works on phone/tablet

---

## 🐛 Troubleshooting

**Q: No articles showing?**
- A: Add interests first. Click ⚙️ Preferences → Add keyword

**Q: Summaries not working?**
- A: First summary takes ~30s (model loading). Wait and retry.

**Q: Error connecting to NewsAPI?**
- A: Check internet. Also check API key in `.env` is correct.

---

## 📁 Key Files

```
backend/app/services/news_service.py     ← AI & news logic
backend/app/api/v1/endpoints/news_feed_v2.py ← API endpoints
app/components/PersonalizedNewsFeed_v2.tsx   ← Frontend
app/lib/api.ts                            ← API calls
```

---

## 🎓 API Endpoints (For Developers)

```
GET /api/v1/feed/real/search?keyword=motorsports
→ Search for news

GET /api/v1/feed/real/trending?country=us  
→ Get trending news

GET /api/v1/feed/real/personalized/1
→ Get personalized feed for user 1

POST /api/v1/feed/real/summarize
→ Generate AI summary

POST /api/v1/feed/real/preferences/1
→ Create user preferences

PUT /api/v1/feed/real/preferences/1
→ Update preferences
```

---

## 📚 Full Documentation

See files:
- `NEWS_FEED_DOCS.md` - Technical guide
- `NEWS_FEED_SUMMARY.md` - Complete feature guide  
- `IMPLEMENTATION_COMPLETE.md` - What was built

---

## ✅ You're Ready!

1. ✅ Get API key from newsapi.org
2. ✅ Add to backend/.env
3. ✅ Restart backend
4. ✅ Go to http://localhost:3000/news-feed
5. ✅ Start searching and reading!

**Enjoy your AI-powered news feed!** 🚀
