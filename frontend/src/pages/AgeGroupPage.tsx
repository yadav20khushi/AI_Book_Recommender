import React from 'react'
import { useNavigate } from 'react-router-dom'
import Sidebar from '../components/Sidebar'

const AGE_GROUPS = [
    { label: '👶 Infant', value: 'infant' },
    { label: '🧒 Toddler', value: 'toddler' },
    { label: '📚 Elementary', value: 'elementary' },
    { label: '🎒 Teen', value: 'teen' },
    { label: '🧑 Adult', value: 'adult' },
]

const tileClass =
    'w-52 h-32 flex items-center justify-center text-center px-4 py-4 rounded-2xl bg-[#1a1a1a] border border-gray-600 text-base font-medium text-gray-200 shadow-sm hover:shadow-lg hover:bg-[#2a2a2a] hover:border-gray-400 transition-transform duration-200 hover:-translate-y-1 cursor-pointer'


export default function AgeGroupPage() {
    const [collapsed, setCollapsed] = React.useState(false)
    const navigate = useNavigate()

    const handleAgeClick = (group: string) => {
        navigate(`/result?age_group=${group}`)
    }

    return (
        <div className="flex min-h-screen bg-[#0f0f0f] text-white">
            <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />

            <main className="flex-1 flex flex-col items-center justify-center p-6">
                <h1 className="text-4xl font-bold text-center mb-12 tracking-tight">
                    📚 연령대에 맞는 책을 선택해보세요!
                </h1>

                <div className="grid grid-cols-3 gap-6">
                    {/* Row 1: Three tiles */}
                    <button onClick={() => handleAgeClick('infant')} className={tileClass}>
                        👶 Infant
                    </button>
                    <button onClick={() => handleAgeClick('toddler')} className={tileClass}>
                        🧒 Toddler
                    </button>
                    <button onClick={() => handleAgeClick('elementary')} className={tileClass}>
                        📚 Elementary
                    </button>

                    {/* Row 2: Two centered tiles (with 1 blank cell at start) */}
                    <button onClick={() => handleAgeClick('teen')} className={tileClass}>
                        🎒 Teen
                    </button>
                    <div></div>
                    <button onClick={() => handleAgeClick('adult')} className={tileClass}>
                        🧑 Adult
                    </button>
                </div>

            </main>
        </div>
    )
}
