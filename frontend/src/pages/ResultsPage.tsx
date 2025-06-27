import React, { useEffect, useState } from 'react'
import { useSearchParams, useNavigate, useLocation } from 'react-router-dom'
import Sidebar from '../components/Sidebar'

interface Book {
    title: string
    isbn13?: string
    author: string
    cover: string
    publisher?: string
    year?: string
    loan?: number
}

export default function ResultsPage() {
    const [books, setBooks] = useState<Book[]>([])
    const [loading, setLoading] = useState(true)
    const [collapsed, setCollapsed] = useState(false)
    const [explanation, setExplanation] = useState('')
    const [searchParams] = useSearchParams()
    const keyword = searchParams.get('query') || ''
    const searchQuery = searchParams.get('search_query') || ''
    const navigate = useNavigate()
    const location = useLocation()
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

    const extractBooksFromResponse = (response: string): Book[] => {
        const marker = 'BOOKLIST_JSON:'
        if (!response.includes(marker)) return []

        try {
            const jsonPart = response.split(marker)[1].trim()
            const lines = jsonPart.split('\n')
            return lines.map(line => JSON.parse(line.trim()))
        } catch (error) {
            console.error('Failed to extract books:', error)
            return []
        }
    }

    useEffect(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' })

        const passedBooks = location.state?.books || []
        const responseText = location.state?.responseText || ''

        // Go to results page immediately, don't wait for response
        if (!searchQuery && passedBooks.length > 0) {
            setBooks(passedBooks)
            setExplanation(responseText)
            setLoading(false)
            return
        }

        const fetchBooks = async () => {
            let endpoint = ''
            let payload = {}

            if (searchQuery) {
                endpoint = 'http://127.0.0.1:8000/api/chat/'
                payload = { action: 'chat', message: searchQuery }
            } else if (ageGroup) {
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

            try {
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
                let booksFromResponse = data.books || []

                if (searchQuery && booksFromResponse.length === 0 && data.response?.includes('BOOKLIST_JSON:')) {
                    booksFromResponse = extractBooksFromResponse(data.response)
                }

                setBooks(booksFromResponse)
                setExplanation(data.response || '')
            } catch (err) {
                console.error('Failed to fetch books:', err)
            } finally {
                setLoading(false)
            }
        }

        fetchBooks()
    }, [keyword, searchQuery])

    const mainHeader = explanation?.split('\n')[0] || (searchQuery
        ? `🔎 Search results for: ${searchQuery}`
        : ageGroup
            ? `📖 Books for age group: ${ageGroup}`
            : keyword
                ? `🔍 Books for keyword: ${keyword}`
                : similarTo
                    ? '🔁 Similar books'
                    : advancedFrom
                        ? '📘 Advanced picks'
                        : '📚 Recommended Books')

    return (
        <div className="flex h-screen bg-[#0f0f0f] text-white">
            <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />

            <main className="flex-1 p-8 overflow-y-auto">
                <h1 className="text-2xl font-bold mb-6 text-center">
                    {mainHeader}
                </h1>

                {loading ? (
                    <div className="flex flex-col items-center justify-center h-64 space-y-4">
                        <div className="w-16 h-20 bg-blue-500 rounded-md animate-flipbook"></div>
                        <p className="text-gray-400">Searching for books...</p>
                    </div>
                ) : books.length === 0 ? (
                    <p className="mx-auto px-4 py-3 bg-gray-800 text-gray-300 rounded-xl max-w-fit text-sm shadow-md animate-dropIn">
                        No books found.
                    </p>
                ) : (
                    <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4">
                        {books.map((book, index) => (
                            <div
                                key={book.isbn13 || index}
                                onClick={() => {
                                    if (book.isbn13) {
                                        navigate('/clova-chat', { state: { isbn13: book.isbn13 } })
                                    } else {
                                        alert('ISBN 정보가 없어 클로바 챗으로 이동할 수 없습니다.')
                                    }
                                }}

                                className="bg-[#1a1a1a] p-4 rounded-xl shadow cursor-pointer transition hover:scale-105 hover:shadow-2xl"
                            >
                                <img
                                    src={book.cover || 'https://via.placeholder.com/150'}
                                    alt={book.title}
                                    className="w-full h-64 object-contain rounded bg-[#0f0f0f] mb-2"
                                />
                                <h2 className="font-semibold text-lg mb-1">{book.title}</h2>
                                <p className="text-sm text-gray-400">👤 {book.author}</p>
                                {book.publisher && <p className="text-xs text-gray-500">🏢 {book.publisher} ({book.year})</p>}
                                {book.loan !== undefined && <p className="text-xs text-gray-500">📈 {book.loan}회 대출</p>}
                            </div>
                        ))}
                    </div>
                )}
            </main>
        </div>
    )
}
