# ddxplus-parser
Simple parser for ddxplus designed for llm usage. The dataset is encoded in such a way that makes it difficult to use for LLMs. 

## Example

### Input Data

CSV data with patient information:

```csv
AGE,SEX,PATHOLOGY,EVIDENCES,INITIAL_EVIDENCE,DIFFERENTIAL_DIAGNOSIS
29,F,Anaphylaxis,"['E_12', 'E_42', ...]",E_51,"[['Anaphylaxis', 0.1127], ...]"
```

### Output Data

JSON file for each patient:

```json
{
    "sex": "F",
    "age": "29",
    "diagnosis": "Anaphylaxis",
    "pathology": {
        "name": "Anaphylaxis",
        "symptoms": ["Symptom 1", "Symptom 2"],
        "antecedents": ["Antecedent 1", "Antecedent 2"],
        "severity": 3
    },
    "condition": [
        {"question": "Question 1", "value": "Yes"},
        {"question": "Question 2", "value": "No"}
    ],
    "initial_condition": {"question": "Initial Question", "value": "Yes"},
    "differential_diagnosis": {
        "Disease 1": 0.1127,
        "Disease 2": 0.0879
    }
}
```


## Features

- Processes medical data from CSV files.
- Queries a GPT-4 model server to determine if a diagnosis is a respiratory disease.
- Generates detailed JSON files for each patient with respiratory disease diagnosis.

## Dataset Acquisition

To get the `ddxplus` dataset, follow these steps:

```bash
mkdir ddxplus
cd ddxplus
curl https://figshare.com/ndownloader/articles/22687585/versions/1 --output ddxplus.zip
unzip ddxplus.zip
rm ddxplus.zip

unzip release_test_patients.zip
rm release_test_patients.zip

unzip release_train_patients.zip
rm release_train_patients.zip

unzip release_validate_patients.zip
rm release_validate_patients.zip
```

## Setup

1. Ensure Python is installed.
2. Install required libraries: `json`, `csv`, `requests`, `time`.
3. If you want the LLM to check for RESPIRATORY conditions, set `SCAN_FOR_REPIRATORY_ONLY` to True and set up the server URL and model in the script.
4. Setup MAX_DECODE for the number of entries you want parsed

## Usage

Run the script with Python:

```bash
python ddxplus_parser.py
```
