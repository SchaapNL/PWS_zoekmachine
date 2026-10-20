import time

import json
import Utils
import LLM
import math

def test():
    start_time = time.time()

    urls = ["https://mountainscholar.org/items/c493e5b6-fc54-4ec8-bba1-bd5202765cf7",
            "https://research.google/pubs/ai-identity-and-ethical-governance-building-trust-in-high-stakes-systems/",
            "https://developers.google.com/search/docs/fundamentals/how-search-works",
            "https://www.tckpublishing.com/difference-between-retail-wholesale-and-distribution/",
            "https://en.wikipedia.org/wiki/Bob_the_Builder",
            "http://www.ijfrcsce.org/index.php/ijfrcsce/article/view/1529", # unique writers
            "https://zenodo.org/records/20091469", # weirdly read authors
            "https://aisel.aisnet.org/jmwais/vol2021/iss1/5/"]

    authors1 = get_authors(urls[7]) # changed this so parm is different

    if authors1 is not None:
        for author in authors1:
            print(author)
            print(get_author_score(author))

    else:
        print("No authors found. 1")

    print("-"*40)
    authors2 = get_authors(urls[3]) # changed this so parm is different

    if authors2 is not None:
        for author in authors2:
            print(author)
            print(get_author_score(author))
    else:
        print("No authors found. 2")

    print(f"took {time.time() - start_time} seconds")

def get_authors(url):
    site_info = Utils.get_website_information(url)

    if site_info is None or site_info["authors"] == "N/A":
        print("No authors found.")
        return None

    correct_authors = []
    for author in site_info["authors"].split(";"):
        author = Utils.remove_punctuation(author).split()

        # We won't be able to find the right person on first or last name alone
        if len(author) <= 1:
            print(f"{author} is to unspecific to lookup with any certainty at all")
            continue

        possible_authors = api_call_openalex(author)
        if possible_authors is None:
            return None

        # Gets the best matching authors and takes away the unneeded information.
        results = get_best_author_options(author, possible_authors)
        if len(results) == 0:
            continue

        correct_authors.append(LLM.get_correct_author(results, site_info))

    return correct_authors

def api_call_openalex(name):
    if type(name) != list:
        raise TypeError("name must be a list.")

    names = "+".join(name)
    base_url = "https://api.openalex.org/authors?search="

    with open('api_key.txt', 'r', encoding='utf-8') as file:
        api_key = file.read()
    file.close()

    api_info = Utils.get_text_from_URL(base_url + names + "&api_key=" + api_key)

    if api_info is None:
        return None

    return json.loads(api_info)

def get_best_author_options(full_name, data):
    results = data.get("results", [])
    best_matches = []
    for result in results:
        author_name = result.get("full_name")

        complete_match = True
        for name in full_name:
            if name not in author_name:
                complete_match = False

        if complete_match:
            best_matches.append(result)

    if best_matches is None:
        best_matches = results

    no_bloat_results = []
    i = 0
    for matches in best_matches:
        no_bloat_results.append(anti_bloat(matches, i))
        i += 1

    return no_bloat_results

def anti_bloat(author, id):
    if type(author) != dict:
        raise TypeError("a must be a dictionary.")

    stats = author.get("summary_stats") or {}

    main = author.get("display_name") or author.get("full_name")
    variants = []
    for name in (author.get("raw_author_names") or []) + (author.get("display_name_alternatives") or []):
        if name and name != main and name not in variants:
            variants.append(name)

    affiliations = []
    for affiliation in author.get("affiliations") or []:
        institution = affiliation.get("institution") or {}
        affiliations.append({
            "institution": institution.get("display_name"),
            "type": institution.get("type"),
            "year": years_range(affiliation.get("years") or []),
        })
    affiliations.sort(key=lambda x: x["year"], reverse=True)

    topics = []
    for t in author.get("topics") or []:
        topics.append({
            "topic": t.get("display_name"),
            "count": t.get("count"),
            "subfield": (t.get("subfield") or {}).get("display_name"),
            "field": (t.get("field") or {}).get("display_name"),
            "domain": (t.get("domain") or {}).get("display_name"),
        })

    concepts = []
    for c in author.get("x_concepts") or []:
        concepts.append({
            "concept": c.get("display_name"),
            "score": round(c.get("score", 0), 2),
        })

    per_year = [
        {
            "year": y.get("year"),
            "work_count": y.get("works_count"),
            "open_work_count": y.get("oa_works_count"),
            "citation_count": y.get("cited_by_count"),
        }
        for y in author.get("counts_by_year") or []
    ]
    per_year.sort(key=lambda x: x["year"])
    years_active = [y["year"] for y in per_year if y["work_count"]]

    profile = {
        "id": id,
        "name": main,
        "name_variants": variants,
        "work_count": author.get("works_count"),
        "citation_count": author.get("cited_by_count"),
        "h_index": stats.get("h_index"),
        "i10_index": stats.get("i10_index"),
        "2yr_mean_citedness": stats.get("2yr_mean_citedness"),
        "activity_during": years_range(years_active),
        "affiliations": affiliations,
        "topics": topics,
        "concepts": concepts,
        "per_year": per_year,
    }
    return delete_empty_objects(profile)

def years_range(years):
    if not years:
        return ""

    lowest = min(years)
    highest = max(years)
    if lowest == highest:
        return str(lowest)

    return f"{lowest}-{highest}"

def delete_empty_objects(json_thing):
    if isinstance(json_thing, dict):
        out = {}
        for (key, value) in json_thing.items():
            clean = delete_empty_objects(value)
            if clean not in (None, "", [], {}):
                out[key] = clean
        return out

    if isinstance(json_thing, list):
        out = []
        for item in json_thing:
            clean = delete_empty_objects(item)
            if clean not in (None, "", [], {}):
                out.append(clean)
        return out

    return json_thing

def get_author_score(author):
    if type(author) != dict:
        raise TypeError("a must be a dictionary.")

    score = math.log(math.log(author.get("h_index", 0) + math.e) * math.log(author.get("i10_index", 0) + math.e)
             * math.log10(author.get("citation_count", 0) + 10)) * 27
    return min(score, 100)

if "__main__" == __name__:
    test()