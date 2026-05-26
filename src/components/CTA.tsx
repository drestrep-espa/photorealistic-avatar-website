import { useRef, useState } from 'react'
import { ArrowRight, Check, Loader2 } from 'lucide-react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { useGSAP } from '@gsap/react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { supabase } from '@/lib/supabase'

gsap.registerPlugin(ScrollTrigger, useGSAP)

type Status = 'idle' | 'loading' | 'success' | 'error'

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function CTA() {
  const sectionRef = useRef<HTMLElement>(null)
  const [email, setEmail] = useState('')
  const [status, setStatus] = useState<Status>('idle')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  useGSAP(
    () => {
      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top 80%',
        },
      })

      tl.from('[data-cta-content]', {
        scale: 0.85,
        opacity: 0,
        duration: 0.9,
        ease: 'power3.out',
      })
        .fromTo(
          '[data-cta-glow]',
          { opacity: 0, scale: 0.6 },
          { opacity: 1, scale: 1, duration: 1.2, ease: 'power2.out' },
          '<',
        )
        .to(
          '[data-cta-button]',
          {
            scale: 1.06,
            duration: 0.35,
            ease: 'power2.out',
            yoyo: true,
            repeat: 1,
          },
          '-=0.2',
        )
    },
    { scope: sectionRef },
  )

  async function submitEmail() {
    const trimmed = email.trim().toLowerCase()
    if (!trimmed) return

    if (!EMAIL_REGEX.test(trimmed)) {
      setStatus('error')
      setErrorMessage('Ese email no tiene un formato válido. Debe ser como nombre@dominio.com.')
      return
    }

    if (!supabase) {
      setStatus('error')
      setErrorMessage(
        'Formulario no configurado. Falta VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY en .env.local.',
      )
      return
    }

    setStatus('loading')
    setErrorMessage(null)

    const { error } = await supabase.from('waitlist').insert({ email: trimmed })

    if (error) {
      console.error('[waitlist] supabase insert failed', error)
      // 23505 = unique_violation (email ya estaba). Lo tratamos como éxito amable.
      if (error.code === '23505') {
        setStatus('success')
        setEmail('')
        return
      }
      setStatus('error')
      setErrorMessage('No hemos podido enviar tu solicitud. Inténtalo en un momento.')
      return
    }

    setStatus('success')
    setEmail('')
  }

  const isLoading = status === 'loading'
  const isSuccess = status === 'success'

  return (
    <section ref={sectionRef} id="acceso" className="relative">
      <div
        data-cta-glow
        aria-hidden
        className="pointer-events-none absolute left-1/2 top-1/2 -z-10 h-[420px] w-[420px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/15 blur-3xl"
      />
      <div data-cta-content className="mx-auto max-w-3xl px-6 py-20 text-center lg:py-28">
        <h2 className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
          Solicita acceso anticipado.
        </h2>
        <p className="mx-auto mt-4 max-w-xl text-lg text-muted-foreground">
          Entra en la lista de espera y te avisamos en cuanto haya plazas disponibles. Sin
          compromiso, sin tarjeta.
        </p>

        {isSuccess ? (
          <div className="mt-10 inline-flex items-center gap-2 rounded-full bg-primary/10 px-5 py-3 font-medium text-primary">
            <Check className="size-5" />
            ¡Apuntado! Te escribiremos pronto.
          </div>
        ) : (
          <form
            onSubmit={(event) => {
              event.preventDefault()
              void submitEmail()
            }}
            className="mx-auto mt-10 flex max-w-md flex-col gap-3 sm:flex-row"
            noValidate
          >
            <label htmlFor="cta-email" className="sr-only">
              Email
            </label>
            <Input
              id="cta-email"
              type="email"
              name="email"
              required
              autoComplete="email"
              placeholder="tu@email.com"
              value={email}
              onChange={(event) => {
                setEmail(event.target.value)
                if (status === 'error') {
                  setStatus('idle')
                  setErrorMessage(null)
                }
              }}
              disabled={isLoading}
              className="h-11 flex-1 text-base"
            />
            <Button data-cta-button type="submit" size="lg" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="animate-spin" />
                  Enviando…
                </>
              ) : (
                <>
                  Solicitar acceso
                  <ArrowRight />
                </>
              )}
            </Button>
          </form>
        )}

        {status === 'error' && errorMessage && (
          <p className="mt-4 text-sm text-red-600" role="alert">
            {errorMessage}
          </p>
        )}
      </div>
    </section>
  )
}

export default CTA
