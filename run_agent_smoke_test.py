import os
from datetime import datetime

from dotenv import load_dotenv
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from rich import print

from src.application.build_review_plan import BUILD_REVIEW_PLAN_TOOL, build_review_plan
from src.application.index_project_document import index_project_document
from src.application.search_item import SEARCH_ITEM_TOOL, search_item
from src.application.search_project_document import (
    SEARCH_PROJECT_DOCUMENT_TOOL,
    search_project_document,
)
from src.infrastructure.agent import Agent
from src.infrastructure.openai_llm_cost_tracker import OpenAiLlmCostTracker
from src.infrastructure.openai_llm_service import OpenAiLlmService
from src.infrastructure.openai_normative_search_service import OpenAiNormativeSearchService
from src.infrastructure.openai_project_document_search_service import (
    OpenAiProjectDocumentSearchService,
)

load_dotenv()

DOCUMENT_PATH = "data/proyecto_basico_paginas_1_a_107.pdf"

cost_tracker = OpenAiLlmCostTracker()
llm_service = OpenAiLlmService(api_key=os.environ["OPENAI_API_KEY"], cost_tracker=cost_tracker)
normative_search_service = OpenAiNormativeSearchService(
    api_key=os.environ["OPENAI_API_KEY"],
    vector_store_id=os.environ["VECTOR_STORE_id"],
)
PROJECT_DOCUMENT_VECTOR_STORE_ID = os.environ.get("PROJECT_DOCUMENT_VECTOR_STORE_ID")

project_document_search_service = OpenAiProjectDocumentSearchService(
    api_key=os.environ["OPENAI_API_KEY"],
    vector_store_id=PROJECT_DOCUMENT_VECTOR_STORE_ID,
)

if PROJECT_DOCUMENT_VECTOR_STORE_ID is None:
    print(f"[bold yellow]Indexando {DOCUMENT_PATH} en un vector store para búsquedas puntuales...[/bold yellow]")
    index_project_document(
        project_document_search_service=project_document_search_service,
        document_path=DOCUMENT_PATH,
    )
    print("[dim]Proyecto indexado (vector store creado para esta ejecución).[/dim]")
else:
    print(
        f"[dim]Reutilizando vector store ya indexado del proyecto "
        f"({PROJECT_DOCUMENT_VECTOR_STORE_ID}), no se vuelve a subir el PDF.[/dim]"
    )


def run_build_review_plan(arguments):
    print(f"[bold cyan]>> tool build_review_plan[/bold cyan] args={arguments}")
    result = build_review_plan(llm_service=llm_service, document_path=DOCUMENT_PATH)
    print("[green]<< build_review_plan devolvió:[/green]")
    print(result)
    return result


def run_search_item(arguments):
    print(f"[bold cyan]>> tool search_item[/bold cyan] args={arguments}")
    result = search_item(
        normative_search_service=normative_search_service,
        query=arguments["query"],
        max_results=15,
    )
    print(f"[green]<< search_item devolvió {len(result)} fragmento(s):[/green]")
    for fragment in result:
        preview = fragment["text"][:120].replace("\n", " ")
        print(f"  [dim]- ({fragment['score']:.2f}) {fragment['filename']}: {preview}...[/dim]")
    return result


def run_search_project_document(arguments):
    print(f"[bold cyan]>> tool search_project_document[/bold cyan] args={arguments}")
    result = search_project_document(
        project_document_search_service=project_document_search_service,
        query=arguments["query"],
        max_results=arguments.get("max_results", 8),
    )
    print(f"[green]<< search_project_document devolvió {len(result)} fragmento(s):[/green]")
    for fragment in result:
        preview = fragment["text"][:120].replace("\n", " ")
        print(f"  [dim]- ({fragment['score']:.2f}) {fragment['filename']}: {preview}...[/dim]")
    return result


agent = Agent(
    llm_service=llm_service,
    tools=[BUILD_REVIEW_PLAN_TOOL, SEARCH_ITEM_TOOL, SEARCH_PROJECT_DOCUMENT_TOOL],
    tool_executors={
        "build_review_plan": run_build_review_plan,
        "search_item": run_search_item,
        "search_project_document": run_search_project_document,
    },
)

print("[bold yellow]Preguntando al agente...[/bold yellow]")
respuesta = agent.ask(
        """
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

cost_summary = cost_tracker.summary()
print("[bold yellow]Coste de OpenAI de esta ejecución:[/bold yellow]")
print(f"  [bold]Total: ${cost_summary['total_cost_usd']:.4f}[/bold]")
print("  Por tool:")
for tool_name, tool_stats in cost_summary["by_tool"].items():
    print(
        f"    - {tool_name}: ${tool_stats['cost_usd']:.4f} "
        f"({tool_stats['calls']} llamada(s), "
        f"{tool_stats['input_tokens']} tokens entrada, "
        f"{tool_stats['cached_input_tokens']} cacheados, "
        f"{tool_stats['output_tokens']} tokens salida)"
    )
print("  Por modelo:")
for model_name, model_stats in cost_summary["by_model"].items():
    print(
        f"    - {model_name}: ${model_stats['cost_usd']:.4f} "
        f"({model_stats['calls']} llamada(s), "
        f"{model_stats['input_tokens']} tokens entrada, "
        f"{model_stats['cached_input_tokens']} cacheados, "
        f"{model_stats['output_tokens']} tokens salida)"
    )
