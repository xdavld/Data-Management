# Data Management - Open Source Lakehouse Container (mittels DuckDB)

- Abschlussprojekt im Rahmen der Vorlesung Data Management

## Worum geht es?

Es handelt sich um ein minimalistisches Setup für eine cloud-agnostische Data-Lakehouse-Architektur, basierend auf Apache Spark, ergänzt durch DuckDB und Visualisierungen mittels Apache Superset. 
MinIO dient dabei als Speicherschicht, Delta Lake als Speicherformat in Kombination mit Apache-Parquet-Dateien. Dieses Setup ist als Sandbox gedacht, um Experimente mit Data-Lakehouse-Architekturen durchzuführen.

## Architektur

Die Architektur der Lakehouse-Sandbox ist so konzipiert, dass sie die wesentlichen Komponenten eines realen Data Lakehouse nachbildet und gleichzeitig flexibel und Cloud-unabhängig ist.

![Architektur](docs/graphics/architecture.png)

- Storage: MinIO, eine leistungsstarke, Kubernetes-native Objektspeicherlösung.
- Data Format: Delta Lake, eine Open-Source-Speicherschicht, bietet ACID-Transaktionen, skalierbare Metadatenverarbeitung und vereinheitlicht Streaming- und Batch-Datenverarbeitung.
- File Format: Apache Parquet, ein freies und Open-Source-Dateiformat, das für Big Data entwickelt wurde.
- Data Processing Engine: Apache Spark, eine einheitliche Analyse-Engine, wird für die Verarbeitung großer Datenmengen verwendet. Spark bietet umfassende APIs für eine effiziente Datenverarbeitung und -analyse.

## Ordnerstruktur

.venv/
compute
├── data
├── duckdb-file
├   ├── persistent.duckdb
├── src
    ├── main.py
├── requirements.txt
├── Dockerfile
docs (Dokumentation)
minio
├── config
├── data
scraper
├── src
│   ├── scrape_glasdoor.py
├── Dockerfile
spark
├── data
├── src
    ├── main.py
├── Dockerfile
superset
.env
.gitignore
compose.yml
README.md

