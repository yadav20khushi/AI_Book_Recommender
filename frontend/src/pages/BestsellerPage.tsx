import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Sidebar from '../components/Sidebar'


interface Book {
    title: string
    isbn13: string
    author: string
    cover: string
}

export default function BestsellerPage() {
    const [books, setBooks] = useState<Book[]>([])
    const [loading, setLoading] = useState(true)
    const navigate = useNavigate()
    const [collapsed, setCollapsed] = useState(false)

    useEffect(() => {
        const fetchBestsellers = async () => {
            try {
                const res = await fetch('http://127.0.0.1:8000/api/bestsellers/')
                const data = await res.json()
                setBooks(data.books || [])
            } catch (err) {
                console.error('Failed to fetch bestsellers:', err)
            } finally {
                setLoading(false)
            }
        }

        fetchBestsellers()
    }, [])

    const handleBookClick = (book: Book) => {
        navigate('/clova-chat', { state: { isbn13: book.isbn13 } })
    }

    return (
        <div className="flex min-h-screen bg-[#0f0f0f] text-white">
            <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />

            <main className="flex-1 p-6 overflow-y-auto">
                <h1 className="text-3xl font-bold text-center mb-10">이달의 베스트셀러</h1>

                {loading ? (
                    <p className="text-center text-gray-400">Loading...</p>
                ) : (
                    <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4">

                        {books.map((book, index) => (
                            <div
                                key={index}
                                onClick={() => handleBookClick(book)}
                                className="bg-[#1a1a1a] p-4 rounded-xl shadow cursor-pointer transition hover:scale-105 hover:shadow-2xl"
                            >
                                <img
                                    src={book.cover}
                                    alt={book.title}
                                    className="w-full h-64 object-contain rounded mb-4 bg-[#0f0f0f]"
                                />
                                <h2 className="font-semibold text-sm mb-1">{book.title}</h2>
                                <p className="text-xs text-gray-400">{book.author}</p>
                            </div>
                        ))}
                    </div>
                )}
            </main>
        </div>
    )
}