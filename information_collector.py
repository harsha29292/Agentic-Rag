import os
import sys
import json
import requests
from dotenv import load_dotenv

# Ensure local imports work even if run from elsewhere
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from helper import get_data_from_serpapi, get_serpapi_url

load_dotenv()


def fetch_patent_data(query: str, dir_path: str) -> None:
    """
    Fetch patent data from SerpApi and save it to the specified directory.
    """
    api_key = os.getenv("SERP_API_KEY")
    if not api_key:
        raise ValueError("SERP_API_KEY environment variable is not set.")

    os.makedirs(dir_path, exist_ok=True)

    # Initial search to get organic_results with serpapi_link for details
    search_url = (
        f"https://serpapi.com/search?engine=google_patents&q={query}&api_key={api_key}"
    )
    try:
        resp = requests.get(search_url, timeout=30)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Initial search request failed: {e}") from e

    data = resp.json() if resp.content else {}
    organic = data.get("organic_results", [])
    if not organic:
        print("No organic_results found for this query; nothing to fetch.")
        return

    for idx, patent in enumerate(organic):
        if "serpapi_link" not in patent:
            print(f"Patent {idx} missing 'serpapi_link', skipping.")
            continue

        try:
            serpapi_url = get_serpapi_url(patent)
            detail = get_data_from_serpapi(serpapi_url)
        except Exception as e:
            print(f"Error fetching detail for patent {idx}: {e}")
            continue

        if not detail:
            print(f"Empty details for patent {idx}, skipping.")
            continue

        # Save detail JSON
        with open(os.path.join(dir_path, f"patent_data_{idx}.json"), "w", encoding="utf-8") as f:
            json.dump(detail, f, indent=2, ensure_ascii=False)

        # Follow citations if present
        citations = (detail.get("patent_citations") or {}).get("original") or []
        if not isinstance(citations, list):
            # Some responses might return a dict; normalize to list of items
            citations = list(citations)  # best-effort fallback

        for idx2, citation in enumerate(citations):
            serpapi_url2 = (citation or {}).get("serpapi_link")
            if not serpapi_url2:
                print(f"No SERPAPI link found for citation {idx2}, skipping.")
                continue

            try:
                citation_data = get_data_from_serpapi(serpapi_url2)
            except Exception as e:
                print(f"Error fetching citation {idx2} for patent {idx}: {e}")
                continue

            if not citation_data:
                print(f"No data returned for citation {idx2}, skipping.")
                continue

            with open(os.path.join(dir_path, f"citation_{idx}_{idx2}.json"), "w", encoding="utf-8") as f:
                json.dump(citation_data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    query = input("Enter the search query for patents: ").strip()
    dir_path = input("Enter the directory path to save results: ").strip()
    try:
        fetch_patent_data(query, dir_path)
        print(f"Patent data fetched and saved to '{dir_path}'")
    except Exception as e:
        print(f"Error: {e}")
