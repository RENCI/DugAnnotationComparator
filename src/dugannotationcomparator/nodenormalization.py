import requests

def get_normalized_concept_ids(ids: set[str]) -> dict:
    url = 'https://nodenormalization-sri.renci.org/get_normalized_nodes'
    req_params = {
                "curies": list(ids),
                "conflate": True,
                "description": True,
                "drug_chemical_conflate": False
            }

    response = requests.post(url, json=req_params, timeout=30)
    json_response = response.json()
    return json_response