import { useRef } from 'react'
import { ArrowRight, Mic, MicOff, PhoneOff, User, Video } from 'lucide-react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { useGSAP } from '@gsap/react'

import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'

gsap.registerPlugin(ScrollTrigger, useGSAP)

function Hero() {
  const sectionRef = useRef<HTMLElement>(null)

  useGSAP(
    () => {
      const tl = gsap.timeline({ defaults: { ease: 'power3.out' } })
      tl.from('[data-hero-reveal]', {
        y: 40,
        opacity: 0,
        duration: 0.9,
        stagger: 0.12,
      }).from(
        '[data-hero-card]',
        { y: 60, opacity: 0, duration: 1, ease: 'power3.out' },
        '-=0.6',
      )

      gsap.to('[data-hero-card]', {
        yPercent: -12,
        ease: 'none',
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top top',
          end: 'bottom top',
          scrub: true,
        },
      })
    },
    { scope: sectionRef },
  )

  return (
    <section ref={sectionRef} className="relative overflow-hidden">
      <div
        aria-hidden
        className="absolute inset-0 -z-10 bg-gradient-to-b from-accent/40 via-background to-background"
      />
      <div
        aria-hidden
        className="absolute -left-32 -top-32 -z-10 h-[480px] w-[480px] rounded-full bg-primary/10 blur-3xl"
      />

      <div className="mx-auto grid max-w-6xl items-center gap-12 px-6 pb-24 pt-20 lg:grid-cols-2 lg:gap-16 lg:pb-32 lg:pt-28">
        <div className="text-center lg:text-left">
          <span
            data-hero-reveal
            className="inline-flex items-center gap-2 rounded-full bg-accent px-3 py-1 text-xs font-medium text-accent-foreground"
          >
            <span className="h-1.5 w-1.5 rounded-full bg-primary" />
            Videollamadas en tiempo real · Para psicólogos
          </span>

          <h1
            data-hero-reveal
            className="mt-6 text-4xl font-semibold leading-[1.05] tracking-tight text-foreground sm:text-5xl lg:text-6xl"
          >
            Videollamadas con pacientes{' '}
            <span className="text-primary">que parecen reales.</span>
          </h1>

          <p
            data-hero-reveal
            className="mx-auto mt-6 max-w-xl text-lg text-muted-foreground lg:mx-0"
          >
            Habla cara a cara con avatares fotorrealistas que reaccionan en tiempo real. Entrena
            tu escucha, tu técnica y tu criterio en sesiones tan creíbles como las del consultorio
            —todas las veces que necesites.
          </p>

          <div
            data-hero-reveal
            className="mt-8 flex flex-col justify-center gap-3 sm:flex-row lg:justify-start"
          >
            <Button asChild size="lg">
              <a href="#acceso">
                Solicitar acceso
                <ArrowRight />
              </a>
            </Button>
            <Button asChild size="lg" variant="outline">
              <a href="#como-funciona">Ver cómo funciona</a>
            </Button>
          </div>

          <p data-hero-reveal className="mt-4 text-sm text-muted-foreground">
            Acceso anticipado gratuito · Sin tarjeta de crédito
          </p>
        </div>

        <HeroVideoCall />
      </div>
    </section>
  )
}

function HeroVideoCall() {
  return (
    <div data-hero-card className="relative mx-auto aspect-[4/5] w-full max-w-md">
      <Card className="relative h-full w-full overflow-hidden rounded-3xl border-border/60 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-0 shadow-2xl">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_50%_30%,rgba(255,255,255,0.08),transparent_60%)]"
        />

        <div className="absolute left-4 top-4 flex items-center gap-2 rounded-full bg-black/40 px-3 py-1 text-xs font-medium text-white backdrop-blur">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-red-500 opacity-75" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-red-500" />
          </span>
          EN VIVO
        </div>

        <div className="absolute right-4 top-4 rounded-full bg-black/40 px-3 py-1 font-mono text-xs text-white backdrop-blur">
          12:34
        </div>

        <div className="grid h-full w-full place-items-center text-white/30">
          <User className="size-40" strokeWidth={1} />
        </div>

        <div className="absolute bottom-24 right-4 h-24 w-20 overflow-hidden rounded-xl border border-white/10 bg-slate-700 shadow-lg">
          <div className="grid h-full w-full place-items-center text-white/40">
            <User className="size-10" strokeWidth={1.5} />
          </div>
          <span className="absolute bottom-1 left-1 rounded bg-black/60 px-1 py-px text-[10px] font-medium text-white">
            Tú
          </span>
        </div>

        <div className="absolute bottom-6 left-1/2 flex -translate-x-1/2 items-center gap-2 rounded-full bg-black/50 px-3 py-2 backdrop-blur">
          <CallControl Icon={Mic} />
          <CallControl Icon={Video} />
          <CallControl Icon={MicOff} muted />
          <CallControl Icon={PhoneOff} danger />
        </div>

        <div className="absolute bottom-20 left-4 rounded-md bg-black/50 px-2 py-1 text-[11px] font-medium text-white backdrop-blur">
          Marta · Paciente
        </div>
      </Card>
    </div>
  )
}

type CallControlProps = {
  Icon: typeof Mic
  muted?: boolean
  danger?: boolean
}

function CallControl({ Icon, muted, danger }: CallControlProps) {
  const base = 'grid size-9 place-items-center rounded-full transition-colors'
  const variant = danger
    ? 'bg-red-500 text-white hover:bg-red-600'
    : muted
      ? 'bg-white/10 text-white/60'
      : 'bg-white/15 text-white hover:bg-white/25'
  return (
    <span className={`${base} ${variant}`} aria-hidden>
      <Icon className="size-4" />
    </span>
  )
}

export default Hero
