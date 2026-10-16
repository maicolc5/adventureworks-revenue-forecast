# Notas del proyecto: Pronóstico de ingresos (AdventureWorks2025)

Última actualización: 16/10/2026. Estado: definiendo la consulta SQL de extracción.

## Pregunta de investigación
¿Cuáles serán los ingresos mensuales (suma de `LineTotal`) por canal de venta en los próximos 6 y 12 meses, y qué modelo los pronostica con menor error frente a baselines ingenuos?

- Paradigma: series de tiempo (regresión), distinto al de Customer_Churn (clasificación).
- Granularidad: mensual. Fecha base: `OrderDate`.
- Variable objetivo: `SUM(LineTotal)` por mes y canal.
- Horizontes: 6 y 12 meses.
- Métricas: MAE, RMSE y MAPE (MAPE solo si no hay meses cercanos a cero).
- Baselines: naive (último valor) y naive estacional (mismo mes del año anterior).

## Hallazgos de la exploración SQL
- Rango de `OrderDate` en la copia: 2022-05-30 a 2025-06-29 (fechas desplazadas ~11 años respecto a la base original).
- Mayo 2022 incompleto (47 pedidos, solo 2 días).
- Junio 2025 incompleto/anómalo (905 pedidos, ingresos ~47 mil).
- Cambio de régimen en pedidos en línea (6-7/2024): pedidos pasan de ~340 a ~1,600-2,200 por mes y el ticket medio cae de ~1,700 a ~550-860. En ingresos el efecto es una tendencia ascendente, no un salto de 5 veces.
- Revendedores (`OnlineOrderFlag = 0`): estacionales, sin tendencia clara, ticket medio ~15,000-25,000, posible patrón cada ~3 meses (por confirmar con gráficos). No hay datos desde 5-2025.
- En línea (`OnlineOrderFlag = 1`): tendencia creciente.

## Decisiones tomadas
- Modelar cada canal por separado (no una serie total).
- Periodos distintos por canal:
  - Revendedores: 6-2022 a 4-2025 (35 meses).
  - En línea: 6-2022 a 5-2025 (36 meses).
- Extraer todo el rango en `data/raw/` sin filtrar; el recorte de meses incompletos se hace en el preprocesamiento con constantes explícitas.

## Decisiones pendientes
- Estrategia multi-horizonte: recursiva vs directa.
- Familia de modelos: estadísticos (ARIMA, Holt-Winters; requiere `statsmodels`, preguntar antes de instalar) vs regresión de ML con lags.
- Tratamiento del quiebre en el canal en línea: log, o entrenar solo con el régimen reciente.
- Validación: origen móvil (rolling origin / `TimeSeriesSplit`) en lugar de un único corte.
- Si se quiere un total, alinear los calendarios de pronóstico de ambos canales.
- Incluir o no `units` y `customers` (sugerido: sí).

## Consulta SQL propuesta (esquema, la escribe el usuario)
Una fila por mes y canal. Columnas:
- `month` (primer día del mes), `channel` ('online' / 'reseller'), `revenue` (SUM LineTotal), `orders` (COUNT DISTINCT SalesOrderID), `units` (SUM OrderQty), `customers` (COUNT DISTINCT CustomerID), `active_days`, `first_order_date`, `last_order_date`.

Advertencias:
- Leakage: las variables del mes t solo sirven como lags para pronosticar t+1 en adelante.
- No sumar campos del Header (`SubTotal`, `TotalDue`) tras el JOIN con Detail: se duplican. Usar `LineTotal` y `COUNT(DISTINCT ...)`.
- `LineTotal` no incluye impuestos ni flete.

Valores de control para validar la consulta:
- 6-2022: reseller = 1,538,408.31; online = 462,870.65.
- 5-2022: reseller = 489,328.58; online = 28,408.86.

## Próximos pasos
1. Escribir y validar la consulta mensual por canal.
2. Script `src/extract_monthly_revenue.py` (get_connection, extract, save_raw) que guarde `data/raw/monthly_revenue.csv`. Servidor y credenciales fuera del código (variable de entorno o archivo en `.gitignore`).
3. Crear estructura de carpetas y entorno virtual.
4. `notebooks/01_eda.ipynb`: serie por canal, gráfico de estacionalidad (mes vs año), ticket medio y pedidos aparte.
5. Preprocesamiento, features (lags, medias móviles, mes), modelado, evaluación, conclusiones.

## Recordatorio
El usuario escribe todo el código; el agente guía y revisa (ver `AGENTS.md`).
