import os
from datetime import datetime

from dotenv import load_dotenv
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from rich import print

from src.application.build_review_plan import BUILD_REVIEW_PLAN_TOOL, build_review_plan
from src.application.search_item import SEARCH_ITEM_TOOL, search_item
from src.infrastructure.agent import Agent
from src.infrastructure.openai_llm_service import OpenAiLlmService
from src.infrastructure.openai_normative_search_service import OpenAiNormativeSearchService
from src.infrastructure.pypdf_text_extractor import PyPdfTextExtractor

load_dotenv()

DOCUMENT_PATH = "data/proyecto_basico_paginas_1_a_107.pdf"

llm_service = OpenAiLlmService(api_key=os.environ["OPENAI_API_KEY"])
normative_search_service = OpenAiNormativeSearchService(
    api_key=os.environ["OPENAI_API_KEY"],
    vector_store_id=os.environ["VECTOR_STORE_id"],
)
text_extractor = PyPdfTextExtractor()

print(f"[bold yellow]Extrayendo texto de {DOCUMENT_PATH}...[/bold yellow]")
document_text = text_extractor.extract_text(DOCUMENT_PATH)
print(f"[dim]Texto extraído: {len(document_text)} caracteres.[/dim]")


def run_build_review_plan(arguments):
    print(f"[bold cyan]>> tool build_review_plan[/bold cyan] args={arguments}")
    result = build_review_plan(llm_service=llm_service, document_text=document_text)
    print("[green]<< build_review_plan devolvió:[/green]")
    print(result)
    return result


def run_search_item(arguments):
    print(f"[bold cyan]>> tool search_item[/bold cyan] args={arguments}")
    result = search_item(
        normative_search_service=normative_search_service,
        query=arguments["query"],
        max_results=25,
    )
    print(f"[green]<< search_item devolvió {len(result)} fragmento(s):[/green]")
    for fragment in result:
        preview = fragment["text"][:120].replace("\n", " ")
        print(f"  [dim]- ({fragment['score']:.2f}) {fragment['filename']}: {preview}...[/dim]")
    return result


agent = Agent(
    llm_service=llm_service,
    tools=[BUILD_REVIEW_PLAN_TOOL, SEARCH_ITEM_TOOL],
    tool_executors={
        "build_review_plan": run_build_review_plan,
        "search_item": run_search_item,
    },
)

print("[bold yellow]Preguntando al agente...[/bold yellow]")
respuesta = agent.ask(
        f"""
Revisa de forma preventiva el proyecto cuyo texto completo se te proporciona más abajo, con el objetivo de detectar posibles deficiencias antes de su presentación al Ayuntamiento. Ya tienes el texto íntegro del proyecto en este mensaje: no necesitas (ni puedes) volver a solicitar el PDF en ningún momento, ni al llamar a `build_review_plan` ni en ningún otro paso.

La revisión debe limitarse al contenido textual suministrado: memoria, tablas, anexos, certificados y referencias normativas. No analices planos ni marques su ausencia como una deficiencia. Cuando una comprobación dependa de planos, cotas o geometrías, indícala como `fuera_del_alcance_de_la_revision_textual`.

Primero, utiliza `build_review_plan` para analizar el proyecto y construir un plan de revisión completo y adaptado a sus características.

Después, revisa cada punto aplicable de forma independiente mediante `search_item`. No agrupes en una misma revisión cuestiones diferentes como edificabilidad, ocupación, altura o retranqueos.

Para cada punto debes obtener y mostrar:

- cuestión revisada;
- norma aplicable;
- documento normativo;
- artículo, apartado y página, cuando estén disponibles;
- fragmento concreto que establece la obligación;
- evidencia del proyecto, indicando página y texto o dato localizado;
- comparación explícita entre lo exigido y lo declarado;
- razonamiento de la conclusión;
- estado final;
- acción correctora.

Utiliza únicamente estos estados:

- `cumple_segun_datos_declarados`
- `no_cumple_demostrado`
- `parcialmente_justificado`
- `no_justificado_en_el_proyecto`
- `normativa_no_recuperada`
- `incoherencia_interna`
- `fuera_del_alcance_de_la_revision_textual`
- `requiere_revision_tecnica`

No confundas `normativa_no_recuperada` con `no_justificado_en_el_proyecto`. No afirmes incumplimiento si no existe una norma concreta y una evidencia suficiente.

Cuando existan valores numéricos, realiza la comparación expresamente. Ejemplo:

Norma: edificabilidad máxima 0,46 m²/m².  
Proyecto: 0,4598 m²/m², página 5.  
Comparación: 0,4598 ≤ 0,46.  
Conclusión: `cumple_segun_datos_declarados`.

Si una conclusión depende de comprobar planos, indica:

“Cumple según los datos declarados en la memoria, pero no ha sido verificado gráficamente”.

Al finalizar, genera un informe claro y trazable que incluya:

- resumen general del proyecto;
- número total de puntos del plan;
- puntos revisados;
- puntos no comprobados;
- comprobaciones que cumplen según los datos declarados;
- incumplimientos o incoherencias demostrados;
- documentación o justificaciones no localizadas;
- normativa no recuperada;
- aspectos parcialmente justificados;
- cuestiones fuera del alcance de la revisión textual;
- acciones correctoras priorizadas.

No te limites a resumir el plan. Debes ejecutar realmente `search_item` para cada punto aplicable y basar todas las conclusiones en evidencia concreta del proyecto y de la normativa.

Continúa hasta revisar todos los puntos del plan o hasta haber intentado razonablemente localizar la normativa y la evidencia necesarias.

---

Texto completo del proyecto a revisar:

{document_text}
"""
)

print("[bold magenta]Respuesta final del agente:[/bold magenta]")
print(respuesta)

pdf = FPDF()
pdf.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
pdf.add_font("DejaVu", "B", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
pdf.add_page()
pdf.set_font("DejaVu", "B", 14)
pdf.multi_cell(0, 8, "Informe de pre-revisión del proyecto", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.set_font("DejaVu", "", 10)
pdf.multi_cell(
    0,
    5,
    datetime.now().strftime("Generado el %Y-%m-%d %H:%M:%S"),
    new_x=XPos.LMARGIN,
    new_y=YPos.NEXT,
)
pdf.ln(4)
pdf.set_font("DejaVu", "", 11)
pdf.multi_cell(0, 6, respuesta or "", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

output_path = f"data/informe/informe_revision_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
pdf.output(output_path)
print(f"[bold green]Informe guardado en {output_path}[/bold green]")
