import { ShieldCheck, Search, Library, MoreHorizontal, LogOut } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { toast } from 'react-hot-toast'

export default function Sidebar({
    collapsed,
    onToggle,
}: {
    collapsed: boolean
    onToggle: () => void
}) {
    const navigate = useNavigate()
    const [signingOut, setSigningOut] = useState(false)

    const handleSignout = async () => {
        setSigningOut(true)
        try {
            const res = await fetch('http://127.0.0.1:8000/api/logout/', {
                method: 'POST',
                credentials: 'include',
            })
            if (res.ok) {
                toast.success('Signed out successfully')
                navigate('/login')
            } else {
                toast.error('Failed to sign out')
            }
        } catch (err) {
            toast.error('Error during sign out')
            console.error('❌ Signout error:', err)
        } finally {
            setSigningOut(false)
        }
    }

    return (
        <div
            className={`h-screen ${collapsed ? 'w-[60px]' : 'w-[260px]'} transition-all duration-300 bg-[#111] border-r border-[#2d2d2d] flex flex-col justify-between`}
        >
            {/* Header */}
            <div>
                <div className="flex items-center justify-between px-4 py-3 border-b border-[#2d2d2d]">
                    <button className="p-1 rounded hover:bg-[#2d2d2d]">
                        <ShieldCheck className="w-6 h-6" />
                    </button>
                    <button onClick={onToggle} className="p-1 rounded hover:bg-[#2d2d2d]">
                        ✕
                    </button>
                </div>

                {/* Menu */}
                <div className="mt-4 px-2 space-y-1">
                    <Link
                        to="/home"
                        className="flex items-center w-full gap-3 text-sm px-3 py-2 rounded hover:bg-[#2d2d2d]"
                    >
                        <ShieldCheck className="w-5 h-5" />
                        {!collapsed && <span>New chat</span>}
                    </Link>

                    <button className="flex items-center w-full gap-3 text-sm px-3 py-2 rounded hover:bg-[#2d2d2d]">
                        <Search className="w-5 h-5" />
                        {!collapsed && <span>Search chats</span>}
                    </button>
                    <button className="flex items-center w-full gap-3 text-sm px-3 py-2 rounded hover:bg-[#2d2d2d]">
                        <Library className="w-5 h-5" />
                        {!collapsed && <span>Library</span>}
                    </button>

                    {!collapsed && (
                        <div className="mt-4 text-xs text-gray-400 uppercase px-3">Chats</div>
                    )}

                    <div className="flex items-center justify-between text-sm px-3 py-2 rounded hover:bg-[#2d2d2d] mt-1">
                        {!collapsed && <span>previous book chat history</span>}
                        {!collapsed && (
                            <button className="text-gray-400 hover:text-white">
                                <MoreHorizontal className="w-4 h-4" />
                            </button>
                        )}
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div className="p-3 border-t border-[#2d2d2d] flex flex-col gap-2">
                {/* <div className="flex items-center gap-3">
                    <img
                        src="https://lh3.googleusercontent.com/a/AGNmyxb_YDklUhiX-1WgE0ahz33qIobkhx2DbyXaMFXSoQ=s96-c"
                        alt="avatar"
                        className="w-7 h-7 rounded-full border border-[#2d2d2d]"
                    />
                    {!collapsed && <span className="text-sm">Khushi Yadav</span>}
                </div> */}

                <button
                    onClick={handleSignout}
                    disabled={signingOut}
                    className={`flex items-center gap-2 text-sm text-red-400 hover:text-red-300 mt-2 px-3 py-2 rounded hover:bg-[#2d2d2d] transition ${signingOut ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                    <LogOut className="w-4 h-4" />
                    {!collapsed && <span>{signingOut ? 'Signing out...' : 'Sign Out'}</span>}
                </button>
            </div>
        </div>
    )
}
