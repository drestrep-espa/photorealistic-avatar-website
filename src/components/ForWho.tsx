import { Briefcase, GraduationCap, Users, type LucideIcon } from 'lucide-react'

type Profile = {
  role: string
  headline: string
  description: string
  Icon: LucideIcon
}

const profiles: Profile[] = [
  {
    role: 'Recién titulados',
    headline: 'Tus primeras horas de práctica, sin pacientes reales delante.',
    description:
      'Coge soltura en consulta, prueba intervenciones y pierde el miedo a equivocarte en un entorno donde nadie se ve afectado.',
    Icon: GraduationCap,
  },
  {
    role: 'Psicólogos en activo',
    headline: 'Practica casos que apenas ves en tu día a día.',
    description:
      'Entrena perfiles concretos —duelo, trauma, adicciones, crisis— y prueba nuevas técnicas antes de aplicarlas con pacientes reales.',
    Icon: Briefcase,
  },
  {
    role: 'Docentes y supervisores',
    headline: 'Prepara a tus alumnos con casos controlados.',
    description:
      'Diseña escenarios concretos para que practiquen una y otra vez, con la conducta exacta que quieres trabajar en cada sesión.',
    Icon: Users,
  },
]

function ForWho() {
  return (
    <section id="para-quien" className="border-t border-border/60 bg-accent/30">
      <div className="mx-auto max-w-4xl px-6 py-20 lg:py-28">
        <div className="max-w-2xl">
          <span className="text-sm font-medium uppercase tracking-wider text-primary">
            Para quién es
          </span>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
            Pensado para psicólogos que quieren seguir practicando.
          </h2>
        </div>

        <ul className="mt-14 divide-y divide-border/60">
          {profiles.map((profile) => (
            <ProfileRow key={profile.role} profile={profile} />
          ))}
        </ul>
      </div>
    </section>
  )
}

function ProfileRow({ profile }: { profile: Profile }) {
  const { role, headline, description, Icon } = profile
  return (
    <li className="flex flex-col gap-6 py-10 sm:flex-row sm:gap-10">
      <div className="shrink-0">
        <div className="grid size-16 place-items-center rounded-2xl bg-background text-primary shadow-sm ring-1 ring-border/60">
          <Icon className="size-7" />
        </div>
      </div>

      <div className="flex-1">
        <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
          {role}
        </p>
        <h3 className="mt-1 text-xl font-semibold leading-snug tracking-tight text-foreground sm:text-2xl">
          {headline}
        </h3>
        <p className="mt-3 max-w-2xl text-muted-foreground">{description}</p>
      </div>
    </li>
  )
}

export default ForWho
