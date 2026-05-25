import { useState, type FormEvent } from 'react'
import { ArrowRight, Check } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

function CTA() {
  const [email, setEmail] = useState('')
  const [submitted, setSubmitted] = useState(false)

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!email) return
    // TODO: conectar con backend / servicio de email
    setSubmitted(true)
  }

  return (
    <section id="acceso" className="relative overflow-hidden border-t border-border/60">
      <div
        aria-hidden
        className="absolute inset-0 -z-10 bg-gradient-to-b from-background via-accent/30 to-background"
      />
      <div
        aria-hidden
        className="absolute -right-32 top-1/2 -z-10 h-[480px] w-[480px] -translate-y-1/2 rounded-full bg-primary/10 blur-3xl"
      />

      <div className="mx-auto max-w-3xl px-6 py-20 text-center lg:py-28">
        <h2 className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
          Solicita acceso anticipado.
        </h2>
        <p className="mx-auto mt-4 max-w-xl text-lg text-muted-foreground">
          Entra en la lista de espera y te avisamos en cuanto haya plazas disponibles. Sin
          compromiso, sin tarjeta.
        </p>

        {submitted ? (
          <div className="mt-10 inline-flex items-center gap-2 rounded-full bg-primary/10 px-5 py-3 font-medium text-primary">
            <Check className="size-5" />
            ¡Apuntado! Te escribiremos pronto.
          </div>
        ) : (
          <form
            onSubmit={handleSubmit}
            className="mx-auto mt-10 flex max-w-md flex-col gap-3 sm:flex-row"
          >
            <label htmlFor="cta-email" className="sr-only">
              Email
            </label>
            <Input
              id="cta-email"
              type="email"
              required
              placeholder="tu@email.com"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="h-11 flex-1 text-base"
            />
            <Button type="submit" size="lg">
              Solicitar acceso
              <ArrowRight />
            </Button>
          </form>
        )}
      </div>
    </section>
  )
}

export default CTA
