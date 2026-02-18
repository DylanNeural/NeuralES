import requests
import json

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBuZXVyYWxlcy5jb20iLCJ1c2VyX2lkIjoxLCJleHAiOjE3NzEzNjQ2OTh9.nsL4eEyKSSOgN-UAspIXqUqYGGYqZdMpk9tfsi46PC0"

payload = {
    "marque_modele": "NeuralES Pro Test",
    "serial_number": "SN-TEST-001",
    "connection_type": "usb",
    "etat": "actif"
}

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

resp = requests.post("http://localhost:8001/devices", json=payload, headers=headers)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text}")
