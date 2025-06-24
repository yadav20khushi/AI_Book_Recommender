// src/components/PageWrapper.tsx
import { motion } from 'framer-motion'
import type { Variants, Transition } from 'framer-motion'
import { useLocation } from 'react-router-dom'


interface SlideVariants {
    direction: number
}

const slideVariants: Variants = {
    initial: (custom: SlideVariants) => ({
        x: custom.direction > 0 ? '100%' : '-100%',
        opacity: 0,
    }),
    animate: {
        x: 0,
        opacity: 1,
        transition: { duration: 0.4, ease: 'easeOut' } as Transition,
    },
    exit: (custom: SlideVariants) => ({
        x: custom.direction < 0 ? '100%' : '-100%',
        opacity: 0,
        transition: { duration: 0.4, ease: 'easeIn' } as Transition,
    }),
}



export default function PageWrapper({ children, direction = 1 }: { children: React.ReactNode; direction?: number }) {
    const location = useLocation()

    return (
        <motion.div
            key={location.pathname}
            variants={slideVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            custom={direction}
            className="w-full h-full"
        >
            {children}
        </motion.div>
    )
}
