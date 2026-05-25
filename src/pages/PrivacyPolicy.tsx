import LegalPage from '@/components/LegalPage'

function PrivacyPolicy() {
  return (
    <LegalPage title="Política de privacidad" lastUpdated="25 de mayo de 2026">
      <p>
        Esta política describe cómo Psyko trata los datos personales que nos facilitas a través de
        este sitio web, en cumplimiento del Reglamento (UE) 2016/679 (RGPD) y de la Ley Orgánica
        3/2018 de Protección de Datos Personales y garantía de los derechos digitales (LOPDGDD).
      </p>

      <section>
        <h2>1. Responsable del tratamiento</h2>
        <ul>
          <li>
            <strong>Responsable:</strong> Daniel Restrepo de Juan
          </li>
          <li>
            <strong>Email de contacto:</strong>{' '}
            <a href="mailto:endrokosverde@gmail.com">endrokosverde@gmail.com</a>
          </li>
        </ul>
      </section>

      <section>
        <h2>2. Datos que recogemos</h2>
        <p>
          Únicamente recogemos la dirección de email que facilitas voluntariamente al solicitar
          acceso anticipado en el formulario de lista de espera.
        </p>
      </section>

      <section>
        <h2>3. Finalidad del tratamiento</h2>
        <ul>
          <li>Gestionar tu inscripción en la lista de espera del producto.</li>
          <li>
            Informarte por email sobre el lanzamiento, la apertura de plazas y novedades
            relacionadas con Psyko.
          </li>
        </ul>
      </section>

      <section>
        <h2>4. Base legal</h2>
        <p>
          La base jurídica del tratamiento es tu <strong>consentimiento explícito</strong> (art.
          6.1.a del RGPD), prestado al enviar el formulario.
        </p>
      </section>

      <section>
        <h2>5. Conservación de los datos</h2>
        <p>
          Tus datos se conservarán hasta que solicites la baja, retires tu consentimiento o se
          cumpla el propósito para el que fueron recogidos.
        </p>
      </section>

      <section>
        <h2>6. Destinatarios y encargados de tratamiento</h2>
        <p>
          Para prestar el servicio nos apoyamos en proveedores que actúan como encargados de
          tratamiento:
        </p>
        <ul>
          <li>
            <strong>Supabase Inc.</strong> (alojamiento de la base de datos donde se almacena tu
            email). Más información en{' '}
            <a href="https://supabase.com/privacy" target="_blank" rel="noreferrer">
              supabase.com/privacy
            </a>
            . Puede implicar transferencia internacional de datos a EE. UU. bajo las garantías
            adecuadas previstas en el RGPD.
          </li>
        </ul>
      </section>

      <section>
        <h2>7. Tus derechos</h2>
        <p>
          Puedes ejercer tus derechos de acceso, rectificación, supresión, oposición, limitación
          del tratamiento y portabilidad escribiendo a{' '}
          <a href="mailto:endrokosverde@gmail.com">endrokosverde@gmail.com</a>, indicando el
          derecho que deseas ejercer.
        </p>
        <p>
          Si consideras que el tratamiento no se ajusta a la normativa, tienes derecho a presentar
          una reclamación ante la Agencia Española de Protección de Datos (
          <a href="https://www.aepd.es" target="_blank" rel="noreferrer">
            www.aepd.es
          </a>
          ).
        </p>
      </section>
    </LegalPage>
  )
}

export default PrivacyPolicy
