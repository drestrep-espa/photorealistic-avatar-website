import { FileText, RefreshCw, Video, type LucideIcon } from 'lucide-react'

import { Card } from '@/components/ui/card'

type Step = {
  number: string
  title: string
  description: string
  Icon: LucideIcon
}

const steps: Step[] = [
  {
    number: '01',
    title: 'Elige o crea el caso',
    description:
      'Parte de un catálogo de casos clínicos o sube tu propio informe para replicar un caso real. Ajusta el comportamiento del paciente: ritmo, apertura, reactividad y más.',
    Icon: FileText,
  },
  {
    number: '02',
    title: 'Entra en la videollamada',
    description:
      'El avatar se prepara para tu sesión. Cuando entra en la llamada, hablas con él como con cualquier persona en pantalla: escucha, responde y reacciona en tiempo real.',
    Icon: Video,
  },
  {
    number: '03',
    title: 'Practica sin límite',
    description:
      'Repite la sesión las veces que necesites, prueba enfoques distintos, vuelve a empezar. Sin pacientes reales, sin riesgo, a tu ritmo.',
    Icon: RefreshCw,
  },
]

function HowItWorks() {
  return (
    <section id="como-funciona" className="border-t border-border/60 bg-background">
      <div className="mx-auto max-w-6xl px-6 py-20 lg:py-28">
        <div className="mx-auto max-w-2xl text-center">
          <span className="text-sm font-medium uppercase tracking-wider text-primary">
            Cómo funciona
          </span>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
            Configura el caso, entra en la videollamada, practica las veces que haga falta.
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Casos clínicos predefinidos o creados desde tus propios informes. Tú decides cómo se
            comporta el paciente.
          </p>
        </div>

        <ol className="mt-16 grid gap-6 md:grid-cols-3">
          {steps.map((step) => (
            <StepCard key={step.number} step={step} />
          ))}
        </ol>
      </div>
    </section>
  )
}

function StepCard({ step }: { step: Step }) {
  const { number, title, description, Icon } = step
  return (
    <li className="list-none">
      <Card className="relative h-full overflow-hidden border-border/60 p-8 transition-colors hover:border-primary/40">
        <div className="flex items-start justify-between">
          <div className="grid size-12 place-items-center rounded-xl bg-primary/10 text-primary">
            <Icon className="size-6" />
          </div>
          <span className="font-mono text-sm font-medium text-muted-foreground/60">
            {number}
          </span>
        </div>
        <h3 className="mt-6 text-xl font-semibold tracking-tight text-foreground">{title}</h3>
        <p className="mt-3 text-muted-foreground">{description}</p>
      </Card>
    </li>
  )
}

export default HowItWorks
