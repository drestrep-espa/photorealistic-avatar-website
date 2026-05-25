import { Mail } from 'lucide-react'
import { Link } from 'react-router'

const productLinks = [
  { href: '/#como-funciona', label: 'Cómo funciona' },
  { href: '/#para-quien', label: 'Para quién' },
  { href: '/#acceso', label: 'Solicitar acceso' },
]

const legalLinks = [
  { to: '/aviso-legal', label: 'Aviso legal' },
  { to: '/politica-privacidad', label: 'Política de privacidad' },
  { to: '/politica-cookies', label: 'Política de cookies' },
]

const EMAIL = 'endrokosverde@gmail.com'
const LINKEDIN_URL = 'https://www.linkedin.com/in/daniel-restrepo-de-juan/'

function Footer() {
  const year = new Date().getFullYear()

  return (
    <footer className="border-t border-border/60 bg-background">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <Link to="/" className="flex items-center gap-2">
              <span className="grid size-8 place-items-center rounded-lg bg-primary font-semibold text-primary-foreground">
                P
              </span>
              <span className="font-semibold tracking-tight text-foreground">Psyko</span>
            </Link>
            <p className="mt-4 max-w-xs text-sm text-muted-foreground">
              Videollamadas con pacientes simulados para psicólogos en formación y práctica
              clínica.
            </p>
          </div>

          <div>
            <h3 className="text-sm font-semibold tracking-tight text-foreground">Producto</h3>
            <ul className="mt-4 space-y-3">
              {productLinks.map((link) => (
                <li key={link.href}>
                  <a
                    href={link.href}
                    className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-sm font-semibold tracking-tight text-foreground">Legal</h3>
            <ul className="mt-4 space-y-3">
              {legalLinks.map((link) => (
                <li key={link.to}>
                  <Link
                    to={link.to}
                    className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-sm font-semibold tracking-tight text-foreground">Contacto</h3>
            <ul className="mt-4 space-y-3">
              <li>
                <a
                  href={`mailto:${EMAIL}`}
                  className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
                >
                  <Mail className="size-4" />
                  {EMAIL}
                </a>
              </li>
              <li>
                <a
                  href={LINKEDIN_URL}
                  target="_blank"
                  rel="noreferrer"
                  aria-label="LinkedIn"
                  className="inline-flex size-9 items-center justify-center rounded-full bg-accent text-accent-foreground transition-colors hover:bg-primary hover:text-primary-foreground"
                >
                  <LinkedInIcon />
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 flex flex-col items-center justify-between gap-3 border-t border-border/60 pt-6 sm:flex-row">
          <p className="text-sm text-muted-foreground">
            © {year} Psyko. Todos los derechos reservados.
          </p>
          <p className="text-xs text-muted-foreground">Hecho en España</p>
        </div>
      </div>
    </footer>
  )
}

function LinkedInIcon() {
  return (
    <svg className="size-4" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
      <path d="M20.5 2h-17A1.5 1.5 0 0 0 2 3.5v17A1.5 1.5 0 0 0 3.5 22h17a1.5 1.5 0 0 0 1.5-1.5v-17A1.5 1.5 0 0 0 20.5 2zM8 19H5v-9h3v9zM6.5 8.25A1.75 1.75 0 1 1 8.3 6.5a1.78 1.78 0 0 1-1.8 1.75zM19 19h-3v-4.74c0-1.42-.6-1.93-1.38-1.93A1.74 1.74 0 0 0 13 14.19a.66.66 0 0 0 0 .14V19h-3v-9h2.9v1.3a3.11 3.11 0 0 1 2.7-1.4c1.55 0 3.36.86 3.36 3.66V19z" />
    </svg>
  )
}

export default Footer
