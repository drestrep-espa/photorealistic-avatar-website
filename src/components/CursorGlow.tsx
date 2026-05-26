import { useEffect, useRef } from 'react'

function CursorGlow() {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const element = ref.current
    if (!element) return

    let frame = 0
    function handleMove(event: MouseEvent) {
      cancelAnimationFrame(frame)
      const x = event.clientX
      const y = event.clientY
      frame = requestAnimationFrame(() => {
        if (!element) return
        element.style.background = `radial-gradient(600px circle at ${x}px ${y}px, rgba(21, 131, 230, 0.14), transparent 60%)`
      })
    }

    window.addEventListener('mousemove', handleMove)
    return () => {
      window.removeEventListener('mousemove', handleMove)
      cancelAnimationFrame(frame)
    }
  }, [])

  return <div ref={ref} aria-hidden className="pointer-events-none fixed inset-0 z-50" />
}

export default CursorGlow
