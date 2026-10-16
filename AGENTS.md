# Guía del proyecto: Newproject (Data Science)

## Objetivo y modo de trabajo
- Proyecto: análisis y predicción sobre la base de datos AdventureWorks2025 (SQL Server), con un paradigma predictivo distinto al de `Customer_Churn`.
- El usuario escribe TODO el código y los archivos él mismo; el agente es guía y apoyo, no ejecutor.
- El agente NO debe crear ni editar archivos de código, notebooks ni datos del proyecto, salvo que el usuario lo pida explícitamente.
- El agente debe: explicar conceptos, proponer el siguiente paso, dar pistas y esquemas (pseudocódigo o fragmentos cortos), revisar el código del usuario, señalar errores, riesgos de data leakage y mejoras, y justificar métricas y decisiones.
- Ante un error, guiar al diagnóstico antes de dar la solución completa.
- Avanzar por etapas: problema de investigación, extracción SQL, EDA, preprocesamiento, features, modelado, evaluación, conclusiones.

## Idioma
- Responde siempre en español.
- Código, nombres de variables y funciones en inglés; comentarios y documentación en español.

## Entorno
- Plataforma: Windows, PowerShell.
- Lenguaje: Python 3.x
- Usar entorno virtual: `python -m venv .venv` y `.venv\Scripts\Activate.ps1`
- Instalar dependencias: `pip install -r requirements.txt`

## Estructura sugerida
- `data/raw/` datos originales (nunca modificar)
- `data/processed/` datos limpios
- `notebooks/` exploración y análisis (Jupyter)
- `src/` código reutilizable (limpieza, features, modelos)
- `models/` modelos entrenados
- `reports/` gráficos y resultados
- `tests/` pruebas

## Convenciones
- Seguir PEP 8; usar type hints en funciones en `src/`.
- Librerías preferidas: pandas, numpy, scikit-learn, matplotlib/seaborn.
- Fijar semillas aleatorias (`random_state=42`) para reproducibilidad.
- Lógica reutilizable va en `src/`, no duplicada en notebooks.
- Notebooks con nombres numerados: `01_eda.ipynb`, `02_modelado.ipynb`.

## Reglas
- No modificar ni borrar archivos en `data/raw/`.
- No subir datos sensibles, credenciales ni archivos grandes al repositorio (usar `.gitignore`).
- Preguntar antes de añadir dependencias nuevas.
- Explicar brevemente las decisiones de análisis y las métricas usadas.
- Validar siempre con train/test split o validación cruzada; evitar data leakage.

## Comandos
- Tests: `pytest`
- Formato: `black .`
- Lint: `ruff check .`
