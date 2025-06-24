import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ShieldCheck, Search, Library, MoreHorizontal } from 'lucide-react'
import Sidebar from '../components/Sidebar'


export default function HomePage1() {
    const [collapsed, setCollapsed] = useState(false)
    const [message, setMessage] = useState('')
    const navigate = useNavigate()

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        if (message.trim()) {
            console.log('Message:', message)
            setMessage('')
        }
    }

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
                            className="ml-3 bg-white text-black w-9 h-9 rounded-full flex items-center justify-center hover:scale-105 transition"
                        >
                            <svg viewBox="0 0 24 24" className="w-4 h-4">
                                <path d="M2,21L23,12L2,3V10L17,12L2,14V21Z" fill="currentColor" />
                            </svg>
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}
