import { useEffect, useRef } from 'react'
import { Outlet, useLocation } from 'react-router'

import Footer from '@/components/Footer'
import Navbar from '@/components/Navbar'

if (typeof window !== 'undefined' && 'scrollRestoration' in window.history) {
  window.history.scrollRestoration = 'manual'
}

function Layout() {
  const { pathname, hash } = useLocation()
  const isFirstMount = useRef(true)

  useEffect(() => {
    if (isFirstMount.current) {
      isFirstMount.current = false
      if (hash) {
        window.history.replaceState(null, '', pathname)
      }
      window.scrollTo({ top: 0, behavior: 'instant' })
      return
    }

    if (hash) {
      const element = document.querySelector(hash)
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' })
        return
      }
    }
    window.scrollTo({ top: 0, behavior: 'instant' })
  }, [pathname, hash])

  return (
    <>
      <Navbar />
      <main>
        <Outlet />
      </main>
      <Footer />
    </>
  )
}

export default Layout
