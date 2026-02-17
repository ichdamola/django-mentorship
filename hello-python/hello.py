import requests

def main():
    response = requests.get("https://api.github.com")
    print(f"GitHub API Status: {response.status_code}")
    print(f"Rate Limit: {response.headers.get('X-RateLimit-Limit')}")

if __name__ == "__main__":
    main()
    
