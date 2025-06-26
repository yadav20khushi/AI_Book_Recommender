import React, { useEffect, useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import Sidebar from '../components/Sidebar'

interface Book {
    title: string
    isbn13: string
    author: string
    cover: string
}

export default function ResultsPage() {
    const [books, setBooks] = useState<Book[]>([])
    const [loading, setLoading] = useState(true)
    const [collapsed, setCollapsed] = useState(false)
    const [searchParams] = useSearchParams()
    const keyword = searchParams.get('query') || ''
    const navigate = useNavigate()
    const ageGroup = searchParams.get('age_group') || ''
    const similarTo = searchParams.get('similar_to') || ''
    const advancedFrom = searchParams.get('advanced_from') || ''

    function getCookie(name: string): string | undefined {
        const match = document.cookie
            .split('; ')
            .find(row => row.startsWith(name + '='));
        return match ? decodeURIComponent(match.split('=')[1]) : undefined;
    }


    const csrfToken = getCookie('csrftoken');

    useEffect(() => {
        const fetchBooks = async () => {
            try {
                let endpoint = ''
                let payload = {}

                if (ageGroup) {
                    endpoint = 'http://127.0.0.1:8000/api/books_by_agegroup/'
                    payload = { age_group: ageGroup }
                } else if (keyword) {
                    endpoint = 'http://127.0.0.1:8000/api/books_by_keyword/'
                    payload = { keyword }
                } else if (similarTo || advancedFrom) {
                    endpoint = 'http://127.0.0.1:8000/api/recommendation/'
                    payload = {
                        isbn13: similarTo || advancedFrom,
                        recommendation_type: similarTo ? 'reader' : 'mania'
                    }
                } else {
                    console.warn('❌ No query provided.')
                    setBooks([])
                    setLoading(false)
                    return
                }


                const res = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken ?? '',
                    },
                    body: JSON.stringify(payload),
                    credentials: 'include',
                })

                const data = await res.json()
                setBooks(data.books || [])
            } catch (err) {
                console.error('Failed to fetch books:', err)
            } finally {
                setLoading(false)
            }
        }


        fetchBooks()
    }, [keyword])



    return (
        <div className="flex h-screen bg-[#0f0f0f] text-white">
            <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />

            <main className="flex-1 p-8 overflow-y-auto">
                <h1 className="text-2xl font-bold mb-6 text-center">
                    {ageGroup ? (
                        <>📖 Books for age group: <span className="text-blue-400 capitalize">{ageGroup}</span></>
                    ) : keyword ? (
                        <>🔍 Books for keyword: <span className="text-blue-400">{keyword}</span></>
                    ) : similarTo ? (
                        <>🔁 Similar books <span className="text-blue-400"></span></>
                    ) : advancedFrom ? (
                        <>📘 Advanced picks <span className="text-blue-400"></span></>
                    ) : (
                        '📚 Recommended Books'
                    )}
                </h1>


                {loading ? (
                    <p className="text-center text-gray-400">Loading books...</p>
                ) : books.length === 0 ? (
                    <p className="mx-auto px-4 py-3 bg-gray-800 text-gray-300 rounded-xl max-w-fit text-sm shadow-md animate-dropIn">
                        {ageGroup ? (
                            <>
                                No books found for age group <span className="text-blue-400 capitalize">"{ageGroup}"</span>.
                            </>
                        ) : keyword ? (
                            <>
                                No books found for keyword <span className="text-blue-400">"{keyword}"</span>.
                            </>
                        ) : similarTo ? (
                            <>
                                No similar books Found <span className="text-blue-400"></span>.
                            </>
                        ) : advancedFrom ? (
                            <>
                                No Advanced Recommendations <span className="text-blue-400"></span>.
                            </>
                        ) : (
                            'No books found.'
                        )}
                    </p>
                ) : (
                    <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4">
                        {books.map((book, index) => (
                            <div
                                key={book.isbn13 || index}
                                onClick={() => navigate('/clova-chat', { state: { isbn13: book.isbn13 } })}
                                className="bg-[#1a1a1a] p-4 rounded-xl shadow cursor-pointer transition hover:scale-105 hover:shadow-2xl"
                            >
                                <img
                                    src={book.cover || 'https://via.placeholder.com/150'}
                                    alt={book.title}
                                    className="w-full h-64 object-contain rounded bg-[#0f0f0f] mb-2"
                                />
                                <h2 className="font-semibold text-lg mb-1">{book.title}</h2>
                                <p className="text-sm text-gray-400">{book.author}</p>
                            </div>

                        ))}
                    </div>
                )}
            </main>
        </div>
    )
}
