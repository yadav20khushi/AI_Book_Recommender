import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'

export default function SignupPage() {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const navigate = useNavigate()

    function getCookie(name: string): string | undefined {
        const match = document.cookie
            .split('; ')
            .find(row => row.startsWith(name + '='));
        return match ? decodeURIComponent(match.split('=')[1]) : undefined;
    }

    const csrfToken = getCookie('csrftoken');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')

        try {
            const res = await fetch('http://127.0.0.1:8000/api/signup/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken ?? '',
                },
                body: new URLSearchParams({ username, password }),
                credentials: 'include',
            })

            if (res.ok) {
                navigate('/home')
            } else {
                const data = await res.json()
                setError(data.error || 'Signup failed')
            }
        } catch (err) {
            setError('Server error. Please try again.')
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-[#0f0f0f] px-4">
            <div className="w-full max-w-md bg-[#1a1a1a] p-8 rounded-2xl shadow-lg border border-gray-700">
                <h2 className="text-2xl font-semibold text-center mb-6 text-white">Sign Up</h2>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <input
                        type="text"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        className="w-full px-4 py-3 rounded-md bg-[#111] text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />

                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full px-4 py-3 rounded-md bg-[#111] text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />

                    <button
                        type="submit"
                        className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-md transition"
                    >
                        Create Account
                    </button>
                </form>

                {error && <p className="text-red-400 text-sm mt-3 text-center">{error}</p>}

                <p className="text-center text-sm text-gray-400 mt-6">
                    Already have an account?{' '}
                    <Link to="/login" className="text-blue-400 hover:underline">
                        Login
                    </Link>
                </p>
            </div>
        </div>
    )
}
