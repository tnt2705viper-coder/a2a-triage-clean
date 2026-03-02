import requests

def ask_ollama(prompt):
    url = "http://localhost:11434/api/generate"

    payload = {
        "model": "phi3:mini",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 100
        }
    }

    response = requests.post(url, json=payload)
    return response.json()["response"]


def triage():
    print("=== ED TRIAGE ASSISTANT (OFFLINE) ===")
    symptoms = input("Enter patient symptoms: ")
    vitals = input("Enter vital signs (BP, HR, SpO2, RR): ")

    prompt = f"""
ED triage.
Return only:
LEVEL: RED / ORANGE / GREEN
REASON: max 2 short lines.

Symptoms: {symptoms}
Vitals: {vitals}
"""

    result = ask_ollama(prompt)

    print("\n--- TRIAGE RESULT ---")
    print(result)


if __name__ == "__main__":
    triage()