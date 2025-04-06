import argparse
import requests
import re

def search_wikipedia(query, year_range=None):
    base_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query,
        "srlimit": 10,
        "origin": "*"
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    search_results = data.get("query", {}).get("search", [])

    if not search_results:
        print("No results found.")
        return []

    filtered_results = []
    for result in search_results:
        title = result["title"]
        page_id = result["pageid"]
        page_params = {
            "action": "query",
            "format": "json",
            "pageids": page_id,
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "origin": "*"
        }
        page_response = requests.get(base_url, params=page_params)
        page_data = page_response.json()
        page_content = page_data.get("query", {}).get("pages", {}).get(str(page_id), {}).get("extract", "")

        if year_range:
            year_match = re.search(r'(\d{4})', page_content)
            if year_match:
                year = int(year_match.group(1))
                if year < year_range[0] or year > year_range[1]:
                    continue

        filtered_results.append((title, page_content))

    return filtered_results
    

def generate_html(results, query, year_range=None):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Wikipedia Search Results</title>
        <style>
            body {{
                background-color: #232323;
                color: #bac1c9;
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
            }}
            h1, h2, h3 {{
                margin: 0;
                padding: 15px 5px 15px 0px;
                font-weight: normal;
                display: inline;
                background: linear-gradient(to bottom, #bac1c9 0%, #8f99a9 60%, #797d83 70%, #63676c 80%, #4d5156 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 0 5px rgba(186, 193, 201, 0.5), 0 0 10px rgba(186, 193, 201, 0.3), 0 0 15px rgba(186, 193, 201, 0.2);
            }}
            h1 {{
                font-size: 2em;
            }}
            h2 {{
                font-size: 1.5em;
            }}
            h3 {{
                font-size: 1.25em;
            }}
            p {{
                font-size: 1em;
                line-height: 1.6;
            }}
        </style>
    </head>
    <body>
        <h1>Search Results for "{query}"</h1><br><br>
    """
    if year_range:
        html_content += f"<h2>Year Range: {year_range[0]} - {year_range[1]}</h2><br><br>"
    for title, content in results:
        html_content += f"<h2>{title}</h2>"
        paragraphs = content.split('\n\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                html_content += f"<p>{paragraph.strip()}</p>"

    html_content += """
    </body>
    </html>
    """
    return html_content

def main():
    parser = argparse.ArgumentParser(description="Search Wikipedia and save results to an HTML file.")
    parser.add_argument('query', type=str, help="The search query.")
    parser.add_argument('year_range', type=str, nargs='?', help="The year range in the format 'start-year-end-year'.")

    args = parser.parse_args()

    query = args.query
    year_range = None
    if args.year_range:
        try:
            start_year, end_year = map(int, args.year_range.split('-'))
            year_range = (start_year, end_year)
        except ValueError:
            print("Invalid year range format. Use 'start-year-end-year'.")
            return

    results = search_wikipedia(query, year_range)
    if results:
        html_content = generate_html(results, query, year_range)
        with open('wikipedia_search_results.html', 'w', encoding='utf-8') as file:
            file.write(html_content)
        print("Results saved to wikipedia_search_results.html")

if __name__ == "__main__":
    main()
