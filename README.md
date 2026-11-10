# Dashboard interactivo de notas

Reproducción funcional de la imagen de referencia del dashboard de notas. Incluye datos ficticios del curso, filtros por sexo, sección, rango de promedio y asistencia, métricas, dos tipos de gráficos, tabla opcional y descarga CSV.

## Ejecutar

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publicar en Streamlit Community Cloud

Subir `app.py`, `requirements.txt` y `estudiantes_notas.csv` a la raíz de un repositorio de GitHub; elegir la rama `main` y el archivo principal `app.py` al publicar.

**Nota importante:** el PDF adjunto titulado `Dashboard_notas.pdf` describe una tarea distinta, más básica (saludos, botones, dos campos de texto y logo institucional). Esta implementación corresponde a la imagen de dashboard de notas, no al enunciado de ese PDF.
