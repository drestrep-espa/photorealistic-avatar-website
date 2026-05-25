function Footer() {
  const year = new Date().getFullYear()

  return (
    <footer className="border-t border-border/60 bg-background">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 py-10 sm:flex-row">
        <div className="flex items-center gap-2">
          <span className="grid size-8 place-items-center rounded-lg bg-primary font-semibold text-primary-foreground">
            P
          </span>
          <span className="font-semibold tracking-tight text-foreground">Psyko</span>
        </div>

        <p className="text-sm text-muted-foreground">
          © {year} Psyko. Todos los derechos reservados.
        </p>
      </div>
    </footer>
  )
}

export default Footer
