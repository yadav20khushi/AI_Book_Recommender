import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import { toast } from 'react-hot-toast'

interface Book {
    title: string
    isbn13: string
    author: string
    cover: string
}

export default function ReturningUserPage() {
    const [books, setBooks] = useState<Book[]>([])
    const [username, setUsername] = useState('')
    const [loading, setLoading] = useState(true)
    const navigate = useNavigate()

    // ✅ 1. Check auth before fetching anything
    useEffect(() => {
        const verify = async () => {
            try {
                const res = await fetch('api/check-auth/', {
                    credentials: 'include',
                })
                const data = await res.json()
                if (!data.authenticated) {
                    toast.error("Please log in first.")
                    navigate('api/login')
                }
            } catch (err) {
                console.error("❌ Auth check failed:", err)
                toast.error("Unable to verify session.")
                navigate('api/login')
            }
        }

        verify()
    }, [navigate])

    // ✅ 2. Now fetch book recommendations
    useEffect(() => {
        const fetchRecommendations = async () => {
            try {
                const res = await fetch('api/returning/', {
                    method: 'GET',
                    credentials: 'include',
                })

                if (res.status === 401) {
                    return // already redirected above
                }

                const data = await res.json()
                setBooks(data.books)
                setUsername(data.username)
            } catch (err) {
                console.error("❌ Failed to fetch returning user books:", err)
                toast.error("Failed to load recommendations.")
            } finally {
                setLoading(false)
            }
        }

        fetchRecommendations()
    }, [])

    const handleBookClick = (isbn13: string) => {
        navigate('/clova-chat', { state: { isbn13 } })
    }

    return (
        <div className="flex h-screen bg-[#0f0f0f] text-white">
            <Sidebar collapsed={false} onToggle={() => { }} />

            <div className="flex-1 p-6 overflow-y-auto">
                <h1 className="text-2xl font-bold mb-6">
                    {username} 님의 이전 추천 기록
                </h1>

                {loading ? (
                    <p className="text-gray-400">Loading recommendations...</p>
                ) : books.length === 0 ? (
                    <p className="text-gray-400">추천 기록이 없습니다.</p>
                ) : (
                    <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4">
                        {books.map((book) => (
                            <div
                                key={book.isbn13}
                                className="bg-[#1a1a1a] p-4 rounded-xl shadow cursor-pointer transition hover:scale-105 hover:shadow-2xl"
                                onClick={() => handleBookClick(book.isbn13)}
                            >
                                <img
                                    src={book.cover}
                                    alt={book.title}
                                    className="w-full h-64 object-contain rounded bg-[#0f0f0f] mb-2"
                                />
                                <h3 className="text-lg font-semibold mb-1 truncate">
                                    {book.title}
                                </h3>
                                <p className="text-sm text-gray-400 truncate">{book.author}</p>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}
