import time
import Utils
from datetime import datetime

def get_rdap_dates(url_or_host):
    domain = Utils.get_domain(url_or_host)

    url = f"https://rdap.org/domain/{domain}"
    http_header = ["Accept: application/rdap+json"]

    data = Utils.api_call(url, http_header)

    events = {event.get("eventAction"): event.get("eventDate") for event in data.get("events", [])}
    registration = events.get("registration")
    last_changed = events.get("last changed")

    if not isinstance(registration, str) or not isinstance(last_changed, str):
        return None

    return {
        "registration": datetime.fromisoformat(registration).timestamp(),
        "last_changed": datetime.fromisoformat(last_changed).timestamp()
    }

def test():
    start_time = time.time()

    site = "https://en.wikipedia.org/wiki/Bob_the_Builder"

    site_info = get_rdap_dates(site)
    print(site_info)

    print(f"The search took {time.time()-start_time} seconds")

if __name__ == '__main__':
    test()