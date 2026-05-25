import type { ReactNode } from 'react'
import { ArrowLeft } from 'lucide-react'
import { Link } from 'react-router'

type LegalPageProps = {
  title: string
  lastUpdated: string
  children: ReactNode
}

function LegalPage({ title, lastUpdated, children }: LegalPageProps) {
  return (
    <article className="mx-auto max-w-3xl px-6 py-16 lg:py-24">
      <header>
        <Link
          to="/"
          className="inline-flex items-center gap-1 text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          <ArrowLeft className="size-4" />
          Volver al inicio
        </Link>
        <h1 className="mt-6 text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
          {title}
        </h1>
        <p className="mt-3 text-sm text-muted-foreground">
          Última actualización: {lastUpdated}
        </p>
      </header>

      <div className="mt-12 space-y-10 text-muted-foreground leading-relaxed [&_h2]:mb-3 [&_h2]:text-lg [&_h2]:font-semibold [&_h2]:tracking-tight [&_h2]:text-foreground [&_p+p]:mt-3 [&_ul]:mt-3 [&_ul]:list-disc [&_ul]:space-y-2 [&_ul]:pl-6 [&_a]:text-primary [&_a]:underline-offset-4 hover:[&_a]:underline">
        {children}
      </div>
    </article>
  )
}

export default LegalPage
