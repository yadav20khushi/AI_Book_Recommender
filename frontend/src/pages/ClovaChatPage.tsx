import React, { useEffect, useRef, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import { useClovaChat } from '../context/ClovaChatContext'

type Message = {
    role: 'user' | 'assistant'
    content: string
}

export default function ClovaChatPage() {
    const location = useLocation()
    const navigate = useNavigate()
    const incomingIsbn = location.state?.isbn13 || null
    const [isbn13, setIsbn13] = useState(incomingIsbn)
    const { bookInfo, setBookInfo, clovaMessages, setClovaMessages, chatStarted, setChatStarted } = useClovaChat()
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const [availabilityMsg, setAvailabilityMsg] = useState<string | null>(null)
    const messagesEndRef = useRef<HTMLDivElement>(null)
    const [fadeOut, setFadeOut] = useState(false)
    const fetchedRef = useRef(false)

    function getCookie(name: string): string | undefined {
        const match = document.cookie.split('; ').find(row => row.startsWith(name + '='))
        return match ? decodeURIComponent(match.split('=')[1]) : undefined
    }

    const csrfToken = getCookie('csrftoken')

    useEffect(() => {
        const saved = sessionStorage.getItem('clovaChat')
        const savedData = saved ? JSON.parse(saved) : null
        const savedIsbn = savedData?.isbn13

        if (incomingIsbn && incomingIsbn !== savedIsbn) {
            sessionStorage.removeItem('clovaChat')
            setIsbn13(incomingIsbn)
        } else if (!incomingIsbn && savedIsbn) {
            setIsbn13(savedIsbn)
        }
    }, [incomingIsbn])

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [clovaMessages])

    useEffect(() => {
        const saved = sessionStorage.getItem('clovaChat')
        const savedData = saved ? JSON.parse(saved) : null
        const savedIsbn = savedData?.isbn13

        if (!isbn13 || fetchedRef.current || isbn13 === savedIsbn) return
        fetchedRef.current = true

        const fetchBookMetadataAndInitClova = async () => {
            setClovaMessages([])
            setChatStarted(false)

            try {
                const metadataRes = await fetch('/api/book_metadata/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrfToken ?? '',
                    },
                    body: new URLSearchParams({ isbn13 }),
                    credentials: 'include',
                })
                const metadata = await metadataRes.json()
                setBookInfo(metadata)

                setLoading(true)

                const clovaRes = await fetch('/recommend/api/selected_book/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrfToken ?? '',
                    },
                    body: new URLSearchParams({ isbn13 }),
                    credentials: 'include',
                })
                const clovaData = await clovaRes.json()

                if (clovaData?.clova_response) {
                    setClovaMessages([{ role: 'assistant', content: clovaData.clova_response }])
                    setChatStarted(true)
                    sessionStorage.setItem('clovaChat', JSON.stringify({ isbn13 }))
                }
            } catch (err) {
                console.error('❌ Error initializing Clova chat:', err)
            } finally {
                setLoading(false)
            }
        }

        fetchBookMetadataAndInitClova()
    }, [isbn13])

    const sendMessage = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!input.trim()) return

        const newUserMessage: Message = { role: 'user', content: input }
        const updatedMessages = [...clovaMessages, newUserMessage]

        setClovaMessages(updatedMessages)
        setInput('')
        setLoading(true)
        setChatStarted(true)

        try {
            const res = await fetch('/recommend/api/followup_question/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken ?? '',
                },
                body: JSON.stringify({ session_messages: updatedMessages }),
                credentials: 'include',
            })

            const data = await res.json()
            setClovaMessages((prev) => [...prev, { role: 'assistant', content: data.clova_response }])
        } catch (err) {
            console.error('❌ Clova follow-up failed:', err)
        } finally {
            setLoading(false)
        }
    }

    const checkAvailability = async () => {
        try {
            const res = await fetch('/api/check_availability/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken ?? '',
                },
                body: new URLSearchParams({ isbn13, lib_code: '110006' }),
                credentials: 'include',
            })
            const data = await res.json()
            setAvailabilityMsg(data.availability || 'No data available.')
            setFadeOut(false)
            setTimeout(() => setFadeOut(true), 2000)
            setTimeout(() => {
                setAvailabilityMsg(null)
                setFadeOut(false)
            }, 2500)
        } catch (err) {
            console.error('❌ Availability check failed:', err)
            setAvailabilityMsg('Failed to check availability.')
            setTimeout(() => setAvailabilityMsg(null), 3000)
        }
    }

    return (
        <div className="flex h-screen bg-[#0f0f0f] text-white relative">
            <Sidebar collapsed={false} onToggle={() => { }} />

            <div className="flex-1 flex">
                <div className="flex-1 flex flex-col p-6 relative">
                    {availabilityMsg && (
                        <div className="absolute bottom-24 left-[calc(50%-130px)] transform -translate-x-1/2 bg-blue-800 text-gray-100 px-8 py-4 rounded-2xl text-lg shadow-2xl animate-dropIn z-50 ${fadeOut ? 'animate-fadeOut' : ''}">
                            {availabilityMsg}
                        </div>
                    )}

                    <div className="flex-1 overflow-y-auto border border-[#2d2d2d] rounded-lg p-4 space-y-4">
                        {clovaMessages.map((msg, i) => (
                            <div
                                key={i}
                                className={`p-3 max-w-[75%] rounded-xl whitespace-pre-wrap ${msg.role === 'user'
                                    ? 'ml-auto bg-blue-600 text-white'
                                    : 'mr-auto bg-gray-800 text-gray-200'
                                    }`}
                            >
                                {msg.content}
                            </div>
                        ))}
                        {loading && (
                            <div className="mr-auto bg-gray-700 text-white px-4 py-2 rounded-xl text-sm animate-pulse">
                                ⏳ Clova is thinking...
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    <form onSubmit={sendMessage} className="mt-4 flex items-center gap-3">
                        <input
                            className="flex-1 px-4 py-3 rounded-full bg-[#1a1a1a] border border-gray-600 text-white outline-none"
                            placeholder="질문을 입력하세요..."
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            disabled={!chatStarted}
                        />
                        <button
                            type="submit"
                            disabled={loading || !chatStarted}
                            className={tileClass}
                        >
                            Send
                        </button>
                    </form>
                </div>

                <div className="w-[260px] p-4 bg-[#111] border-l border-[#2d2d2d] flex flex-col justify-center items-center text-center">
                    {bookInfo ? (
                        <>
                            <img src={bookInfo.cover} alt="cover" className="w-40 h-60 object-cover rounded shadow mb-4" />
                            <h2 className="font-bold text-lg mb-1">{bookInfo.title}</h2>
                            <p className="text-sm text-gray-400 mb-6">{bookInfo.author}</p>
                            <div className="flex flex-col gap-3">
                                <button onClick={() => navigate(`/result?similar_to=${isbn13}`)} className={tileClass}>비슷한 책 추천해주세요</button>
                                <button onClick={() => navigate(`/result?advanced_from=${isbn13}`)} className={tileClass}>고급 레벨 권장</button>
                                <button onClick={checkAvailability} className={tileClass}>가용성 확인</button>
                            </div>
                        </>
                    ) : (
                        <p className="text-gray-500 text-sm">Loading book info...</p>
                    )}
                </div>
            </div>
        </div>
    )
}

const tileClass =
    'w-44 h-12 px-4 py-2 flex items-center justify-center text-center bg-[#1a1a1a] border border-gray-600 rounded-2xl text-sm font-medium text-gray-200 shadow-sm transition-transform duration-200 cursor-pointer ' +
    'hover:shadow-lg hover:bg-[#2a2a2a] hover:border-gray-400 hover:-translate-y-1 ' +
    'disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0 disabled:hover:shadow-none'
