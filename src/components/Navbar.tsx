import { Link } from 'react-router'

import { Button } from '@/components/ui/button'

const navLinks = [
  { href: '/#como-funciona', label: 'Cómo funciona' },
  { href: '/#para-quien', label: 'Para quién' },
]

function Navbar() {
  return (
    <header className="sticky top-0 z-30 border-b border-border/60 bg-background/80 backdrop-blur">
      <nav className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <Link to="/" className="flex items-center gap-2">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-primary font-semibold text-primary-foreground">
            P
          </span>
          <span className="text-lg font-semibold tracking-tight text-foreground">Psyko</span>
        </Link>

        <div className="hidden items-center gap-8 text-sm text-muted-foreground md:flex">
          {navLinks.map((link) => (
            <a key={link.href} href={link.href} className="transition-colors hover:text-foreground">
              {link.label}
            </a>
          ))}
        </div>

        <Button asChild size="sm">
          <a href="/#acceso">Solicitar acceso</a>
        </Button>
      </nav>
    </header>
  )
}

export default Navbar
