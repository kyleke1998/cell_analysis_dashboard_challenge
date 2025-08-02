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
#### One liner to run the app using Docker in Code Space. This will create and load data from .csv into databse, start up backend API and frontend. 
```
docker-compose up --build -d
```

### Database Design Rationale
The overall rational is to create a design that focuses on enabling fast analytic workflows behind the dashboard, at the same time reducing redundancy via appropraite normalizations, and also making sure new cell populations can be added in future projects. This design can be used in the future to do analyses such as comparing cell population frequencies over time (e.g., baseline vs. day 7 or 14) using paired t-tests or linear mixed effects models to account for repeated measures. It also enables comparisons across treatment arms to identify population-level immune responses associated with different therapies.

- **Normalization**: Data is structured to reduce redundancy and ensure data integrity. Metadata regarding `subject`, `sample`, and `project` entities are separate and connected via foreign keys.
- **Fast Analytic workflow**: I tired to reduce the in-memory dataframe computations to a minimum and frontload majority of it to the database. `sample_cell_count` is a table in the long format.  Similarily, the `relative_cell_frequency` table has precomputed relative frequencies to accelerate downstream stats tests and visualizations so raw data does not need to be loaded into a dataframe for computation each time the endpoints are hit.
- **Extensibility**: For instance, `sample_cell_count` in the long format. It supports extensibility to more populations and efficient aggregation. 

### Repo Structure Rationale
The database layer uses DuckDB with separate SQL files for schema definitions and data loading. The backend is built with FastAPI and organized into modular components for database access, API routing, and statistical testing, promoting clean separation of logic. The frontend leverages Streamlit with a multi-page layout for clear navigation between summary views, statistical analyses, and subset exploration. Deployment is containerized using Docker and managed with docker-compose.


├── dashboard_app/                # Frontend UI app
│   ├── 1_About.py                # Project introduction & usage guide
│   └── pages/                    # Multi-page Streamlit interface
│       ├── Page_1_-_Summary_Table.py
│       ├── Page_2_-_Statistical_Analysis.py
│       └── Page_3_-_Subset_Analysis.py
│   ├── environment.yml           # Frontend specific conda environment
│   └── images/                   # Logo image
│
├── data/                         # Raw input + database connection config
│   ├── raw_csv/cell_count.csv    # Original flow cytometry data
│   └── duckdb_config.yaml        # Database connection config
│
├── data_model/sql/               # Database schema and loading scripts
│   ├── model/                    # CREATE TABLE statements
│   └── load/                     # SQL data loaders
│
├── docker-compose.yml            # Container orchestration (API + frontend)
├── Dockerfile                    # Backend container (FastAPI)
├── Dockerfile.streamlit          # Frontend container (Streamlit)
│
├── notebook/                     # Prototyping and EDA
│   └── sandbox.ipynb
│
├── scripts/                      
│   └── create_schema_and_load_data.py # Python CLI script for schema creation and data ingestion
│
├── src/                          # Core backend logic
│   ├── db/                       # Database abstraction layer
│   │   ├── connection.py         # DuckDB connection logic
│   │   ├── constant.py         
│   │   └── crud.py               # Reusable SQLAlchemy-style CRUD operations
│   ├── rest/                     # REST Endpoint logic
│   │   ├── model_rest.py         # Pydantic models
│   │   └── service.py            # API logic and handlers
│   └── stat_tests.py             # Statistical testing functions
│
├── README.md                     # Documentation
└── environment.yml               # Backend conda environment

## Contact
* Kyle Ke <siyangke98@gmail.com>
