import LegalPage from '@/components/LegalPage'

function LegalNotice() {
  return (
    <LegalPage title="Aviso legal" lastUpdated="25 de mayo de 2026">
      <p>
        En cumplimiento de la Ley 34/2002, de 11 de julio, de Servicios de la Sociedad de la
        Información y Comercio Electrónico (LSSI-CE), se facilita la siguiente información sobre
        el titular de este sitio web.
      </p>

      <section>
        <h2>1. Datos identificativos del titular</h2>
        <ul>
          <li>
            <strong>Titular:</strong> Daniel Restrepo de Juan
          </li>
          <li>
            <strong>Email de contacto:</strong>{' '}
            <a href="mailto:endrokosverde@gmail.com">endrokosverde@gmail.com</a>
          </li>
        </ul>
      </section>

      <section>
        <h2>2. Objeto</h2>
        <p>
          Este sitio web tiene como finalidad presentar el servicio Psyko —una plataforma de
          videollamadas con avatares fotorrealistas para la práctica clínica de psicólogos— y
          permitir a los usuarios solicitar acceso anticipado mediante la lista de espera. En el
          momento actual, el sitio se encuentra en fase de pre-lanzamiento y no presta servicios
          comerciales.
        </p>
      </section>

      <section>
        <h2>3. Condiciones de uso</h2>
        <p>
          El acceso a este sitio es gratuito. El usuario se compromete a utilizar el contenido y
          servicios conforme a la ley, este aviso legal y la buena fe, absteniéndose de utilizarlo
          con fines ilícitos o que puedan dañar a terceros o al titular.
        </p>
      </section>

      <section>
        <h2>4. Propiedad intelectual</h2>
        <p>
          Todos los contenidos del sitio (textos, imágenes, código, diseños) son titularidad del
          responsable o cuentan con la correspondiente licencia. Queda prohibida su reproducción,
          distribución o modificación sin autorización expresa.
        </p>
      </section>

      <section>
        <h2>5. Responsabilidad</h2>
        <p>
          El titular no se hace responsable de los daños y perjuicios derivados del uso
          inadecuado del sitio, ni de la indisponibilidad temporal del mismo por causas técnicas.
        </p>
      </section>

      <section>
        <h2>6. Legislación aplicable</h2>
        <p>
          La relación entre el titular y los usuarios se regirá por la legislación española
          vigente.
        </p>
      </section>
    </LegalPage>
  )
}

export default LegalNotice
