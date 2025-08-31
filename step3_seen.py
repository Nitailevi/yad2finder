import json
from pathlib import Path

STORE = Path("seen.json")

def load_seen():
    """uploads the list of seen ads from a file"""
    if STORE.exists():
        try:
            return set(json.loads(STORE.read_text(encoding="utf-8")))
        except:
            return set()
    return set()

def save_seen(seen):
    """ saves the list of seen ads to a file"""
    STORE.write_text(
        json.dumps(sorted(list(seen)), ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

if __name__ == "__main__":
    #example usage
    seen = load_seen()
    print("seen", seen)

    found_now = {"https://www.yad2.co.il/item/aaa", "https://www.yad2.co.il/item/bbb"}
    new_ads = [u for u in found_now if u not in seen]

    print(" new adds:", new_ads)

    # update seen
    seen |= set(new_ads)
    save_seen(seen)
