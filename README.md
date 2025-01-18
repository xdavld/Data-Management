# Data Management - Open Source Lakehouse Container (mittels DuckDB) 
#### Abschlussprojekt im Rahmen der Vorlesung Data Management

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
Im Root-Verzeichnis des Projekts befinden sich die folgenden Ordner und Dateien, dabei führt die Datei `compose.yml` die Container-Konfigurationen zusammen:

Innerhalb des 'compute' Ordners befinden sich die Dateien für DuckDB und Ibis. Der 'docs' Ordner enthält die Dokumentation, 'minio' die Konfigurationen und Daten für MinIO, 'scraper' die Dateien für das Web-Scraping und 'spark' die Dateien für die Spark-Verarbeitung.

```
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
```

## Versionen

Der Programmcode wurde mit folgenden Versionen getestet und auf Podman Version 1.15.0 ausgeführt: 

- bitnami/spark:3.4.1
- apache/superset:latest
- minio:latest
- minio/mc:latest
- python:3.10-slim
- selenium/standalone-chrome:latest

## Installation

1. Repository klonen
2. .env Datei erstellen und die Variablen entsprechend anpassen für minio und superset (für die Abgabe wurde die .env Datei mitgeliefert)
3. Podman Container erstellen mittels:
```
podman-compose build
```
4. Podman Container starten mittels:
```
podman-compose up
```
## Herunterfahren

Podman Container stoppen mittels:
```
podman-compose down
```

## Anwendung
Erreichbarkeit der Services:
- MinIO: http://localhost:9000
- Apache Superset: http://localhost:8088
- Apache Spark: http://localhost:8080

Durch das Ausführen der `compose.yml`-Datei werden die Container gestartet, und die Services sind über die angegebenen URLs direkt erreichbar. Die Einrichtung der Services erfolgt dabei nahezu vollständig automatisch, sodass diese unmittelbar genutzt werden können.

Der einzige manuelle Schritt betrifft die Konfiguration von Apache Superset. Nach dem Login mit den Zugangsdaten aus der `.env`-Datei können neue Charts und Dashboards erstellt werden. Diese basieren auf den Datenanalysen, die mithilfe von DuckDB und Ibis durchgeführt wurden.

Apache Spark ist ebenfalls über die bereitgestellte URL zugänglich, sodass die ausgeführten Jobs eingesehen und überwacht werden können. Beim Starten der Container erfolgt ein automatischer Import der Daten in MinIO, die anschließend von Apache Spark verarbeitet werden. 

Dabei wird die hinterlegte Datei `ds_salaries.csv`, die Gehaltsdaten zu verschiedenen Jobpositionen und Standorten enthält, in drei separate Tabellen aufgeteilt. Diese Tabellen werden danach als Delta-Lake-Dateien im Parquet-Format in MinIO abgelegt, wodurch eine effiziente Speicherung und Weiterverarbeitung gewährleistet wird.
