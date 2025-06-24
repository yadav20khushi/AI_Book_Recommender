// src/hooks/useNavigationDirection.ts
import { useEffect, useRef, useState } from 'react'
import { useLocation } from 'react-router-dom'

export default function useNavigationDirection() {
    const location = useLocation()
    const [direction, setDirection] = useState(1)
    const prevPathStack = useRef<string[]>([])

    useEffect(() => {
        const pathname = location.pathname
        const stack = prevPathStack.current
        const prev = stack[stack.length - 1]

        if (!prev) {
            stack.push(pathname)
            return
        }

        if (pathname === prev) {
            return
        }

        const prevIndex = stack.indexOf(pathname)
        if (prevIndex === -1) {
            // Forward navigation
            setDirection(1)
            stack.push(pathname)
        } else {
            // Backward navigation
            setDirection(-1)
            stack.splice(prevIndex + 1)
        }
    }, [location.pathname])

    return direction
}
