import json
import csv
import requests
import time

# Directory where the dataset is stored
DATA_DIRECTORY = 'data/ddxplus/'
OUTPUT_DIRECTORY = "examples_ddxplus/"
SCAN_FOR_REPIRATORY_ONLY = False
SERVER_URL = "http://127.0.0.1:5000/chat"
MODEL = "gpt-4"
MAX_DECODE = 50


def query_server(text):
    messages = [{"role": "user", "content": f"Given '{text}', is the diagnosis a respiratory disease? give the answer YES or NO"}]
    payload = {
            "messages": messages,
            "model_type": MODEL,
        }
    response = requests.post(SERVER_URL, json=payload)

    return response.json()


def load_json(file_path):
    with open(DATA_DIRECTORY + file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def decode_evidence(evidence_code, evidences_data):
    parts = evidence_code.split('_@_')
    base_evidence_code = parts[0]
    evidence_value = parts[1] if len(parts) > 1 else None
    evidence = evidences_data.get(base_evidence_code, {})

    if evidence['data_type'] == 'B':
        return {"question": evidence['question_en'], "value": "Yes" if evidence_value is None else "No"}
    elif evidence['data_type'] in ['C', 'M']:
        # If evidence_value is a digit, use it directly as the value
        if evidence_value is not None and evidence_value.isdigit():
            return {"question": evidence['question_en'], "value": evidence_value}
        else:
            value_meaning = evidence['value_meaning'].get(evidence_value, {})
            return {"question": evidence['question_en'], "value": value_meaning.get('en', '')}


def decode_evidence_value(evidence_code, evidence_data):
    if evidence_data['data_type'] == 'N':
        return str(evidence_code)
    elif evidence_data['data_type'] in ['C', 'M']:
        value_meaning = evidence_data['value_meaning'].get(evidence_code, {})
        return value_meaning.get('en', '')
    else:
        return "Yes" if evidence_code else "No"

def decode_pathology(pathology_code, conditions_data, evidences_data):
    pathology = conditions_data.get(pathology_code, {})
    decoded_symptoms = []
    decoded_antecedents = []

    for symptom in pathology.get('symptoms', []):
        evidence = evidences_data.get(symptom, {})
        symptom_name = evidence.get('question_en', 'Unknown Symptom')
        decoded_symptoms.append(symptom_name)

    for antecedent in pathology.get('antecedents', []):
        evidence = evidences_data.get(antecedent, {})
        antecedent_name = evidence.get('question_en', 'Unknown Antecedent')
        decoded_antecedents.append(antecedent_name)

    return {
        "name": pathology.get('cond-name-eng', ''),
        "symptoms": decoded_symptoms,
        "antecedents": decoded_antecedents,
        "severity": pathology.get('severity', '')
    }

def process_patient(patient, evidences_data, conditions_data):
    decoded_pathology = decode_pathology(patient["PATHOLOGY"], conditions_data, evidences_data)
    decoded_patient = {
        "sex": patient["SEX"],
        "age": patient["AGE"],
        "diagnosis": decoded_pathology["name"],
        "pathology": decoded_pathology,
        "condition": [],
        "initial_condition": decode_evidence(patient["INITIAL_EVIDENCE"], evidences_data),
        "differential_diagnosis": {}
    }

    for evidence in patient["EVIDENCES"]:
        decoded_patient["condition"].append(decode_evidence(evidence, evidences_data))

    for diagnosis in eval(patient["DIFFERENTIAL_DIAGNOSIS"]):
        decoded_patient["differential_diagnosis"][decode_pathology(diagnosis[0], conditions_data, evidences_data)["name"]] = diagnosis[1]

    return decoded_patient

def count_total_rows(file_path):
    total_rows = 0
    with open(file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        next(csv_reader, None)  # Skip the header row
        for _ in csv_reader:
            total_rows += 1
    return total_rows

def main(max_decode):
    evidences_data = load_json('release_evidences.json')
    conditions_data = load_json('release_conditions.json')
    patient_data_file = DATA_DIRECTORY + 'release_validate_patients' #using the validation set bc it's smaller
    output_file = OUTPUT_DIRECTORY + '_respiratory_scanner_ddxplus_output.txt'

    patients = []

    with open(patient_data_file, 'r', encoding='utf-8') as file, open(output_file, 'w') as out_f:
        csv_reader = csv.DictReader(file)
        idx = 0
        for idx,row in enumerate(csv_reader):
            time.sleep(0.1)
            if idx >= max_decode:
                break
            row["EVIDENCES"] = row["EVIDENCES"].strip("[]").replace("'", "").split(", ")
            print (f"\n\n{row}\n\n")
            patient = process_patient(row, evidences_data, conditions_data)
            patients.append(patient)

            save_file = True
            if SCAN_FOR_REPIRATORY_ONLY:
                #requires you to hookup query_server with an LLM

                text = {"condition":patient["condition"], "diagnosis":patient["diagnosis"]}
                response = query_server(text)

                out_f.write(f"Text: {text}\n")
                out_f.write(f"Answer: {response}\n\n")

                #this is a resperatory
                if response['text'] != "YES":
                    save_file = False
            
            if save_file:
                output_file_machine = f"{OUTPUT_DIRECTORY}/transcript_{idx}.machine.txt"
                with open(output_file_machine, 'w') as out_json_f:
                    json.dump(patient, out_json_f, indent = 4)



        print (f"{idx + 1} / {count_total_rows(patient_data_file)} total rows processed")



if __name__ == "__main__":
    main(MAX_DECODE)
