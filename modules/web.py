import requests
from urllib.parse import quote


class NexusWeb:
    def __init__(self):
        self.name = "NEXUS WEB"

    def search(self, query):
        if not query or not query.strip():
            return {"status": "error", "message": "Пустой запрос"}

        try:
            url = "https://ru.wikipedia.org/w/api.php"
            response = requests.get(
                url,
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": query,
                    "format": "json",
                    "utf8": 1
                },
                headers={"User-Agent": "NEXUS-AI/3.0"},
                timeout=20
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("query", {}).get("search", [])[:5]:
                results.append({
                    "title": item["title"],
                    "text": item["snippet"].replace("<span class=\"searchmatch\">", "").replace("</span>", ""),
                    "url": "https://ru.wikipedia.org/wiki/" + quote(item["title"].replace(" ", "_"))
                })

            return {
                "module": self.name,
                "query": query,
                "status": "success" if results else "no_results",
                "results": results
            }

        except requests.RequestException as error:
            return {"status": "error", "message": str(error)}
