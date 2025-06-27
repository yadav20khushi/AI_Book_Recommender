import React, { useState } from 'react';
import axios from 'axios';

interface Book {
    title: string;
    author: string;
    publisher: string;
    year: string;
    loan: number;
    cover: string;
}

const SearchBar: React.FC = () => {
    const [query, setQuery] = useState('');
    const [response, setResponse] = useState('');
    const [books, setBooks] = useState<Book[]>([]);
    const [loading, setLoading] = useState(false);

    const extractBookList = (text: string): Book[] => {
        if (!text.includes('BOOKLIST_JSON:')) return [];
        try {
            const jsonPart = text.split('BOOKLIST_JSON:')[1].trim();
            const jsonLines = jsonPart.split('\n');
            return jsonLines.map(line => JSON.parse(line.trim()));
        } catch (err) {
            console.error('Failed to parse BOOKLIST_JSON:', err);
            return [];
        }
    };

    const handleSearch = async () => {
        setLoading(true);
        setBooks([]);
        setResponse('');

        try {
            // STEP 1: Call chat (first-level smart processing)
            const res = await axios.post('http://127.0.0.1:8000/api/chat/', {
                action: 'chat',
                message: query,
            });

            if (res.data.success) {
                const chatResponse = res.data.response;
                const parsedBooks = extractBookList(chatResponse);

                if (parsedBooks.length > 0) {
                    setBooks(parsedBooks);
                    setResponse(chatResponse);
                } else {
                    // STEP 2: Fallback to search_books (broader results)
                    const fallback = await axios.post('http://127.0.0.1:8000/api/chat/', {
                        action: 'search_books',
                        query: query,
                    });

                    if (fallback.data.success) {
                        setBooks(fallback.data.books || []);
                        setResponse(fallback.data.response || '결과 없음');
                    } else {
                        setResponse('🔴 검색 실패: ' + fallback.data.error);
                    }
                }
            } else {
                setResponse('🔴 채팅 처리 실패: ' + res.data.error);
            }
        } catch (err) {
            console.error(err);
            setResponse('서버 오류가 발생했습니다.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-4 max-w-xl mx-auto">
            <div className="flex items-center gap-2">
                <input
                    className="border px-3 py-2 flex-1"
                    placeholder="예: 스티븐 킹 책, 서울 역사책, 철학 관련"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                />
                <button
                    onClick={handleSearch}
                    disabled={loading}
                    className="bg-blue-600 text-white px-4 py-2 rounded"
                >
                    {loading ? '검색 중...' : '검색'}
                </button>
            </div>

            {response && (
                <div className="mt-4 whitespace-pre-wrap bg-gray-100 p-3 rounded">
                    {response}
                </div>
            )}

            {books.length > 0 && (
                <div className="mt-4">
                    <h2 className="font-bold mb-2">📚 검색된 도서</h2>
                    <ul className="space-y-2">
                        {books.map((book, index) => (
                            <li key={index} className="border p-3 rounded shadow-sm">
                                <div className="font-semibold">{book.title}</div>
                                <div>👤 {book.author}</div>
                                <div>🏢 {book.publisher} ({book.year})</div>
                                <div>📈 대출: {book.loan}회</div>
                                {book.cover && <img src={book.cover} alt="cover" className="mt-2 w-24" />}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

export default SearchBar;
