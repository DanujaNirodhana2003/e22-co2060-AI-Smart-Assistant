import requests

def check_ollama():
    print("Checking Ollama status...")
    try:
        # Check if running
        r = requests.get("http://localhost:11434/")
        print(f"Root endpoint status: {r.status_code}")
        print(f"Root text: {r.text}")

        # Check models
        r = requests.get("http://localhost:11434/api/tags")
        if r.status_code == 200:
            models = r.json().get('models', [])
            print("\nAvailable models:")
            for m in models:
                print(f" - {m['name']}")
        else:
            print(f"Failed to list models: {r.status_code} {r.text}")

    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    check_ollama()
