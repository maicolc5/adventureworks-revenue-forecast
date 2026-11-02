# Notas del proyecto: Pronóstico de ingresos (AdventureWorks2025)

Última actualización: 29/10/2026. Estado: EDA casi cerrado (falta corregir sección 8 y revisar efecto calendario del reseller).

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

## Decisiones de estructura
- Se descarta la carpeta `src/`: el código vive en `01_data_extraction.py` y en los notebooks. Si las funciones se duplican entre notebooks, moverlas a un `utils.py` en la raíz.
- CSV oficial: `data/raw/raw_revenue_features.csv` (la copia en `data/` sobra).

## Resultados del EDA (02_eda.ipynb)
- Baselines evaluados sobre la misma muestra (desde el mes 13), h = 1, 6 y 12.
- Reseller: gana el snaive (MAE ~786k, MAPE ~30%).
- Online: gana el drift (h=1 ~126k; h=6 ~335k). Post-quiebre todos fallan a h=12 (MAPE ~62%).
- Online: usar log; reseller: componente estacional.
- statsmodels instalado (en requirements.txt).
- Reseller: patrón trimestral (ACF/PACF lag 3 = 0.51/0.48, banda ±0.34); lag 12 no significativo. Usar lags 1, 3 y 12 como candidatos.
- Online: la ACF de diff(log) está dominada por el quiebre de 6-2024; modelar con indicador de régimen.
- Pendiente: corregir sección 8 del notebook (aún menciona estacionalidad anual lag 12 = 0.80) y revisar efecto calendario del reseller.

## Próximos pasos
1. Cerrar EDA: ACF/PACF con bandas sobre diff(log) (online) y reseller; boxplot por mes/trimestre del reseller; revisar si el ingreso del reseller cae a fin de mes (efecto calendario).
2. Preprocesamiento (en notebook): constantes de recorte, log online, indicador de régimen.
3. Features: lags, medias móviles con shift(1), mes/trimestre.
4. Validación con origen móvil (h=6 y 12) y baselines recalculados.
5. Modelado, evaluación y conclusiones.

## Recordatorio
El usuario escribe todo el código; el agente guía y revisa (ver `AGENTS.md`).
