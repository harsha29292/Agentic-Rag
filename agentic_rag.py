import os
from datetime import datetime
import requests
from dotenv import load_dotenv

from opensearch_client import get_opensearch_client
from patent_crew import run_patent_analysis
from patent_search_tools import hybrid_search, iterative_search, semantic_search, keyword_search

def display_menu():
    print("\n" + "=" * 60)
    print("  PATENT INNOVATION PREDICTOR - LITHIUM BATTERY TECHNOLOGY  ")
    print("=" * 60)
    print("1. Run complete patent trend analysis and forecasting")
    print("2. Search for specific patents")
    print("3. Iterative patent exploration")
    print("4. View system status")
    print("5. Exit")
    print("-" * 60)
    return input("Select an option (1-5): ")

def run_complete_analysis():
    print("\nRunning comprehensive patent analysis...")
    print("This may take several minutes depending on the data volume.")
    research_area = input("Enter research area (default: Lithium Battery): ")
    if not research_area:
        research_area = "Renewable Energy"
    model_name = input("Enter the Ollama model to use (default: deepseek-r1:1.5b): ")
    if not model_name:
        model_name = "deepseek-r1:1.5b"
    model_name = model_name.strip()

    # Preflight: print and check
    print(f">>> Using Ollama model: {repr(model_name)}")
    try:
        tags = requests.get("http://localhost:11434/api/tags", timeout=30).json()
        available = {m["name"] for m in tags.get("models", [])}
        print("Available models from Ollama:", available)
        if model_name not in available:
            print(f"Requested model '{model_name}' not found. Using fallback.")
            if "deepseek-r1:1.5b" in available:
                model_name = "deepseek-r1:1.5b"
            elif available:
                model_name = next(iter(available))
            print(f"Using fallback model: {model_name}")
        test_payload = {"model": model_name, "prompt": "ping"}
        test = requests.post("http://localhost:11434/api/generate", json=test_payload, timeout=60)
        print(f"Ollama model test status: {test.status_code}, Response: {test.text[:200]}")
        if test.status_code != 200:
            print("Model failed preflight test. Aborting analysis.")
            return
    except Exception as e:
        print(f"Error during Ollama preflight: {e}")
        return

    # One last test: print before agent call
    print(f"DEBUG: About to call run_patent_analysis with model_name={repr(model_name)}")
    test2 = requests.post("http://localhost:11434/api/generate", json={"model": model_name, "prompt": "is this working?"})
    print("DEBUG: Pre-agent API test", test2.status_code, test2.text[:200])

    print(f"\nAnalyzing patents for: {research_area}")
    print(f"Using Ollama model: {model_name}")
    print("Agents are now processing the data...\n")

    try:
        # Make sure your run_patent_analysis and its LLM/agent are actually receiving the model_name as-is!
        result = run_patent_analysis(research_area, model_name)
        if not isinstance(result, str):
            result = str(result)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"patent_analysis_{timestamp}.txt"
        with open(filename, "w") as f:
            f.write(result)
        print(f"\nAnalysis completed and saved to {filename}")
        print("\n" + "=" * 60)
        print("ANALYSIS SUMMARY")
        print("-" * 60)
        print(result[:500] + "...\n")
    except Exception as e:
        print(f"Error during analysis: {e}")

def search_patents():
    print("\nPATENT SEARCH")
    print("-" * 60)
    query = input("Enter search query: ")
    if not query:
        print("Search query cannot be empty.")
        return
    search_type = input("Select search type (1: Keyword, 2: Semantic, 3: Hybrid) [3]: ")
    if not search_type:
        search_type = "3"
    try:
        results = []
        if search_type == "1":
            results = keyword_search(query)
        elif search_type == "2":
            results = semantic_search(query)
        else:
            results = hybrid_search(query)
        print(f"\nFound {len(results)} results for '{query}':")
        print("-" * 60)
        for i, hit in enumerate(results):
            source = hit["_source"]
            print(f"{i+1}. {source['title']}")
            print(f"   Score: {hit['_score']}")
            print(f"   Date: {source.get('publication_date', 'N/A')}")
            print(f"   Patent ID: {source.get('patent_id', 'N/A')}")
            print(f"   Abstract: {source['abstract'][:150]}...")
            print("-" * 60)
    except Exception as e:
        print(f"Search error: {e}")

def iterative_exploration():
    print("\nITERATIVE PATENT EXPLORATION")
    print("-" * 60)
    query = input("Enter initial exploration query: ")
    if not query:
        print("Query cannot be empty.")
        return
    steps = input("Number of exploration steps (default: 3): ")
    try:
        steps = int(steps) if steps else 3
    except:
        steps = 3
    print(f"\nExploring patents related to '{query}' with {steps} refinement steps...")
    try:
        results = iterative_search(query, refinement_steps=steps)
        print(f"\nFound {len(results)} results through iterative exploration:")
        print("-" * 60)
        for i, hit in enumerate(results):
            source = hit["_source"]
            print(f"{i+1}. {source['title']}")
            print(f"   Date: {source.get('publication_date', 'N/A')}")
            print(f"   Patent ID: {source.get('patent_id', 'N/A')}")
            print(f"   Abstract: {source['abstract'][:150]}...")
            print("-" * 60)
    except Exception as e:
        print(f"Exploration error: {e}")

def check_system_status():
    print("\nSYSTEM STATUS")
    print("-" * 60)
    # OpenSearch connection
    try:
        client = get_opensearch_client("localhost", 9200)
        indices = client.cat.indices(format="json")
        print("✅ OpenSearch connection: OK")
        print(f"   Found {len(indices)} indices:")
        for index in indices:
            print(f"   - {index['index']}: {index['docs.count']} documents")
    except Exception as e:
        print(f"❌ OpenSearch connection: Failed - {e}")
    # Ollama connection
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            print("✅ Ollama connection: OK")
            print(
                f"   Available models: {', '.join([m.get('name', 'unknown') for m in models])}"
            )
        else:
            print(f"❌ Ollama connection: Failed (Status code: {response.status_code})")
    except Exception as e:
        print(f"❌ Ollama connection: Failed - {e}")
    # Embedding model connection
    try:
        from embedding import get_embedding
        sample = get_embedding("test")
        print(f"✅ Embedding model: OK (dimension: {len(sample)})")
    except Exception as e:
        print(f"❌ Embedding model: Failed - {e}")
    print("\nSystem is ready for operation.")

def main():
    load_dotenv()
    while True:
        choice = display_menu()
        if choice == "1":
            run_complete_analysis()
        elif choice == "2":
            search_patents()
        elif choice == "3":
            iterative_exploration()
        elif choice == "4":
            check_system_status()
        elif choice == "5":
            print("\nExiting Patent Innovation Predictor. Goodbye!")
            break
        else:
            print("\nInvalid option. Please select a number between 1 and 5.")
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
