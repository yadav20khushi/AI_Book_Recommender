// ClovaChatContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react'
import type { ReactNode } from 'react'


type Message = {
    role: 'user' | 'assistant'
    content: string
}

type ClovaChatContextType = {
    isbn13: string | null
    chatStarted: boolean
    clovaMessages: Message[]
    bookInfo: any
    setIsbn13: (isbn: string | null) => void
    setChatStarted: (val: boolean) => void
    setClovaMessages: React.Dispatch<React.SetStateAction<Message[]>>
    setBookInfo: (info: any) => void
}

const ClovaChatContext = createContext<ClovaChatContextType | undefined>(undefined)

export const ClovaChatProvider = ({ children }: { children: ReactNode }) => {
    const [isbn13, setIsbn13] = useState<string | null>(null)
    const [chatStarted, setChatStarted] = useState(false)
    const [clovaMessages, setClovaMessages] = useState<Message[]>([])
    const [bookInfo, setBookInfo] = useState<any>(null)

    // Load from sessionStorage on mount
    useEffect(() => {
        const saved = sessionStorage.getItem('clovaChat')
        if (saved) {
            const parsed = JSON.parse(saved)
            setIsbn13(parsed.isbn13)
            setChatStarted(parsed.chatStarted)
            setClovaMessages(parsed.clovaMessages || [])
            setBookInfo(parsed.bookInfo || null)
        }
    }, [])

    // Save to sessionStorage whenever it changes
    useEffect(() => {
        if (isbn13) {
            sessionStorage.setItem(
                'clovaChat',
                JSON.stringify({ isbn13, chatStarted, clovaMessages, bookInfo })
            )
        }
    }, [isbn13, chatStarted, clovaMessages, bookInfo])

    return (
        <ClovaChatContext.Provider
            value={{ isbn13, setIsbn13, chatStarted, setChatStarted, clovaMessages, setClovaMessages, bookInfo, setBookInfo }}
        >
            {children}
        </ClovaChatContext.Provider>
    )
}

export const useClovaChat = () => {
    const ctx = useContext(ClovaChatContext)
    if (!ctx) throw new Error('useClovaChat must be used within ClovaChatProvider')
    return ctx
}
