import { Route, Routes } from 'react-router'

import Layout from '@/components/Layout'
import CookiePolicy from '@/pages/CookiePolicy'
import Landing from '@/pages/Landing'
import LegalNotice from '@/pages/LegalNotice'
import PrivacyPolicy from '@/pages/PrivacyPolicy'

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Landing />} />
        <Route path="/aviso-legal" element={<LegalNotice />} />
        <Route path="/politica-privacidad" element={<PrivacyPolicy />} />
        <Route path="/politica-cookies" element={<CookiePolicy />} />
      </Route>
    </Routes>
  )
}

export default App
