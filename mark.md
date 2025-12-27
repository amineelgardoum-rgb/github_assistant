```
graph TD
    subgraph Data Ingestion
        A[Finnhub API] --> B(Kafka Producer)
    end

    subgraph Streaming Layer
        B --> C[Kafka Cluster]
        C --> D(Kafka Consumer)
    end

    subgraph Storage & ELT
        D --> E[MinIO (Bronze Layer)]
        E -- "Data copied via DAGs" --> F(Apache Airflow Orchestration)
        F -- "Loads to Staging Tables" --> G[PostgreSQL Data Warehouse]
        F -- "Triggers dbt Models" --> H(dbt Transformation)
        H -- "Builds Silver/Gold Layers" --> G
    end

    subgraph Data Serving
        G --> I(RESTful API)
    end

    subgraph Monitoring & Management
        C -- "Kafka Topic Inspection" --> J(Kafdrop)
        K(Docker Monitor Service) -- "Sends Container Stats" --> L[Elasticsearch Cluster]
        L -- "Visualized by" --> M(Kibana)
        G -- "Managed via" --> N(pgAdmin)
    end

    %% Class Definitions for better visual distinction
    classDef external fill:#f9f,stroke:#333,stroke-width:2px,font-weight:bold;
    class A, J, K, L, M, N external; %% Finnhub, Kafdrop, Docker Monitor, Elasticsearch, Kibana, pgAdmin

    classDef storage fill:#fff,stroke:#333,stroke-width:2px,font-weight:bold;
    class E, G storage; %% MinIO, PostgreSQL

    classDef service fill:#ccf,stroke:#333,stroke-width:2px,font-weight:bold;
    class B, D, F, H, I service; %% Kafka Producer, Kafka Consumer, Airflow, dbt, RESTful API

    classDef broker fill:#cfc,stroke:#333,stroke-width:2px,font-weight:bold;
    class C broker; %% Kafka Cluster
```mermaid

