import uuid
from datetime import datetime

def generate_fhir_bundle(session_id, profile_data, recommendation, language="en"):
    now = datetime.utcnow().isoformat()
    patient_id = str(uuid.uuid4())

    return {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": patient_id,
                    "language": language,
                    "extension": [
                        {"url": "http://hl7.org/fhir/StructureDefinition/patient-appearance", "valueString": profile_data["age_appearance"]}
                    ]
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": str(uuid.uuid4()),
                    "subject": {"reference": f"Patient/{patient_id}"},
                    "code": {"text": profile_data["symptoms"]},
                    "recordedDate": now
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": str(uuid.uuid4()),
                    "subject": {"reference": f"Patient/{patient_id}"},
                    "note": [
                        {"text": f"History: {profile_data['history']}, Duration: {profile_data['duration']}"}
                    ]
                }
            },
            {
                "resource": {
                    "resourceType": "MedicationRequest",
                    "id": str(uuid.uuid4()),
                    "status": "active",
                    "intent": "proposal",
                    "medicationCodeableConcept": {"text": recommendation["drug"]},
                    "subject": {"reference": f"Patient/{patient_id}"},
                    "note": [{"text": f"Confidence: {recommendation['confidence']}%, Side effects: {recommendation['side_effects']}"}]
                }
            }
        ]
    }
