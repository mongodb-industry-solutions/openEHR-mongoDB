# openEHR MongoDB Project

This repository contains tools and scripts for managing and enriching clinical compositions from openEHR data, optimized for MongoDB as a scalable and flexible backend for healthcare applications.

## Project Overview

The openEHR MongoDB project addresses the limitations of traditional relational database systems in handling complex hierarchical clinical data at scale, by leveraging MongoDB's document model.

### Key Objectives

- **Improve Query Performance:** Optimized queries with MongoDB's flexible schema and indexing capabilities.
- **Support Analytical and Operational Use Cases:** Dual-use scenarios for real-time patient data access and advanced analytics.
- **Simplify Data Storage:** Efficient storage with a hybrid model combining canonical JSON and denormalized fields for queries.
- **Enable Scalability and Maintainability:** Supports over a billion clinical compositions with minimal operational overhead.
- **Open Data architecture:** Support for data querying out of openEHR, supporting new querying patterns

---

## Features

- **Synthetic Data Generation:** Generate realistic clinical compositions based on predefined schemas using `Faker` and MongoDB's `ObjectId`.
- **Data Enrichment:** Enrich generated compositions with additional metadata, search parameters, and AQL-mapped fields.
- **MongoDB Upload:** Upload enriched compositions to a MongoDB database for querying and analysis.
- **Hybrid Data Representation:** Combines canonical JSON and flattened data to support efficient queries while maintaining semantic integrity.

---

## Folder Structure

```plaintext
.
├── enriched_output        # Folder for storing enriched JSON files
├── output                 # Folder for storing generated synthetic compositions
├── schemas                # JSON schemas for different clinical compositions
│   ├── Corona_composition.json
│   ├── Ex1_Composition_Immunitzacio.json
│   ├── minimal_observation.json
│   └── ...                # Additional schemas
├── testData               # Test data files for compositions
├── 1_generateSyntheticCompositions.py  # Script to generate synthetic compositions
├── 2_enrichParams.py      # Script to enrich compositions with metadata
├── 3_uploadToMongoDB.py   # Script to upload enriched compositions to MongoDB
├── config.json            # Configuration file for schemas and database details
└── README.md              # Documentation
```
---

## Scripts and Usage

### 1. **Generate Synthetic Compositions**
Generates synthetic clinical compositions based on predefined schemas.

```python
python 1_generateSyntheticCompositions.py
```

- **Input:** `schemas/` folder and `config.json`.
- **Output:** JSON files saved to the `output/` folder.

---

### 2. **Enrich Parameters**
Enriches generated compositions with:
- Searchable metadata (`AQLSearchParams`).
- Relationships (`RelatedTo`).
- Enriched metadata (`EnrichedData`).

```python
python 2_enrichParams.py
```

- **Input:** JSON files from `output/`.
- **Output:** Enriched JSON files saved to `enriched_output/`.

---

### 3. **Upload to MongoDB**
Uploads enriched compositions to a MongoDB collection.

```python
python 3_uploadToMongoDB.py
```

- **Environment Variable:** `MONGO_URI` (MongoDB connection string).
- **Input:** JSON files from `enriched_output/`.

---

## Key Concepts

### Hybrid Representation Model
- **Canonical JSON:** Full hierarchical structure for clinical context and semantic integrity.
- **Flattened Model (AQLSearchParams):** Optimized for MongoDB queries, indexed for fast retrieval.

### Dynamic API Design
A middleware layer translates openEHR AQL queries into MongoDB Query Language (MQL) operations, enabling:
- Fast query execution with indexed paths.
- Support for advanced searches (e.g., NLP, vector search).

---

## Configuration

The `config.json` file specifies:
- Schema file paths.
- MongoDB database and collection names.
- Configuration for generating synthetic data.

Example:

```json
{
  "ehrID_suffix": "ehr_",
  "ehrID_range": 1000,
  "num_documents": 100,
  "schemas": {
    "minimal_evaluation": "schemas/minimal_evaluation.json",
    "Corona_composition": "schemas/Corona_composition.json"
  },
  "database_name": "openEHR",
  "collection_name": "compositions"
}
```

---

## Prerequisites

- **Python** (>= 3.8)
- **MongoDB Atlas** or a local MongoDB instance
- Required Python packages:
  ```bash
  pip install faker pymongo bson
  ```

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License.
