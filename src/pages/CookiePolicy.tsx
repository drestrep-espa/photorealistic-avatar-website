import LegalPage from '@/components/LegalPage'

function CookiePolicy() {
  return (
    <LegalPage title="Política de cookies" lastUpdated="25 de mayo de 2026">
      <p>
        Esta política explica el uso de cookies y tecnologías similares en el sitio web de Psyko,
        en cumplimiento del artículo 22 de la Ley 34/2002 (LSSI-CE) y del RGPD.
      </p>

      <section>
        <h2>1. ¿Qué son las cookies?</h2>
        <p>
          Una cookie es un pequeño archivo de texto que se almacena en tu dispositivo cuando
          visitas un sitio web. Permiten recordar información sobre tu visita, como tu idioma
          preferido u otras configuraciones.
        </p>
      </section>

      <section>
        <h2>2. Cookies utilizadas en este sitio</h2>
        <p>
          Actualmente este sitio <strong>no utiliza cookies propias ni de terceros</strong> con
          fines de análisis, publicidad o seguimiento. Tampoco hay cookies de redes sociales
          embebidas.
        </p>
        <p>
          Si en el futuro incorporamos herramientas que utilicen cookies (por ejemplo, analítica
          web), actualizaremos esta política y solicitaremos tu consentimiento previo cuando sea
          necesario.
        </p>
      </section>

      <section>
        <h2>3. Cómo configurar las cookies en tu navegador</h2>
        <p>
          En cualquier momento puedes configurar tu navegador para aceptar, rechazar o eliminar
          las cookies. Consulta la ayuda de tu navegador para más detalles:
        </p>
        <ul>
          <li>
            <a
              href="https://support.google.com/chrome/answer/95647"
              target="_blank"
              rel="noreferrer"
            >
              Google Chrome
            </a>
          </li>
          <li>
            <a
              href="https://support.mozilla.org/es/kb/habilitar-y-deshabilitar-cookies-sitios-web-rastrear-preferencias"
              target="_blank"
              rel="noreferrer"
            >
              Mozilla Firefox
            </a>
          </li>
          <li>
            <a
              href="https://support.apple.com/es-es/guide/safari/sfri11471/mac"
              target="_blank"
              rel="noreferrer"
            >
              Safari
            </a>
          </li>
          <li>
            <a
              href="https://support.microsoft.com/es-es/windows/eliminar-y-administrar-cookies-168dab11-0753-043d-7c16-ede5947fc64d"
              target="_blank"
              rel="noreferrer"
            >
              Microsoft Edge
            </a>
          </li>
        </ul>
      </section>
    </LegalPage>
  )
}

export default CookiePolicy
