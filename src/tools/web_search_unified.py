#!/usr/bin/env python
"""
Web Search Tool - Unified interface supporting both Exa AI and Perplexity

Priority order:
1. Exa AI (if EXA_API_KEY is set) - Better for research
2. Perplexity (if PERPLEXITY_API_KEY is set) - General search
"""

from datetime import datetime
import json
import os

# Try to import both clients
try:
    from exa_py import Exa
    EXA_AVAILABLE = True
except ImportError:
    EXA_AVAILABLE = False
    Exa = None

try:
    from perplexity import Perplexity
    PERPLEXITY_AVAILABLE = True
except ImportError:
    PERPLEXITY_AVAILABLE = False
    Perplexity = None


def web_search(
    query: str,
    output_dir: str | None = None,
    verbose: bool = False,
    prefer_provider: str | None = None,
) -> dict:
    """
    Perform network search using Exa AI or Perplexity API

    Automatically selects the best available provider:
    - Exa AI (preferred) if EXA_API_KEY is set
    - Perplexity if PERPLEXITY_API_KEY is set

    Args:
        query: Search query
        output_dir: Output directory (optional)
        verbose: Whether to print detailed information
        prefer_provider: Force specific provider ('exa' or 'perplexity')

    Returns:
        dict: Dictionary containing search results (compatible format)

    Raises:
        ImportError: If no search module is installed
        ValueError: If no API key is configured
        Exception: If API call fails
    """
    # Determine which provider to use
    exa_key = os.environ.get("EXA_API_KEY")
    perplexity_key = os.environ.get("PERPLEXITY_API_KEY")

    # Manual override
    if prefer_provider == "exa" and exa_key:
        provider = "exa"
    elif prefer_provider == "perplexity" and perplexity_key:
        provider = "perplexity"
    # Auto-detect (Exa preferred)
    elif exa_key and EXA_AVAILABLE:
        provider = "exa"
    elif perplexity_key and PERPLEXITY_AVAILABLE:
        provider = "perplexity"
    else:
        raise ValueError(
            "No web search API key configured. "
            "Please set EXA_API_KEY (recommended) or PERPLEXITY_API_KEY in .env file."
        )

    if verbose:
        print(f"Using web search provider: {provider}")

    # Route to appropriate provider
    if provider == "exa":
        return _web_search_exa(query, output_dir, verbose)
    else:
        return _web_search_perplexity(query, output_dir, verbose)


def _web_search_exa(
    query: str,
    output_dir: str | None = None,
    verbose: bool = False,
) -> dict:
    """Exa AI implementation"""
    if not EXA_AVAILABLE:
        raise ImportError("exa_py module not installed. Run: pip install exa-python")

    api_key = os.environ.get("EXA_API_KEY")
    if not api_key:
        raise ValueError("EXA_API_KEY not set")

    exa = Exa(api_key=api_key)

    try:
        search_results = exa.search_and_contents(
            query=query,
            numResults=10,
            useAutoprompt=True,
            text=True,
            livecrawl="always",
            category=["research paper", "blog", "wiki", "company"],
        )

        results = []
        for item in search_results.results:
            result = {
                "title": item.title,
                "url": item.url,
                "publishedDate": getattr(item, "publishedDate", None),
                "author": getattr(item, "author", None),
                "score": getattr(item, "score", None),
                "text": getattr(item, "text", "")[:1000],  # Limit text length
            }
            results.append(result)

        # Build answer from top results
        answer = ""
        if results:
            top_results = results[:3]
            answer = f"Found {len(results)} relevant results.\n\n"
            for r in top_results:
                if r.get("text"):
                    answer += f"**{r['title']}**\n{r['text'][:300]}...\n\n"

        # Build unified result dict
        result = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "provider": "exa",
            "answer": answer,
            "search_results": results,
            "citations": [
                {
                    "id": i + 1,
                    "reference": f"[{i + 1}]",
                    "url": r["url"],
                    "title": r["title"],
                    "snippet": r.get("text", "")[:200],
                }
                for i, r in enumerate(results)
            ],
        }

        # Save if needed
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(output_dir, f"search_exa_{timestamp}.json")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            result["result_file"] = output_path

        return result

    except Exception as e:
        raise Exception(f"Exa AI API call failed: {e!s}")


def _web_search_perplexity(
    query: str,
    output_dir: str | None = None,
    verbose: bool = False,
) -> dict:
    """Perplexity implementation"""
    if not PERPLEXITY_AVAILABLE:
        raise ImportError("perplexity module not installed")

    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        raise ValueError("PERPLEXITY_API_KEY not set")

    client = Perplexity(api_key=api_key)

    try:
        completion = client.chat.completions.create(
            model="sonar",
            messages=[
                {
                    "role": "system",
                    "content": "Provide detailed and accurate answers based on web search results.",
                },
                {"role": "user", "content": query},
            ],
        )

        answer = completion.choices[0].message.content

        result = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "provider": "perplexity",
            "answer": answer,
            "citations": [],
            "search_results": [],
        }

        # Extract citations
        if hasattr(completion, "citations") and completion.citations:
            for i, url in enumerate(completion.citations, 1):
                result["citations"].append({
                    "id": i,
                    "reference": f"[{i}]",
                    "url": url,
                })

        # Extract search results
        if hasattr(completion, "search_results") and completion.search_results:
            for item in completion.search_results:
                result["search_results"].append({
                    "title": item.title,
                    "url": item.url,
                    "snippet": getattr(item, "snippet", ""),
                })

        # Save if needed
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(output_dir, f"search_perplexity_{timestamp}.json")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            result["result_file"] = output_path

        return result

    except Exception as e:
        raise Exception(f"Perplexity API call failed: {e!s}")


if __name__ == "__main__":
    import sys

    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    # Test
    result = web_search("What is RAG in AI?", output_dir="./test_output", verbose=True)
    print(f"\n✅ Search completed using: {result['provider']}")
    print(f"Found {len(result.get('search_results', []))} results")
    if result.get("answer"):
        print(f"Answer preview: {result['answer'][:200]}...")
