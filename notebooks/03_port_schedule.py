import re, time, pathlib, requests, pandas as pd
from bs4 import BeautifulSoup

URL = "https://www.crew-center.com/sydney-australia-cruise-ship-schedule-{y}"
YEARS = [2018, 2019, 2020, 2022, 2023]
CACHE = pathlib.Path("data/raw/crewcenter"); CACHE.mkdir(parents=True, exist_ok=True)

def fetch(year):
    """Cache to disk so you only hit the site once per year."""
    f = CACHE / f"{year}.html"
    if not f.exists():
        r = requests.get(URL.format(y=year), timeout=30,
                         headers={"User-Agent": "sydney-tour-forecast/0.1 (you@example.com)"})
        r.raise_for_status()
        f.write_text(r.text, encoding="utf-8")
        time.sleep(2)
    return f.read_text(encoding="utf-8")

def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for tr in soup.select("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
        if len(cells) >= 4 and re.match(r"\d{1,2}-[A-Za-z]{3}-\d{4}", cells[1]):
            rows.append(cells[:5])
    return pd.DataFrame(rows, columns=["port", "date", "ship", "line", "times"])

df = pd.concat([parse(fetch(y)) for y in YEARS], ignore_index=True)
df["call_date"] = pd.to_datetime(df["date"], format="%d-%b-%Y")

print(df)