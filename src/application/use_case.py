from src.infrastructure.agent import Agent

REVIEW_PROMPT = """
Revisa de forma preventiva el proyecto con el objetivo de detectar posibles deficiencias antes de su presentación al Ayuntamiento.

No tienes el texto del proyecto en este mensaje. `build_review_plan` analiza directamente el PDF completo del proyecto adjunto internamente, por lo que no debes pedir que se vuelva a proporcionar.

La revisión debe limitarse al contenido textual del proyecto: memoria, tablas, anexos, certificados y referencias normativas. No analices planos ni marques su ausencia como deficiencia. Cuando una comprobación dependa de cotas, geometrías, mediciones o contenido gráfico, utiliza el estado `fuera_del_alcance_de_la_revision_textual`.

## Flujo obligatorio

1. Utiliza `build_review_plan` para identificar todos los puntos aplicables al proyecto.
2. Separa los puntos para que cada comprobación trate una única cuestión. No agrupes edificabilidad, ocupación, altura, retranqueos u otros parámetros diferentes.
3. Para cada punto:
   - utiliza `search_project_document` para localizar la evidencia exacta dentro del proyecto;
   - utiliza `search_item` para localizar la normativa aplicable;
   - compara ambas evidencias;
   - emite una conclusión trazable.

`build_review_plan` sirve para construir el plan, pero su resultado no debe utilizarse como única evidencia. Las cifras, textos, fechas y páginas relevantes deben confirmarse mediante `search_project_document`.

No declares que una información no está localizada en el proyecto sin haber realizado antes una búsqueda específica con `search_project_document`. Si la primera búsqueda no es concluyente, reformula la consulta una vez utilizando términos más concretos, sinónimos o el valor numérico buscado.

No declares `normativa_no_recuperada` sin haber realizado una búsqueda normativa específica mediante `search_item`. Si los primeros resultados no son concluyentes, repite la búsqueda una vez con el municipio, ordenanza, artículo o parámetro más específico.

No incluyas en el informe todos los fragmentos recuperados. Selecciona únicamente la evidencia más relevante y concluyente.

## Contenido obligatorio de cada punto

Para cada cuestión revisada, muestra:

- cuestión revisada;
- norma aplicable;
- documento normativo;
- artículo, apartado y página, cuando estén disponibles;
- fragmento normativo concreto que establece la obligación;
- evidencia del proyecto, indicando página y fragmento o dato exacto;
- comparación explícita entre lo exigido y lo declarado;
- razonamiento de la conclusión;
- estado final;
- acción correctora.

## Estados permitidos

Utiliza únicamente:

- `cumple_segun_datos_declarados`
- `no_cumple_demostrado`
- `parcialmente_justificado`
- `no_justificado_en_el_proyecto`
- `normativa_no_recuperada`
- `incoherencia_interna`
- `fuera_del_alcance_de_la_revision_textual`
- `requiere_revision_tecnica`

Aplica los estados con estos criterios:

- `no_cumple_demostrado`: existe una obligación normativa concreta y evidencia suficiente del proyecto que demuestra que no se cumple.
- `no_justificado_en_el_proyecto`: la obligación normativa está localizada, pero tras buscar expresamente en el proyecto no aparece la justificación necesaria.
- `normativa_no_recuperada`: existe evidencia en el proyecto, pero no se ha podido localizar una norma suficientemente concreta para validarla.
- `incoherencia_interna`: dos o más datos del propio proyecto son incompatibles.
- `fuera_del_alcance_de_la_revision_textual`: la comprobación depende de planos, geometría, cotas o mediciones.
- `requiere_revision_tecnica`: existe evidencia textual, pero su validez necesita cálculo o criterio técnico especializado.

No confundas falta de normativa recuperada con falta de justificación en el proyecto. No afirmes incumplimiento basándote únicamente en que una información no ha sido encontrada.

## Comparaciones numéricas

Cuando existan valores numéricos, realiza siempre la operación de forma explícita.

Ejemplo:

Norma: edificabilidad máxima 0,46 m²/m².  
Proyecto: 0,4598 m²/m², página 5.  
Comparación: 0,4598 ≤ 0,46.  
Estado: `cumple_segun_datos_declarados`.

Cuando el resultado numérico sea favorable, pero necesite validación gráfica, indica:

“Cumple según los datos declarados en la memoria, pero no ha sido verificado gráficamente”.

No rebajes automáticamente a `parcialmente_justificado` una comparación numérica favorable únicamente porque no se hayan revisado los planos.

## Informe final

Al finalizar, genera un informe claro y trazable que incluya:

- resumen general del proyecto;
- número total de puntos generados;
- número de puntos revisados;
- puntos no comprobados;
- comprobaciones que cumplen según los datos declarados;
- incumplimientos demostrados;
- incoherencias internas;
- documentación o justificaciones no localizadas;
- normativa no recuperada;
- aspectos parcialmente justificados;
- cuestiones fuera del alcance de la revisión textual;
- cuestiones que requieren revisión técnica;
- acciones correctoras priorizadas.

No te limites a resumir el plan. Debes ejecutar realmente `search_project_document` y `search_item` sobre cada punto aplicable y basar todas las conclusiones en evidencia concreta.

Continúa hasta revisar todos los puntos aplicables. Para controlar el contexto y evitar búsquedas innecesarias, realiza como máximo dos búsquedas en el proyecto y dos búsquedas normativas por cada punto, salvo que exista una contradicción que requiera una comprobación adicional."""


def check_document_with_agent(agent: Agent):
    return agent.ask(REVIEW_PROMPT)
