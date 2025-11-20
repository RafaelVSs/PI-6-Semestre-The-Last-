import requests

url = "http://localhost:3030/api/v1/refuels/"
token = input("Token: ")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

payload = {}

r = requests.post(url, json=payload, headers=headers)

print("Status:", r.status_code)
print("Resposta:", r.text)
print("== HEADERS QUE FORAM ENVIADOS ==")
print(r.request.headers)
