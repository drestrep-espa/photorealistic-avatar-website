from dotenv import load_dotenv
from rich import print

from src.endpoints.handler import check_document

load_dotenv()

DOCUMENT_PATH = "data/proyecto_basico_paginas_1_a_107.pdf"

print(f"[bold yellow]Revisando {DOCUMENT_PATH}...[/bold yellow]")
print(
    "[dim]Se reindexará el proyecto en un vector store nuevo y se borrará al terminar.[/dim]"
)

resultado = check_document(DOCUMENT_PATH)

print("[bold magenta]Respuesta final del agente:[/bold magenta]")
print(resultado["summary"])

print(f"[bold green]Informe guardado en {resultado['report_path']}[/bold green]")

cost_summary = resultado["cost_summary"]
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
