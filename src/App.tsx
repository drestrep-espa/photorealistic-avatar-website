import CTA from '@/components/CTA'
import Footer from '@/components/Footer'
import ForWho from '@/components/ForWho'
import Hero from '@/components/Hero'
import HowItWorks from '@/components/HowItWorks'
import Navbar from '@/components/Navbar'

function App() {
  return (
    <>
      <Navbar />
      <main>
        <Hero />
        <HowItWorks />
        <ForWho />
        <CTA />
      </main>
      <Footer />
    </>
  )
}

export default App
