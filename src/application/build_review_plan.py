import json
from typing import Any, Dict

from ..domain.llm_service import LlmService

_BUILD_REVIEW_PLAN_PROMPT = """\
Eres un asistente de pre-revisión de proyectos básicos de arquitectura frente \
a normativa urbanística municipal. Analiza el texto completo del documento \
del proyecto (documentación exclusivamente textual: memoria, tablas, anexos, \
certificados y normativa citada) que se te proporciona a continuación y \
construye un plan de revisión.

No inventes checks innecesarios ni obligaciones normativas que no se puedan \
justificar por el contenido real del documento: cada dato del plan debe estar \
fundamentado en lo que efectivamente aparece (o debería aparecer, según el \
tipo de proyecto detectado) en el documento. Si no tienes información \
suficiente para justificar un punto, no lo incluyas.

Responde ÚNICAMENTE con un JSON válido (nada de texto antes ni después, sin \
bloques de código markdown) con exactamente estas claves:

1. "tipo_proyecto": objeto con las claves "municipio", "uso", \
"obra_nueva_o_reforma", "ordenanza_aplicable", "numero_viviendas", \
"numero_plantas" — qué tipo de proyecto es.
2. "documentacion_esperada": lista de strings — qué documentación textual \
debería contener el proyecto (memoria, índice, estudio geotécnico, residuos, \
certificados, CTE, anexos, etc.) según el tipo de proyecto detectado.
3. "elementos_detectados": lista de strings — qué elementos tiene el \
proyecto (garaje, sótano, trasteros, piscina, ascensores, cubierta, \
instalaciones, zonas verdes, arbolado...).
4. "normativa_aplicable": lista de strings — qué normativa le aplica (PGOU, \
plan parcial, ordenanza, CTE, normativa autonómica y sectorial).
5. "usos_y_compatibilidad": string — usos permitidos y compatibilidad del \
proyecto con la ordenanza.
6. "parametros_urbanisticos_a_verificar": lista de strings — qué parámetros \
urbanísticos hay que comprobar (parcela mínima, ocupación, edificabilidad, \
retranqueos, alturas, plantas, fondo edificable, aparcamientos, \
ajardinamiento), a partir de lo declarado en el texto del proyecto.
7. "justificaciones_tecnicas_requeridas": lista de strings — qué \
justificaciones técnicas deberían aparecer según los elementos detectados \
(incendios, ventilación, energía, ruido, accesibilidad, garaje, piscina, \
trasteros, etc.).
8. "afecciones": lista de strings — arqueología, servidumbres aeronáuticas, \
patrimonio, arbolado, carreteras, cauces u otras que aplique la normativa.
9. "coherencia_interna_a_revisar": lista de strings — qué debe ser \
coherente (municipio, dirección, viviendas, superficies, alturas, fechas y \
normativa citada).
10. "afirmaciones_a_verificar": lista de objetos con las claves \
"afirmacion" y "ubicacion" — afirmaciones del proyecto como "cumple", \
"no aplica" o "no procede", con dónde aparecen, para comprobar después si \
tienen evidencia.
11. "puntos_no_automatizables": lista de strings — qué puntos no pueden \
comprobarse automáticamente y necesitarán revisión técnica por un profesional.

Recuerda: no afirmes cumplimiento ni incumplimiento legal, solo describe el \
plan de revisión. No inventes checks ni obligaciones que no puedas justificar \
con el contenido real del documento.
"""


BUILD_REVIEW_PLAN_TOOL = {
    "type": "function",
    "function": {
        "name": "build_review_plan",
        "description": (
            "Analiza el texto completo ya extraído de un proyecto básico de "
            "arquitectura (documentación exclusivamente textual: memoria, "
            "tablas, anexos, certificados y normativa citada) y construye un "
            "plan de revisión normativa: tipo de proyecto, documentación "
            "esperada, elementos detectados, normativa aplicable, parámetros "
            "urbanísticos a verificar, afecciones, coherencia interna, "
            "afirmaciones a comprobar y puntos que requieren revisión "
            "técnica manual. No decide si el proyecto cumple, solo planifica "
            "qué revisar."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
}


def build_review_plan(*, llm_service: LlmService, document_text: str) -> Dict[str, Any]:
    content = (
        f"{_BUILD_REVIEW_PLAN_PROMPT}\n\n"
        f"Texto completo del documento a analizar:\n\n{document_text}"
    )
    response = llm_service.make_request(
        messages=[{"role": "user", "content": content}],
    )
    return json.loads(response["content"])
