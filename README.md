## Cell Analysis Dashboard Challenge
This dashboard provides an interactive analysis of immune cell population frequencies across clinical trial samples, allowing users to compute relative frequencies per sample and compare distributions between responders and non-responders to the drug miraclib. It also supports subset analysis to explore early treatment effects in melanoma PBMC samples at baseline, stratifying by project, response status, and sex.



### Highlights
- CLI utility to load CSV data into *DuckDB* from YAML configuration  
- Support for schema tracking and reproducible ingestion  
- Flexible database retrival methods using SQLAlchemy  
- Parametric and Non-Parametric statistical analysis methods exposed via API
- REST API for serving dashboard statistics and plotting built with FastAPI  
- Streamlit web app for interactive cell analysis dashboard  
- Containerized deployment via Docker with shared networking between API and dashboard app  


### Getting Started
#### One liner to run the app using Docker in CodeSpace. This will create and load data from .csv into databse, start up backend API and frontend. 
#### Important: CodeSpace instance must have at 16 GB of RAM!!
```
docker-compose up --build -d
```
#### To access the dashboard, link is dynamically generated in CodeSpace. Click PORTS and click on the `forwarded_address` where port is 8501.
<img width="2828" height="652" alt="image" src="https://github.com/user-attachments/assets/edcb16f2-f59c-4bb7-890f-d6bf6a7f1508" />





### Database Design Rationale
The overall rationale is to create a design that focuses on enabling fast analytic workflows behind the dashboard, at the same time reducing redundancy via appropraite normalizations, and ensure extensibility (e.g. more cell type can be added). This design can be used in the future to do analyses such as comparing cell population frequencies over time (e.g., baseline vs. day 7 or 14) using paired t-tests or linear mixed effects models to account for repeated measures. It also enables comparisons across treatment arms to identify population-level immune responses associated with different therapies.

- **Normalization**: Data is structured to reduce redundancy and ensure data integrity. Metadata regarding `subject`, `sample`, and `project` entities are separate and connected via foreign keys.
- **Fast Analytic workflow**: I tired to reduce the in-memory dataframe computations to a minimum and frontload majority of it to the database. `sample_cell_count` is a table in the long format.  Similarily, the `relative_cell_frequency` table has precomputed relative frequencies to accelerate downstream stats tests and visualizations so raw data does not need to be loaded into a dataframe for computation each time the endpoints are hit.
- **Extensibility**: For instance, `sample_cell_count` in the long format. It supports extensibility to more populations and efficient aggregation. 


### Repo Structure Rationale
The database layer uses DuckDB separate SQL files for schema definitions and data loading. The `.sql` scripts for creating the schema and ingesting data is all in `data_models/sql`. Importable modualized backend code is built with FastAPI and organized into modular components in `src`, including database abastration, API routing, and statistical testing. The frontend leverages Streamlit with a multi-page layout and is located in `dashboard_app`. Deployment is containerized using Docker and managed with docker-compose.


```
├── dashboard_app/   # Frontend UI app
│ ├── 1_About.py   
│ ├── pages/  
│ │ ├── Page_1_-Summary_Table.py
│ │ ├── Page_2-Statistical_Analysis.py
│ │ └── Page_3-_Subset_Analysis.py
│ ├── environment.yml   # Frontend-specific conda environment
│ └── images/   # Logo image(s)
│
├── data/ # Raw input & database config
│ ├── raw_csv/
│ │ └── cell_count.csv   # Raw data
│ └── duckdb_config.yaml   # DuckDB connection configuration
│
├── data_model/sql/   # Database schema & loaders
│ ├── model/   # CREATE TABLE scripts
│ └── load/   # SQL scripts to load data
│
├── docker-compose.yml   # Orchestrates backend + frontend containers
├── Dockerfile   # Backend (FastAPI) container build
├── Dockerfile.streamlit   # Frontend (Streamlit) container build
│
├── notebook/
│ └── sandbox.ipynb   # Prototyping and exploratory analysis
│
├── scripts/
│ └── create_schema_and_load_data.py   # CLI for schema + data ingestion
│
├── src/   # Backend application logic
│ ├── db/
│ │ ├── connection.py   # DuckDB connection
│ │ ├── constant.py   
│ │ └── crud.py   # database abstraction layer
│ ├── rest/
│ │ ├── model_rest.py   # Pydantic response models
│ │ └── service.py   
│ └── stat_tests.py   # Statistical test functions
│
├── README.md # Project documentation
└── environment.yml   # Backend conda environment
```
## Contact
* Kyle Ke <siyangke98@gmail.com>
