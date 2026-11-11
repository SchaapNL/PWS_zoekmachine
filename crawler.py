import AuthorModule
import DatabaseManager as db
import DomainInfoModule

import time
import Utils
import sys

def handle_links(links, url_root, con):
    for link in links:
        if link is None:
            continue

        if not 'https://' in link and not 'http://' in link:
            if link[:1] == "/":
                links[links.index(link)] = url_root + link
            else:
                links[links.index(link)] = None

    while None in links:
        links.remove(None)

    links.sort()
    last_robot_txt = {"root": str, "robots.txt": list}
    for link in links:
        if 'wikipedia.org' in link and 'en.wikipedia.org' not in link:
            links[links.index(link)] = None
            continue

        root_url = Utils.get_root_url(link)
        if root_url == last_robot_txt['root']:
            disallowed_urls = last_robot_txt['robots.txt']
        else:
            disallowed_urls = get_disallowed_urls(root_url)
            last_robot_txt = {"root": root_url, "robots.txt": disallowed_urls}

        for disallowed_url in disallowed_urls:
            if link.startswith(disallowed_url):
                links[links.index(link)] = None
                continue

    while None in links:
        links.remove(None)

    for link in links:
        if db.get_website_id(con, link) is None:
            db.insert_website(con, link)

def link_sites(con, original_site_id, original_site, links):
    for link in links:
        if link is None:
            continue

        if not 'https://' in link and not 'http://' in link:
            if link[:1] == "/":
                links[links.index(link)] = Utils.get_root_url(original_site) + link
            else:
                links[links.index(link)] = None

    print(links)

    website_ids = db.get_website_ids_from_links(con, links)

    print(website_ids)

    original_domain = Utils.get_domain(original_site)
    websites = [(site[0], Utils.get_domain(site[1]) == original_domain) for site in website_ids]

    db.insert_website_links(con, original_site_id, websites)

def get_disallowed_urls(site):
    root_url = Utils.get_root_url(site)
    robots_txt = Utils.get_website_information(root_url + "/robots.txt")

    if robots_txt is None:
        return []

    robots_txt = robots_txt.get("text")
    correct_user_agent = False
    disallowed = []
    for line in robots_txt.split("\n"):
        if line is None: continue

        if line.startswith("User-agent: "):
            if line[len("User-agent: ") :] == "*" or line[len("User-agent: ") :] == "moffel":
                correct_user_agent = True

            else:
                correct_user_agent = False

        if correct_user_agent:
            if line.startswith("Disallow: "):
                disallowed.append(root_url + line[len("Disallow: "):])

    return disallowed

def main():
    max_scrape_amount = 100
    scrape_limit = False
    author_via_api = False
    scrape = False
    update_domains = True

    start_time = time.time()

    con = db.connect_to_database('zoekmachine.db')
    db.create_tables(con)

    if scrape:
        sites = db.get_websites_to_crawl(con)
        if sites is None or len(sites) <= 0:
            start_site = 'https://en.wikipedia.org/wiki/Bob_the_Builder'

            if db.get_website_id(con, start_site) is None:
                db.insert_website(con, start_site)
                sites = [[db.get_website_id(con, start_site), start_site]]

        i = 0

        while i < max_scrape_amount or not scrape_limit:
            i = i + 1

            if len(sites) <= 0:
                sites = get_websites_to_crawl(con)

            site_time = time.time()
            site = sites.pop()

            scrape_site(site[0], site[1], con)

            print(f"{i} - {site[1]} took {time.time() - site_time} seconds to scrape.")

        print(f"Crawled {max_scrape_amount} websites, in {time.time() - start_time} seconds.")

    if author_via_api:
        for author in db.get_unrated_authors(con):
            site = db.get_website_url(con, author[0])

            authors = AuthorModule.get_authors(site)
            if authors is not None:
                for author_info in authors:

                    score = AuthorModule.get_author_score(author_info) if author_info is not None else -1
                    db.set_author_score(con, author[0], author[1], float(score))

    if update_domains:
        domains = db.get_domains_to_update(con)
        for domain in domains:
            last_crawl = time.time()
            domain_info = DomainInfoModule.get_rdap_dates(domain[1])

            if domain_info is None:
                db.update_domain_last_updated(con, domain[0])
            else:
                db.update_domain_info(con, domain[0],
                                      int(domain_info.get("registration")),
                                      int(domain_info.get("last_changed"))
                                      )

            crawl_time = time.time() - last_crawl
            if crawl_time < 1:
                time.sleep(1.5-crawl_time)


    print(f"{time.time() - start_time} seconds.")

    db.close_connection(con)


def scrape_site(website_id, url, con):
    db.clear_word_freq(con, website_id)
    db.clear_author(con, website_id)

    site_info = Utils.get_website_information(url)

    if site_info is None:
        db.update_last_crawled(con, website_id, int(time.time()))
        return

    if site_info.get("text") is not None:
        text = Utils.remove_punctuation(site_info.get("text"))
        word_freq_dict = Utils.stem_freq_words(text)

        db.insert_word_frequencies(con, website_id, word_freq_dict)
        db.insert_website_size(con, website_id, len(text))

    if site_info.get("authors") is not None:
        for author in site_info.get("authors").split(";"):
            db.insert_author(con, website_id, author, None)

    if site_info.get("title") is not None:
        db.insert_title(con, website_id, site_info.get("title"))

    if site_info.get("date") is not None:
        db.insert_website_date(con, website_id, Utils.timestamp_to_epoch(site_info.get("date")))

    link_sites(con, website_id, url, site_info.get("links"))

    domain = Utils.get_domain(url)
    domain_id = db.get_or_create_domain_id(con, domain)
    db.update_website_domain(con, website_id, domain_id)

    db.update_last_crawled(con, website_id, int(time.time()))

def get_websites_to_crawl(con):
    sites = db.get_websites_to_crawl(con)

    if len(sites) > 0:
        return sites

    website = db.get_site_to_scan_links(con)

    if website is not None:
        site_info = Utils.get_website_information(website[1])

        if site_info is None:
            db.update_last_scanned_sites(con, website[0], int(time.time()))
            return get_websites_to_crawl(con)

        root_url = Utils.get_root_url(website[1])
        links = site_info.get("links")
        handle_links(links, root_url, con)

        db.update_last_scanned_sites(con, website[0], int(time.time()))

        return get_websites_to_crawl(con)

    else:
        sys.exit("All websites were crawled successfully")

if __name__ == '__main__':
    main()
