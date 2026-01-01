#!/usr/bin/env python
"""
Web Search Tool - Network search using Exa AI API
Enhanced version with better search results for research scenarios
"""

from datetime import datetime
import json
import os

try:
    from exa_py import Exa

    EXA_AVAILABLE = True
except ImportError:
    EXA_AVAILABLE = False
    Exa = None


def web_search_exa(
    query: str,
    output_dir: str | None = None,
    verbose: bool = False,
    num_results: int = 10,
    use_autoprompt: bool = True,
) -> dict:
    """
    Perform network search using Exa AI API and return results

    Exa AI is optimized for AI research with:
    - Better semantic understanding
    - Higher quality results
    - Automatic query optimization

    Args:
        query: Search query
        output_dir: Output directory (optional)
        verbose: Whether to print detailed information
        num_results: Number of results to return (default: 10)
        use_autoprompt: Use Exa's automatic query optimization (default: True)

    Returns:
        dict: Dictionary containing search results
            {
                "query": str,
                "answer": str,  # Simplified answer
                "results": list,  # Detailed search results
                "result_file": str (if saved)
            }

    Raises:
        ImportError: If exa_py module is not installed
        ValueError: If EXA_API_KEY environment variable is not set
        Exception: If API call fails
    """
    # Check if exa_py module is available
    if not EXA_AVAILABLE:
        raise ImportError(
            "exa_py module is not installed. Install with: pip install exa-python\n"
            "Note: This is an optional feature."
        )

    # Check API key
    api_key = os.environ.get("EXA_API_KEY")
    if not api_key:
        raise ValueError("EXA_API_KEY environment variable is not set")

    # Initialize client
    exa = Exa(api_key=api_key)

    try:
        # Perform search with Exa's advanced options
        search_results = exa.search_and_contents(
            query=query,
            numResults=num_results,
            useAutoprompt=use_autoprompt,  # Automatically optimize the query
            text=True,  # Return full text content
            livecrawl="always",  # Always fetch fresh content
            category=["research paper", "blog", "wiki", "company"],
        )

        # Extract results
        results = []
        for item in search_results.results:
            result = {
                "title": item.title,
                "url": item.url,
                "publishedDate": getattr(item, "publishedDate", None),
                "author": getattr(item, "author", None),
                "score": getattr(item, "score", None),
                "text": getattr(item, "text", ""),
                "highlight": getattr(item, "highlight", ""),
            }
            results.append(result)

        # Build simplified answer from results
        if results:
            top_results = results[:3]
            answer_parts = []
            for r in top_results:
                if r.get("text"):
                    # Extract first meaningful paragraph
                    text = r["text"][:500]
                    answer_parts.append(f"From {r['title']}:\n{text}")

            answer = "\n\n".join(answer_parts) if answer_parts else "Search completed successfully. See detailed results below."
        else:
            answer = "No results found."

        # Build result dictionary (compatible with Perplexity format)
        result = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "provider": "exa",
            "model": "exa-search-v1",
            "answer": answer,
            "search_results": results,
            "citations": [
                {
                    "id": i + 1,
                    "reference": f"[{i + 1}]",
                    "url": r["url"],
                    "title": r["title"],
                    "snippet": r.get("text", "")[:200] + "..." if r.get("text") else "",
                }
                for i, r in enumerate(results)
            ],
            "usage": {
                "num_results": len(results),
                "autoprompt_enabled": use_autoprompt,
            },
        }

        # Save results if output directory provided
        result_file = None
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"search_exa_{timestamp}.json"
            output_path = os.path.join(output_dir, output_filename)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            result_file = output_path

            if verbose:
                print(f"Search results saved to: {output_path}")

        if result_file:
            result["result_file"] = result_file

        if verbose:
            print(f"Query: {query}")
            print(f"Found {len(results)} results")
            print(f"Answer: {answer[:200]}..." if len(answer) > 200 else answer)

        return result

    except Exception as e:
        raise Exception(f"Exa AI API call failed: {e!s}")


if __name__ == "__main__":
    import sys

    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    # Test
    result = web_search_exa("What is a diffusion model?", output_dir="./test_output", verbose=True)
    print("\nSearch completed!")
    print(f"Query: {result['query']}")
    print(f"Found {result['usage']['num_results']} results")
    print(f"Answer: {result['answer'][:300]}...")
