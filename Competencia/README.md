# Competencia Final NLP — Proyecto ARTEMIS

## 1. Idea general de la competencia

La competencia no consiste en construir un chatbot general. El objetivo es construir un sistema que recibe una consulta en inglés de un operador de la estación espacial ficticia **Kuntur Station** y debe producir exactamente una **tool call** en formato canónico.

Ejemplo de salida esperada:

```text
get_telemetry(module='jaguar',metric='oxygen',timeframe_hours=12)
```

La clave es que el sistema debe decidir:

1. Qué herramienta usar.
2. Qué parámetros poner.
3. En qué orden escribirlos.
4. Con qué formato exacto generar la respuesta.

El sistema debe usar documentos técnicos recuperados como contexto, por eso el proyecto pide un sistema **RAG con Tool Calling**.

---

## 2. Pipeline general esperado

El flujo completo sería:

```text
query del operador
        ↓
encoder convierte la query en embedding
        ↓
FAISS busca documentos/chunks relevantes
        ↓
se arma un prompt con query + contexto recuperado + tools disponibles
        ↓
Llama-3.2-1B-Instruct fine-tuneado genera la tool call
        ↓
post-procesamiento normaliza el string
        ↓
submission.csv para Kaggle
```

Diagrama:

```text
┌──────────────────────────────────────┐
│ Query del test.csv                    │
│ "Oxygen levels dropped in Jaguar..."  │
└───────────────────┬──────────────────┘
                    ↓
┌──────────────────────────────────────┐
│ Encoder BAAI/bge-small-en-v1.5        │
│ Convierte texto → vector              │
└───────────────────┬──────────────────┘
                    ↓
┌──────────────────────────────────────┐
│ FAISS                                │
│ Busca chunks parecidos en docs MASA   │
└───────────────────┬──────────────────┘
                    ↓
┌──────────────────────────────────────┐
│ Contexto recuperado                   │
│ Ej: protocolo de fuga de oxígeno      │
│     severidad, módulo, razón, etc.    │
└───────────────────┬──────────────────┘
                    ↓
┌──────────────────────────────────────┐
│ Decoder Llama-3.2-1B-Instruct         │
│ Fine-tuneado para generar tool calls  │
└───────────────────┬──────────────────┘
                    ↓
┌──────────────────────────────────────┐
│ Output canónico                       │
│ send_alert(module='jaguar',...)       │
└──────────────────────────────────────┘
```

---

## 3. Qué es exactamente la tarea de Kaggle

El archivo `train.csv` trae ejemplos con esta estructura:

```text
id: Q-00001
query: "Oxygen readings in Jaguar have fallen below safe limits over the last 12 hours."
tool_call: get_telemetry(module='jaguar',metric='oxygen',timeframe_hours=12)
```

El archivo `test.csv` trae consultas sin respuesta:

```text
id: T-00001
query: "Which protocol should be activated for a radiation spike in Quetzal?"
```

El sistema debe producir la respuesta correcta, por ejemplo:

```text
activate_protocol(protocol_id='MASA-SEC-009',scope='module_only')
```

La evaluación se hace con **exact string match**. Esto significa que la predicción debe coincidir carácter por carácter con la respuesta correcta. No hay crédito parcial.

Por ejemplo, esta salida estaría mal:

```text
send_alert(severity='critical',module='quetzal',reason='radiation_spike')
```

Aunque los valores sean correctos, el orden de los parámetros no coincide con el formato esperado.

La salida correcta sería:

```text
send_alert(module='quetzal',severity='critical',reason='radiation_spike')
```

---

## 4. Qué son las tools

Las tools son acciones posibles que el sistema puede ejecutar. En la competencia no se ejecutan realmente, sino que se deben generar como texto.

Ejemplos:

```text
get_telemetry(module='jaguar',metric='oxygen',timeframe_hours=12)
send_alert(module='vicuna',severity='critical',reason='radiation_spike')
activate_protocol(protocol_id='MASA-SEC-008',scope='module_only')
no_action
```

El sistema tiene estas tools disponibles:

```text
get_telemetry
get_crew_status
get_module_status
send_alert
send_message
schedule_maintenance
activate_protocol
control_system
calculate_trajectory
request_supply
no_action
```

El problema no es simplemente clasificar una consulta. También hay que generar parámetros estructurados.

Ejemplo:

```text
Query:
"Send an urgent message to all crew about the pressure drop."

Output:
send_message(recipient='all_crew',priority='urgent')
```

Otro ejemplo:

```text
Query:
"Check pressure in Condor during the last hour."

Output:
get_telemetry(module='condor',metric='pressure',timeframe_hours=1)
```

Y una consulta informativa podría requerir:

```text
no_action
```

---

## 5. Por qué piden RAG

RAG significa **Retrieval-Augmented Generation**.

La idea es que el modelo no responda solo con lo que cree saber. Primero debe buscar documentos relevantes y luego generar la respuesta usando esos documentos.

Esto importa porque algunas consultas no contienen todos los parámetros explícitamente.

Ejemplo:

```text
Query:
"Activate the correct protocol for radiation lockdown in Quetzal."
```

La consulta dice `radiation lockdown`, pero quizá no dice directamente que el protocolo es:

```text
MASA-SEC-009
```

Ese dato puede estar en un documento técnico. El retrieval recupera el documento correcto y el decoder usa ese contexto para generar:

```text
activate_protocol(protocol_id='MASA-SEC-009',scope='module_only')
```

Sin RAG, el modelo tendría que memorizar todos los protocolos durante el fine-tuning. Eso es riesgoso con pocos datos y con un modelo pequeño.

En resumen:

```text
query → retrieval encuentra documentos relevantes → decoder genera tool call
```

---

## 6. Por qué piden un encoder

Un encoder convierte texto en un vector numérico.

Ejemplo:

```text
"Oxygen leak in Jaguar"
        ↓ encoder
[0.12, -0.44, 0.87, ..., 0.31]
```

Un documento también se convierte en vector:

```text
"Jaguar oxygen emergency procedures..."
        ↓ encoder
[0.10, -0.41, 0.82, ..., 0.29]
```

Si los vectores son parecidos, significa que los textos hablan de cosas similares.

En esta competencia el encoder obligatorio es:

```text
BAAI/bge-small-en-v1.5
```

Su función es recuperar documentos relevantes:

```text
query → embedding
chunk del documento → embedding
comparar embeddings → recuperar documentos relevantes
```

Ejemplo:

```text
Query:
"Radiation levels are spiking in Quetzal. What emergency action applies?"

Chunks candidatos:
A. "Quetzal radiation protocol MASA-SEC-009..."
B. "Tucan humidity maintenance..."
C. "Docking procedures for Vicuna..."

El encoder debería poner A más cerca de la query.
```

---

## 7. Por qué piden FAISS

FAISS permite hacer búsqueda eficiente por similitud vectorial.

El flujo sería:

```text
1. Dividir documentos en chunks.
2. Calcular embedding de cada chunk con BGE.
3. Guardar esos embeddings en FAISS.
4. Para cada query:
   - calcular embedding de la query
   - buscar los top-k chunks más similares
   - usar esos chunks como contexto para Llama
```

Ejemplo:

```python
query = "What protocol governs oxygen leak in Jaguar?"
top_chunks = faiss.search(query_embedding, k=5)
```

Resultado ideal:

```text
1. MASA-DOC-014 chunk 2: oxygen leak emergency in Jaguar
2. MASA-DOC-003 chunk 0: Jaguar life support systems
3. MASA-DOC-018 chunk 1: alert severity rules
```

---

## 8. Por qué piden un decoder

Un decoder es un modelo de lenguaje generativo. Toma texto como entrada y genera texto de salida token por token.

En esta competencia el decoder obligatorio es:

```text
meta-llama/Llama-3.2-1B-Instruct
```

El decoder no busca documentos. Su trabajo es generar la tool call final.

Ejemplo de entrada al decoder:

```text
System:
You are a tool-calling assistant. Return only the canonical tool call.

Available tools:
get_telemetry(module,metric,timeframe_hours)
send_alert(module,severity,reason)
activate_protocol(protocol_id,scope)
...

Context:
MASA-DOC-009 says radiation lockdown in Quetzal uses MASA-SEC-009 with module_only scope.

Query:
"Activate the correct protocol for a radiation lockdown in Quetzal."

Answer:
```

Salida esperada:

```text
activate_protocol(protocol_id='MASA-SEC-009',scope='module_only')
```

---

## 9. Diferencia entre encoder y decoder

| Modelo | Qué recibe | Qué produce | Para qué sirve |
|---|---|---|---|
| Encoder BGE | Query o chunk de documento | Vector / embedding | Buscar información relevante |
| Decoder Llama | Prompt con query + contexto | Texto | Generar la tool call |

Más simple:

```text
Encoder:
"oxygen leak in Jaguar" → [0.1, 0.9, -0.2, ...]

Decoder:
"Given this query and context..." → send_alert(module='jaguar',...)
```

El encoder no escribe. El decoder sí.

El decoder no es bueno buscando entre muchos documentos si no se los das. El encoder ayuda a encontrar esos documentos.

---

## 10. Por qué piden fine-tuning

El fine-tuning del decoder es obligatorio. No basta con prompt engineering.

Llama-3.2-1B-Instruct ya sabe seguir instrucciones, pero no necesariamente sabe:

1. Usar exactamente las 10 tools del proyecto.
2. Respetar el formato canónico.
3. Ordenar los parámetros como exige la competencia.
4. Usar comillas simples.
5. Evitar texto adicional.
6. Mapear consultas de MASA a herramientas específicas.
7. Convertir `Cóndor` en `condor`.
8. Saber cuándo responder `no_action`.
9. Inferir parámetros tipo enum desde lenguaje natural.

El fine-tuning le enseña ese patrón.

Ejemplo de entrenamiento:

```text
Input:
Query: "Check oxygen levels in Jaguar over the past 12 hours."
Context: "Jaguar life support telemetry includes oxygen monitoring..."
Tools: ...

Target:
get_telemetry(module='jaguar',metric='oxygen',timeframe_hours=12)
```

Otro ejemplo:

```text
Input:
Query: "There is a radiation spike in Vicuna. Alert the station."
Context: "Radiation spikes are critical events..."

Target:
send_alert(module='vicuna',severity='critical',reason='radiation_spike')
```

---

## 11. RAG y fine-tuning no son lo mismo

No compiten. Se complementan.

```text
Fine-tuning:
Le enseña al decoder el formato, las tools y el estilo de salida.

RAG:
Le da información específica de documentos que puede necesitar para decidir parámetros.
```

Ejemplo donde fine-tuning puede bastar:

```text
Query:
"Get temperature telemetry for Tucan during the last 24 hours."

Respuesta:
get_telemetry(module='tucan',metric='temperature',timeframe_hours=24)
```

Ejemplo donde RAG ayuda mucho:

```text
Query:
"Activate the protocol for a Class-A life support cascade in Jaguar."
```

La query no dice el `protocol_id`. Ese dato puede estar en un documento.

---

## 12. Archivos entregados y uso de cada uno

| Archivo | Uso |
|---|---|
| `train.csv` | Entrenar/fine-tunear el decoder y crear validación local |
| `test.csv` | Generar predicciones finales para Kaggle |
| `consultas_centro_control.json` | Evaluar retrieval y posibles mejoras del encoder/reranking |
| `base_conocimiento/` | Corpus de documentos técnicos para RAG |
| `tools_definition.json` | Definición de tools, parámetros, enums y orden correcto |
| `sample_submission.csv` | Plantilla para generar el archivo final |

Uso ideal de `train.csv`:

```text
- Entrenar Llama.
- Crear validación local.
- Analizar distribución de tools.
- Detectar duplicados o labels inconsistentes.
```

Uso ideal de `consultas_centro_control.json`:

```text
- Evaluar Recall@k del retrieval.
- Identificar documentos difíciles.
- Usar hard negatives.
- Mejorar búsqueda densa o híbrida.
```

---

## 13. Formato canónico

Las reglas principales son:

```text
1. Parámetros en el orden correcto.
2. Sin espacios después de comas ni alrededor de =.
3. Strings con comillas simples.
4. Todo en minúsculas, excepto protocol_id.
5. Números sin comillas.
```

Ejemplo válido:

```text
get_telemetry(module='condor',metric='pressure',timeframe_hours=1)
```

Ejemplo inválido por espacios:

```text
get_telemetry(module = 'condor', metric = 'pressure', timeframe_hours = 1)
```

Ejemplo inválido por comillas dobles:

```text
get_telemetry(module="condor",metric="pressure",timeframe_hours=1)
```

Ejemplo inválido por número como string:

```text
get_telemetry(module='condor',metric='pressure',timeframe_hours='1')
```

Ejemplo inválido por orden:

```text
get_telemetry(metric='pressure',module='condor',timeframe_hours=1)
```

---

## 14. Cómo se vería una solución ideal

Una solución ideal tendría varias capas.

### 14.1 Exploración de datos

Preguntas iniciales:

```text
¿Cuántos ejemplos hay por tool?
¿Hay tools desbalanceadas?
¿Hay duplicados?
¿Hay queries iguales con tool_call distinta?
¿Qué tan frecuentes son los módulos?
¿Qué parámetros son más difíciles?
¿Cuántos ejemplos son no_action?
```

Ejemplo de análisis:

```text
Tool distribution:
get_telemetry          610
send_alert             420
activate_protocol      350
get_module_status      300
no_action              260
...
```

Esto ayuda a detectar clases difíciles o desbalanceadas.

---

### 14.2 Limpieza

Estrategias:

```text
1. Eliminar duplicados exactos.
2. Si hay query duplicada con mismo label, dejar una.
3. Si hay query duplicada con labels distintos, revisar.
4. Normalizar comillas raras.
5. Validar que todo tool_call sea parseable.
6. Validar que parámetros estén dentro de tools_definition.json.
```

Ejemplo de validador:

```python
def is_valid_tool_call(tool_call, tools_definition):
    # Verifica:
    # - nombre de tool existe
    # - parámetros esperados
    # - orden correcto
    # - valores enum válidos
    # - formato canónico
    return True
```

---

### 14.3 Chunking de documentos

Los documentos técnicos se dividen en chunks.

Ejemplo:

```text
MASA-DOC-009/doc.md

Chunk 0:
"# Radiation Safety Protocols..."

Chunk 1:
"MASA-SEC-009 applies to radiation lockdown..."

Chunk 2:
"For Quetzal, module_only scope is used unless..."
```

Recomendación razonable:

```text
chunk_size: 300 a 600 tokens
overlap: 50 a 100 tokens
```

El overlap evita cortar información importante entre dos chunks.

---

### 14.4 Retrieval con encoder + FAISS

Para cada chunk:

```text
chunk text → BGE encoder → vector
```

Se guarda algo así:

```json
{
  "doc_id": "MASA-DOC-009",
  "chunk_id": 12,
  "text": "Radiation lockdown uses MASA-SEC-009...",
  "vector": [0.123, -0.456]
}
```

Luego, para cada query:

```text
query → vector → FAISS → top-k chunks
```

Una solución ideal evalúa retrieval usando `consultas_centro_control.json`:

```text
Recall@1: ¿el doc correcto aparece como primer resultado?
Recall@3: ¿el doc correcto aparece en los 3 primeros?
Recall@5: ¿el doc correcto aparece en los 5 primeros?
```

---

### 14.5 Hybrid search

Hybrid search combina búsqueda densa y búsqueda lexical.

```text
Búsqueda densa:
Usa embeddings. Es buena para significado semántico.

Búsqueda lexical:
Usa palabras exactas, BM25 o TF-IDF. Es buena para IDs, nombres raros y códigos.
```

Esto importa porque hay elementos como:

```text
MASA-SEC-009
Cóndor
Vicuña
Colibrí
Tucán
oxygen_leak
radiation_spike
```

Una solución ideal podría hacer:

```text
top-10 dense con FAISS
top-10 BM25
unir candidatos
rerankear
quedarse con top-5 final
```

---

### 14.6 Reranking

Reranking significa reordenar los documentos recuperados con una señal más precisa.

Ejemplo:

```text
FAISS devuelve:
1. MASA-DOC-012
2. MASA-DOC-009
3. MASA-DOC-018

Pero el reranker nota que MASA-DOC-009 contiene "radiation lockdown", entonces lo sube:
1. MASA-DOC-009
2. MASA-DOC-012
3. MASA-DOC-018
```

Una forma simple:

```text
score final = 0.7 * dense_score + 0.3 * lexical_score
```

---

### 14.7 Fine-tuning del decoder

Ejemplo ideal de dato para fine-tuning:

```text
### Instruction
Return only the canonical tool call. Do not explain.

### Tools
get_telemetry(module,metric,timeframe_hours)
send_alert(module,severity,reason)
activate_protocol(protocol_id,scope)
...

### Retrieved context
MASA-DOC-014:
Oxygen leaks in Jaguar require high severity alerts with reason oxygen_leak.

### Query
"Jaguar oxygen levels indicate a leak. Send the appropriate alert."

### Answer
send_alert(module='jaguar',severity='high',reason='oxygen_leak')
```

El target del entrenamiento debe ser solo:

```text
send_alert(module='jaguar',severity='high',reason='oxygen_leak')
```

No debe incluir explicaciones.

---

## 15. Ejemplos de solución ideal

### Ejemplo 1: telemetría directa

```text
Query:
"Check oxygen telemetry in Jaguar over the last 12 hours."
```

Razonamiento:

```text
"Check telemetry" → get_telemetry
"oxygen" → metric='oxygen'
"Jaguar" → module='jaguar'
"last 12 hours" → timeframe_hours=12
```

Salida:

```text
get_telemetry(module='jaguar',metric='oxygen',timeframe_hours=12)
```

---

### Ejemplo 2: alerta con severidad inferida desde documento

```text
Query:
"Radiation readings in Quetzal exceeded emergency limits. Alert the correct module."
```

Contexto recuperado:

```text
MASA-DOC-009:
Radiation spikes above emergency threshold must be reported as critical alerts.
Reason code: radiation_spike.
```

Razonamiento:

```text
"Alert" → send_alert
"Quetzal" → module='quetzal'
"emergency limits" + documento → severity='critical'
"Radiation readings" → reason='radiation_spike'
```

Salida:

```text
send_alert(module='quetzal',severity='critical',reason='radiation_spike')
```

---

### Ejemplo 3: protocolo

```text
Query:
"Activate the radiation lockdown protocol for Quetzal only."
```

Contexto recuperado:

```text
MASA-DOC-009:
Radiation lockdown is governed by MASA-SEC-009.
If only one module is affected, use module_only scope.
```

Salida:

```text
activate_protocol(protocol_id='MASA-SEC-009',scope='module_only')
```

---

### Ejemplo 4: control de sistema

```text
Query:
"Decrease cooling in Condor."
```

Salida:

```text
control_system(module='condor',system='cooling',action='decrease')
```

---

### Ejemplo 5: no_action

```text
Query:
"Who designed the naming convention for the Kuntur Station modules?"
```

Razonamiento:

```text
Es una pregunta informativa o histórica.
No pide ejecutar una acción operacional.
```

Salida:

```text
no_action
```

---

## 16. Prompt de inferencia recomendado

Ejemplo:

```text
You are a tool-calling system for MASA Kuntur Station.

Your task:
Given a user query and retrieved technical context, output exactly one canonical tool call.

Rules:
- Return only the tool call.
- Do not explain.
- Use only the allowed tools and enum values.
- Preserve parameter order exactly.
- Use single quotes for string values.
- Use no spaces after commas or around equals.
- Use lowercase values except protocol_id.
- If no operational action is required, output no_action.

Allowed tools:
1. get_telemetry(module,metric,timeframe_hours)
   module ∈ condor, quetzal, jaguar, colibri, vicuna, tucan
   metric ∈ temperature, pressure, oxygen, radiation, humidity, power
   timeframe_hours ∈ 1, 6, 12, 24
...

Retrieved context:
[MASA-DOC-009 chunk 2]
Radiation lockdown is governed by MASA-SEC-009...

Query:
Activate the radiation lockdown protocol for Quetzal only.

Answer:
```

Salida esperada:

```text
activate_protocol(protocol_id='MASA-SEC-009',scope='module_only')
```

---

## 17. Post-procesamiento

Como el score es exact match, no conviene confiar completamente en el output bruto del modelo.

El modelo podría generar:

```text
The answer is: get_telemetry(module='jaguar',metric='oxygen',timeframe_hours=12)
```

Se debe extraer solo:

```text
get_telemetry(module='jaguar',metric='oxygen',timeframe_hours=12)
```

También puede generar espacios:

```text
get_telemetry(module='jaguar', metric='oxygen', timeframe_hours=12)
```

Y se debe normalizar a:

```text
get_telemetry(module='jaguar',metric='oxygen',timeframe_hours=12)
```

También se deben normalizar módulos con acentos:

```text
module='cóndor' → module='condor'
module='colibrí' → module='colibri'
module='vicuña' → module='vicuna'
module='tucán' → module='tucan'
```

---

## 18. Lo que no se puede hacer

Restricciones importantes:

```text
No usar otro decoder distinto de meta-llama/Llama-3.2-1B-Instruct.
No usar otro encoder distinto de BAAI/bge-small-en-v1.5.
No usar APIs pagas como OpenAI, Claude, Gemini o Cohere.
No usar datos externos no entregados.
No entrenar con test.csv.
No reemplazar el LLM por un clasificador.
Sí o sí hacer fine-tuning del decoder.
Entrenar en PyTorch.
Hacer que el resultado sea replicable.
```

Sí está permitido hacer post-procesamiento, regex y normalización de formato.

---

## 19. Fases recomendadas del proyecto

### Fase 1: baseline funcional rápido

```text
1. Cargar train/test/tools/docs.
2. Limpiar duplicados básicos.
3. Crear chunks de documentos.
4. Crear embeddings con BGE.
5. Crear índice FAISS.
6. Para cada query, recuperar top-3 chunks.
7. Fine-tunear Llama con train.csv.
8. Inferir test.csv.
9. Postprocesar outputs.
10. Generar submission.csv.
```

---

### Fase 2: mejorar retrieval

```text
1. Evaluar Recall@k usando consultas_centro_control.json.
2. Probar chunk sizes.
3. Probar top-k 3, 5, 8.
4. Agregar BM25.
5. Agregar reranking simple.
6. Usar hard negatives para ajustar retrieval.
```

---

### Fase 3: mejorar decoder

```text
1. Mejorar formato de prompt.
2. Agregar contexto recuperado al entrenamiento.
3. Balancear ejemplos por tool.
4. Data augmentation permitida con modelos open-source.
5. Entrenar con LoRA.
6. Evaluar exact match local.
```

---

### Fase 4: mejorar post-procesamiento

```text
1. Parser robusto de tool calls.
2. Corrección de orden de parámetros.
3. Normalización de módulos con acentos.
4. Validación contra tools_definition.json.
5. Si output inválido, intentar reparación.
6. Si sigue inválido, usar fallback razonable.
```

---

## 20. Estructura recomendada del notebook

```text
# 1. Carga y exploración de datos
- Cargar train.csv
- Cargar test.csv
- Cargar consultas_centro_control.json
- Cargar tools_definition.json
- Cargar documentos Markdown
- Analizar distribución de tools
- Analizar duplicados
- Analizar valores inválidos

# 2. Preprocesamiento
- Limpieza de train
- Parser de tool_call
- Normalización de labels
- Chunking de documentos
- Preparación de datasets de fine-tuning

# 3. Retrieval
- Embeddings con BAAI/bge-small-en-v1.5
- Construcción FAISS
- Evaluación Recall@k
- Hybrid search / reranking si aplica
- Exportar retrieval_index.json

# 4. Fine-tuning del decoder
- Cargar Llama-3.2-1B-Instruct
- Configurar LoRA/QLoRA
- Entrenar en PyTorch
- Validar exact match local
- Guardar checkpoint

# 5. Inferencia
- Para cada query de test:
    query → retrieval → prompt → decoder → postproceso

# 6. Generación de submission.csv
- Validar formato final
- Guardar CSV con columnas id,tool_call
```

---

## 21. Estructura recomendada del entregable

```text
entrega_grupo_XX.zip/
│
├── pipeline.ipynb
├── scripts/
│   ├── chunker.py
│   ├── finetune_decoder.py
│   └── utils.py
│
├── prompts/
│   └── system_prompt.yaml
│
├── models/
│   ├── decoder/
│   │   ├── adapter_config.json
│   │   ├── adapter_model.safetensors
│   │   ├── tokenizer.json
│   │   └── ...
│   │
│   └── encoder/
│       ├── config.json
│       ├── model.safetensors
│       ├── tokenizer.json
│       └── ...
│
├── retrieval_index.json
└── requirements.txt
```

---

## 22. Intuición final

Piensa en el sistema como dos cerebros trabajando juntos:

```text
Encoder/Retrieval:
"Déjame buscar en los manuales qué dice MASA sobre esto."

Decoder/Fine-tuned Llama:
"Con esa información, voy a escribir exactamente la tool call correcta."
```

El encoder es como el bibliotecario.

El decoder es como el operador que llena el comando final.

FAISS es la estantería indexada que permite buscar rápido.

RAG es el proceso completo de buscar primero y generar después.

Fine-tuning es entrenar al operador para que use el formato exacto que pide la estación espacial.

Post-procesamiento es el inspector final que evita perder puntos por espacios, comillas, acentos u orden incorrecto.

La competencia se gana no solo con un buen modelo, sino con un pipeline muy cuidadoso, porque el score no perdona errores pequeños.
