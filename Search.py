import DatabaseManager as db
import Utils
import time
import math

base_author_score = 20
weights = {
        "match": 10,
        'authors': 4,
        'site_age': 2,
        'site_update': 4,
        'link': 4,
        'back_link': 4
}

def search(query):
    con = db.connect_to_database('zoekmachine.db')

    query = Utils.remove_punctuation(query)
    query = Utils.stem_words(query)

    raw_sites_info = db.get_website_score(con, query)

    if raw_sites_info is None or len(raw_sites_info) == 0:
        return []

    max_match = raw_sites_info[0][1]

    sites_info = []
    for site in raw_sites_info:
        authors = []
        if site[2] is not None:
            for author in site[2].split(","):
                author_score = author.split(": ")
                author_score[1] = "not found" if author_score[1] == -1 else author_score[1]

                authors.append({'author': author_score[0], 'score': author_score[1]})
        else:
            authors.append({'author': "not found", 'score': "N/A"})

        info = {'link': site[0], 'authors': authors, 'title': site[9],
                'site_age': site[3] or "N/A", 'site_update': site[4] or "N/A",
                'in_links': site[5] or 0, 'out_links': site[6] or 0,
                'in_back_links': site[7] or 0, 'out_back_links': site[8] or 0}

        scores = {'final_score': None,
                  "match": site[1] / max_match * 100,
                  'authors': get_authors_score(info['authors']),
                  'site_age': get_site_age_score(info['site_age']),
                  'site_update': get_site_update_score(info['site_update']),
                  'link': get_link_score(int(info['in_links']), int(info['out_links'])),
                  'back_link': get_link_score(int(info['in_back_links']), int(info['out_back_links']))
                  }

        final_score = 0
        for weight in weights.keys():
            final_score += weights[weight] * scores[weight]

        scores['final_score'] = final_score / sum(weights.values())

        sites_info.append({'info': info, 'scores': scores})

    db.close_connection(con)

    sites_info.sort(key=lambda x: x['scores']['final_score'], reverse=True)
    return sites_info

def get_authors_score(authors):
    scores = []
    for author in authors:
        score = get_author_score(author)
        scores.append(score)

    while None in scores:
        scores.remove(None)

    return sum(scores) / len(scores) if scores else base_author_score

def get_author_score(author):
    if author['author'] == "not found":
        return 0
    if author['score'] == "N/A" or author['score'] == -1:
        return None
    else:
        return author['score'] or base_author_score

def get_site_age_score(site_age):
    if site_age == "N/A":
        return 0

    seconds_old = time.time() - site_age
    years_old = seconds_old / (60*60*24*365)
    return min(20*math.log(1+5.85*years_old), 100)

def get_site_update_score(site_update):
    if site_update == "N/A":
        return 0

    seconds_old = time.time() - site_update
    years_old = seconds_old / (60*60*24*365)
    return min(100*math.exp(-0.2*years_old), 100)

def get_link_score(in_links, out_links):
    if out_links == 0 and in_links == 0:
        return 0

    total = out_links + min(math.log(1 + in_links, 2), 0,15*out_links)
    return min(30*math.log(1+0.5*total), 100)

def main():
    start_time = time.time()

    query = 'bob'
    search_results = search(query)[0].get('info').get('title')

    if search_results is None or len(search_results) == 0:
        print('no results')
    else:
        print(search_results)

    print('The search took %f' % (time.time()- start_time))

if __name__ == '__main__':
    main()
