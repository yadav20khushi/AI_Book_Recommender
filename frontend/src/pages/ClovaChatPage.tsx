import React, { useEffect, useRef, useState } from 'react'
import { useLocation } from 'react-router-dom'
import Sidebar from '../components/Sidebar'

type Message = {
    role: 'user' | 'assistant'
    content: string
}

export default function ClovaChatPage() {
    const location = useLocation()
    const isbn13 = location.state?.isbn13

    const [bookInfo, setBookInfo] = useState<any>(null)
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const [chatStarted, setChatStarted] = useState(false)
    const [clovaMessages, setClovaMessages] = useState<Message[]>([])
    const messagesEndRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [clovaMessages])

    const fetchedRef = useRef(false)

    function getCookie(name: string): string | undefined {
        const match = document.cookie
            .split('; ')
            .find(row => row.startsWith(name + '='));
        return match ? decodeURIComponent(match.split('=')[1]) : undefined;
    }

    const csrfToken = getCookie('csrftoken');

    useEffect(() => {
        const fetchBookMetadataAndInitClova = async () => {
            if (!isbn13 || fetchedRef.current) return
            fetchedRef.current = true

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
                    setClovaMessages((prev) => [
                        ...prev,
                        { role: 'assistant', content: clovaData.clova_response }
                    ])
                    setChatStarted(true)
                }
            } catch (err) {
                console.error('❌ Error initializing Clova chat:', err)
            } finally {
                setLoading(false)
            }
        }

        fetchBookMetadataAndInitClova()
    }, [isbn13])




    // const sendMessage = async (e: React.FormEvent) => {
    //     e.preventDefault()
    //     if (!input.trim()) return

    //     const newUserMessage: Message = {
    //         role: 'user',
    //         content: input,
    //     }
    //     setClovaMessages((prev) => [...prev, newUserMessage])
    //     setInput('')
    //     setLoading(true)
    //     setChatStarted(true)

    //     try {
    //         const res = await fetch('http://127.0.0.1:8000/recommend/api/followup_question/', {
    //             method: 'POST',
    //             headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    //             body: new URLSearchParams({ user_input: input }),
    //             credentials: 'include',
    //         })
    //         const data = await res.json()
    //         setClovaMessages((prev) => [
    //             ...prev,
    //             { role: 'assistant', content: data.clova_response },
    //         ])
    //     } catch (err) {
    //         console.error('❌ Clova follow-up failed:', err)
    //     } finally {
    //         setLoading(false)
    //     }
    // }

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
            setClovaMessages((prev) => [
                ...prev,
                { role: 'assistant', content: data.clova_response },
            ])
        } catch (err) {
            console.error('❌ Clova follow-up failed:', err)
        } finally {
            setLoading(false)
        }
    }


    const displayTextFor = (endpoint: string): string => {
        switch (endpoint) {
            case 'book_description': return '설명을 해주세요'
            case 'similar_books': return '비슷한 책 추천해주세요'
            case 'advanced_books': return '고급 레벨 권장'
            case 'check_availability': return '가용성 확인'
            default: return '요청을 보냈습니다'
        }
    }

    const fetchFromAPI = async (endpoint: string, bodyObj: Record<string, string>) => {
        setLoading(true)
        setChatStarted(true)

        const userMessage: Message = {
            role: 'user',
            content: displayTextFor(endpoint),
        }

        try {
            const res = await fetch(`/api/${endpoint}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken ?? '',
                },
                body: new URLSearchParams(bodyObj),
                credentials: 'include',
            })

            const data = await res.json()

            let content = ''

            if (Array.isArray(data.data)) {
                const book = data.data[0]
                content = `📘 ${book.title}\n👤 ${book.authors}\n📝 ${book.description}`
            } else if (Array.isArray(data.books)) {
                content = data.books
                    .map((book: { title: string; author: string }) => `📘 ${book.title}\n👤 ${book.author}`)
                    .join('\n\n')
            } else if (typeof data.availability === 'string') {
                content = data.availability
            } else {
                content = JSON.stringify(data, null, 2)
            }

            setClovaMessages((prev) => [...prev, userMessage, { role: 'assistant', content }])
        } catch (err) {
            console.error(`❌ Failed to fetch ${endpoint}`, err)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="flex h-screen bg-[#0f0f0f] text-white">
            <Sidebar collapsed={false} onToggle={() => { }} />

            <div className="flex-1 flex">
                {/* Chat Section */}
                <div className="flex-1 flex flex-col p-6">
                    {/* Message List */}
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

                    {/* Action Tiles */}
                    <div className="flex justify-center gap-4 my-4 flex-wrap">
                        <button onClick={() => fetchFromAPI('book_description', { isbn13 })} className={tileClass} disabled={!chatStarted || loading}>설명을 해주세요</button>
                        <button onClick={() => fetchFromAPI('similar_books', { isbn13 })} className={tileClass} disabled={!chatStarted || loading}>비슷한 책 추천해주세요</button>
                        <button onClick={() => fetchFromAPI('advanced_books', { isbn13 })} className={tileClass} disabled={!chatStarted || loading}>고급 레벨 권장</button>
                        <button onClick={() => fetchFromAPI('check_availability', { isbn13, lib_code: '110006' })} className={tileClass} disabled={!chatStarted || loading}>가용성 확인</button>
                    </div>

                    {/* Input Bar */}
                    <form onSubmit={sendMessage} className="mt-2 flex items-center gap-3">
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

                {/* Book Info */}
                <div className="w-[260px] p-4 bg-[#111] border-l border-[#2d2d2d] flex flex-col justify-center items-center text-center">
                    {bookInfo ? (
                        <>
                            <img src={bookInfo.cover} alt="cover" className="w-40 h-60 object-cover rounded shadow mb-4" />
                            <div className="text-center">
                                <h2 className="font-bold text-lg mb-1">{bookInfo.title}</h2>
                                <p className="text-sm text-gray-400">{bookInfo.author}</p>
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
    'w-30 h-18 px-4 py-4 flex items-center justify-center text-center bg-[#1a1a1a] border border-gray-600 rounded-2xl text-sm font-medium text-gray-200 shadow-sm transition-transform duration-200 cursor-pointer ' +
    'hover:shadow-lg hover:bg-[#2a2a2a] hover:border-gray-400 hover:-translate-y-1 ' +
    'disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0 disabled:hover:shadow-none'
