'use client';

import { useState } from 'react';

interface Post {
  id: number;
  author: string;
  role: string;
  content: string;
  time: string;
  likes: number;
  liked: boolean;
}

export default function Home() {
  const [posts, setPosts] = useState<Post[]>([
    {
      id: 1,
      author: "Sarah the Solopreneur",
      role: "Freelance Designer | 4-hour workdays",
      content: "Just wrapped up a client project at 2 PM. Time to hit the beach. This is why I quit my 9-5.",
      time: "2h ago",
      likes: 42,
      liked: false
    },
    {
      id: 2,
      author: "Mike the Maker",
      role: "Indie Hacker | Building in public",
      content: "Shipped 3 features this week while working from a van in Utah. No stand-ups, no meetings, just building.",
      time: "5h ago",
      likes: 89,
      liked: false
    },
    {
      id: 3,
      author: "Alex the Artist",
      role: "Creative | Work when inspired",
      content: "Started work at midnight because that's when creativity struck. Finished at 4 AM. Freedom hits different.",
      time: "8h ago",
      likes: 63,
      liked: false
    }
  ]);

  const [newPost, setNewPost] = useState('');
  const [error, setError] = useState('');

  const handlePost = () => {
    const bannedWords = ['congratulations', 'congrats', 'congratulate', 'pleased to announce', 'happy to announce', 'excited to announce'];
    const lowerContent = newPost.toLowerCase();

    if (bannedWords.some(word => lowerContent.includes(word))) {
      setError('🚫 DETECTED: This sounds like corporate speak. No congratulations allowed on LinkedOut!');
      return;
    }

    if (newPost.trim().length === 0) {
      setError('Post cannot be empty');
      return;
    }

    const post: Post = {
      id: posts.length + 1,
      author: "You",
      role: "Escaped the 9-5 | Living free",
      content: newPost,
      time: "Just now",
      likes: 0,
      liked: false
    };

    setPosts([post, ...posts]);
    setNewPost('');
    setError('');
  };

  const handleLike = (postId: number) => {
    setPosts(posts.map(post => {
      if (post.id === postId) {
        return {
          ...post,
          likes: post.liked ? post.likes - 1 : post.likes + 1,
          liked: !post.liked
        };
      }
      return post;
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-black">
      {/* Header */}
      <header className="bg-black/40 backdrop-blur-xl border-b border-purple-500/20 sticky top-0 z-50 shadow-lg shadow-purple-900/20">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="relative group">
                <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 via-pink-600 to-red-600 rounded-xl blur opacity-75 group-hover:opacity-100 transition duration-300"></div>
                <div className="relative w-11 h-11 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center text-white font-bold text-xl shadow-xl">
                  LO
                </div>
              </div>
              <div>
                <h1 className="text-2xl sm:text-3xl font-black bg-gradient-to-r from-purple-400 via-pink-400 to-red-400 bg-clip-text text-transparent">
                  LinkedOut
                </h1>
                <p className="text-xs text-gray-400 font-medium -mt-1">Where freedom works</p>
              </div>
            </div>
            <div className="hidden sm:flex items-center gap-2 px-4 py-2 rounded-full bg-red-500/10 border border-red-500/30">
              <span className="text-red-400 text-sm font-bold">🚫</span>
              <span className="text-red-300 text-sm font-semibold">No 9-5 Zone</span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
        {/* Create Post */}
        <div className="relative group mb-8">
          <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl blur opacity-25 group-hover:opacity-40 transition duration-300"></div>
          <div className="relative bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl p-6 border border-purple-500/20 shadow-2xl">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-bold text-lg shadow-lg">
                Y
              </div>
              <div>
                <h2 className="text-lg font-bold text-white">Share your story</h2>
                <p className="text-sm text-gray-400">No suits, no BS, just real talk</p>
              </div>
            </div>
            <textarea
              value={newPost}
              onChange={(e) => {
                setNewPost(e.target.value);
                setError('');
              }}
              placeholder="What are you building? Where are you? When did you start your day? (Corporate jargon will be rejected)"
              className="w-full p-4 bg-black/30 border border-purple-500/30 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 text-white placeholder-gray-500 transition-all"
              rows={4}
            />
            {error && (
              <div className="mt-3 p-4 bg-red-900/20 border border-red-500/40 rounded-xl text-red-300 text-sm font-semibold backdrop-blur-sm flex items-start gap-3">
                <span className="text-xl">⚠️</span>
                <span>{error}</span>
              </div>
            )}
            <div className="mt-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              <div className="flex flex-wrap gap-2 text-xs">
                <span className="px-3 py-1 bg-red-500/10 border border-red-500/30 rounded-full text-red-300 font-medium">
                  🚫 congratulations
                </span>
                <span className="px-3 py-1 bg-red-500/10 border border-red-500/30 rounded-full text-red-300 font-medium">
                  🚫 happy to announce
                </span>
                <span className="px-3 py-1 bg-red-500/10 border border-red-500/30 rounded-full text-red-300 font-medium">
                  🚫 excited to share
                </span>
              </div>
              <button
                onClick={handlePost}
                className="relative group/btn w-full sm:w-auto"
              >
                <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl blur opacity-75 group-hover/btn:opacity-100 transition duration-300"></div>
                <div className="relative bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-3 rounded-xl font-bold hover:from-purple-700 hover:to-pink-700 transition-all shadow-xl">
                  Post to LinkedOut
                </div>
              </button>
            </div>
          </div>
        </div>

        {/* Feed */}
        <div className="space-y-6">
          {posts.map((post) => (
            <div key={post.id} className="relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-purple-600/30 to-pink-600/30 rounded-2xl blur opacity-0 group-hover:opacity-100 transition duration-300"></div>
              <div className="relative bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl p-6 border border-purple-500/20 hover:border-purple-500/40 shadow-xl transition-all duration-300">
                <div className="flex items-start gap-4">
                  <div className="relative">
                    <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full blur opacity-50"></div>
                    <div className="relative w-14 h-14 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-bold text-xl shadow-lg flex-shrink-0 border-2 border-purple-400/30">
                      {post.author[0]}
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="font-bold text-white text-lg">{post.author}</h3>
                        <p className="text-sm text-purple-300/80 font-medium">{post.role}</p>
                      </div>
                      <span className="text-sm text-gray-500 font-medium whitespace-nowrap ml-4">{post.time}</span>
                    </div>
                    <p className="text-gray-300 leading-relaxed mb-6 text-base">{post.content}</p>
                    <div className="flex items-center gap-6">
                      <button
                        onClick={() => handleLike(post.id)}
                        className={`group/like flex items-center gap-2 transition-all ${
                          post.liked
                            ? 'text-pink-400'
                            : 'text-gray-400 hover:text-pink-400'
                        }`}
                      >
                        <div className={`p-2 rounded-lg transition-all ${
                          post.liked
                            ? 'bg-pink-500/20'
                            : 'bg-gray-800/50 group-hover/like:bg-pink-500/10'
                        }`}>
                          <svg className="w-5 h-5" fill={post.liked ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                          </svg>
                        </div>
                        <span className="font-semibold">{post.likes}</span>
                      </button>
                      <button className="group/comment flex items-center gap-2 text-gray-400 hover:text-purple-400 transition-all">
                        <div className="p-2 rounded-lg bg-gray-800/50 group-hover/comment:bg-purple-500/10 transition-all">
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                          </svg>
                        </div>
                        <span className="font-semibold">Comment</span>
                      </button>
                      <button className="group/share flex items-center gap-2 text-gray-400 hover:text-blue-400 transition-all">
                        <div className="p-2 rounded-lg bg-gray-800/50 group-hover/share:bg-blue-500/10 transition-all">
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                          </svg>
                        </div>
                        <span className="font-semibold">Share</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="mt-16 text-center">
          <div className="inline-block p-8 rounded-2xl bg-gradient-to-br from-slate-900/50 to-slate-800/50 border border-purple-500/20 backdrop-blur-sm">
            <p className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
              LinkedOut
            </p>
            <p className="text-gray-400 text-sm mb-1">Where the 9-5 escapees gather</p>
            <p className="text-gray-500 text-xs">No suits • No meetings • No congratulations</p>
          </div>
        </div>
      </main>
    </div>
  );
}
