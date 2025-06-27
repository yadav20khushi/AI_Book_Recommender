import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ShieldCheck, Search, Library, MoreHorizontal } from 'lucide-react'
import Sidebar from '../components/Sidebar'


export default function HomePage1() {
    const [collapsed, setCollapsed] = useState(false)
    const [message, setMessage] = useState('')
    const navigate = useNavigate()
    const [sending, setSending] = useState(false)


    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!message.trim()) return;

        setSending(true)

        try {
            const res = await fetch('http://127.0.0.1:8000/api/chat/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'chat', message }),
            });

            const data = await res.json();

            if (data.success) {
                // Pass search_query instead of query
                navigate(`/result?search_query=${encodeURIComponent(message)}`, {
                    state: {
                        books: data.books || [],
                        responseText: data.response || '',
                    },
                });
            } else {
                alert('🔴 검색 실패: ' + data.error);
            }
        } catch (err) {
            console.error('Error during search:', err);
            alert('서버 오류가 발생했습니다.');
        } finally {
            setSending(false)
            setMessage('');
        }
    };


    return (
        <div className="flex min-h-screen bg-[#0f0f0f] text-white">
            <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />

            {/* Main */}
            <div className="flex-1 flex flex-col justify-center items-center p-6">
                <h1 className="text-2xl sm:text-3xl font-bold mb-10 text-white">
                    <span className="font-semibold text-white">안녕~</span> 오늘은 어떤 책 읽고 싶어?
                </h1>

                <div className="flex flex-wrap justify-center gap-4 mb-12">
                    <button
                        onClick={() => navigate('/keyword')}
                        className="w-52 h-32 flex items-center justify-center text-center px-4 py-4 rounded-2xl bg-[#1a1a1a] border border-gray-600 text-sm font-medium text-gray-200 shadow-sm hover:shadow-lg hover:bg-[#2a2a2a] hover:border-gray-400 transition-transform duration-200 hover:-translate-y-1 cursor-pointer"
                    >
                        이번 달 인기 키워드로 책 찾아보기
                    </button>
                    <button
                        onClick={() => navigate('/age-group')}
                        className="w-52 h-32 flex items-center justify-center text-center px-4 py-4 rounded-2xl bg-[#1a1a1a] border border-gray-600 text-sm font-medium text-gray-200 shadow-sm hover:shadow-lg hover:bg-[#2a2a2a] hover:border-gray-400 transition-transform duration-200 hover:-translate-y-1 cursor-pointer"

                    >
                        연령대별 추천 도서 보기
                    </button>
                    <button
                        onClick={() => navigate('/bestsellers')}
                        className="w-52 h-32 flex items-center justify-center text-center px-4 py-4 rounded-2xl bg-[#1a1a1a] border border-gray-600 text-sm font-medium text-gray-200 shadow-sm hover:shadow-lg hover:bg-[#2a2a2a] hover:border-gray-400 transition-transform duration-200 hover:-translate-y-1 cursor-pointer"

                    >
                        이번 달 베스트셀러 확인하기
                    </button>
                </div>

                {/* Search input */}
                <form
                    onSubmit={handleSubmit}
                    className="w-full max-w-2xl px-4"
                >
                    <div className="flex items-center px-5 py-3 bg-[#374151] rounded-full shadow-lg border border-[#4b5563]">
                        <button type="button" className="text-gray-400 mr-3">
                            <Library className="w-5 h-5" />
                        </button>
                        <input
                            type="text"
                            className="flex-1 bg-transparent text-white outline-none border-none placeholder-gray-400"
                            placeholder="Type your message here..."
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                        />
                        <button
                            type="submit"
                            disabled={sending}
                            className={`px-6 py-2 rounded-full bg-blue-600 text-white font-semibold transition-all duration-200 
              hover:bg-blue-700 hover:scale-105 focus:outline-none 
              ${sending ? 'opacity-60 cursor-not-allowed' : ''}`}
                        >
                            {sending ? 'Sending...' : 'Send'}
                        </button>

                    </div>
                </form>
            </div>
        </div>
    )
}