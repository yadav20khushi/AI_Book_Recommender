import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Sidebar from '../components/Sidebar'

export default function KeywordPage() {
    const [keywords, setKeywords] = useState<string[]>([])
    const [loading, setLoading] = useState(true)
    const [collapsed, setCollapsed] = useState(false)
    const navigate = useNavigate()

    useEffect(() => {
        const fetchKeywords = async () => {
            try {
                const res = await fetch('http://127.0.0.1:8000/api/keywords')
                const data = await res.json()
                setKeywords(data.keywords || [])
            } catch (err) {
                console.error('❌ Failed to fetch keywords', err)
            } finally {
                setLoading(false)
            }
        }

        fetchKeywords()
    }, [])

    const handleKeywordClick = (keyword: string) => {
        navigate(`/result?query=${encodeURIComponent(keyword)}`)
    }

    return (
        <div className="flex h-screen bg-[#0f0f0f] text-white">
            <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />

            <main className="flex-1 flex flex-col justify-center items-center p-6">
                <h1 className="text-4xl font-bold text-center mb-10">📅 이번 달 인기 키워드</h1>

                {loading ? (
                    <p className="text-center text-gray-400">Loading...</p>
                ) : (
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-6 justify-center">
                        {keywords.map((word, idx) => (
                            <button
                                key={idx}
                                onClick={() => handleKeywordClick(word)}
                                className="w-52 h-32 flex items-center justify-center text-center px-4 py-4 rounded-2xl bg-[#1a1a1a] border border-gray-600 text-sm font-medium text-gray-200 shadow-sm hover:shadow-lg hover:bg-[#2a2a2a] hover:border-gray-400 transition-transform duration-200 hover:-translate-y-1 cursor-pointer"
                            >
                                {word}
                            </button>
                        ))}
                    </div>
                )}
            </main>
        </div>
    )
}
