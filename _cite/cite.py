"""
cite process to convert sources and metasources into full citations
"""

import traceback
from importlib import import_module
from pathlib import Path
from dotenv import load_dotenv
from urllib.request import Request, urlopen
from util import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup


# load environment variables
load_dotenv()


# error flag
error = False

# output citations file
output_file = "_data/citations.yaml"


log()

log("Compiling sources")

# compiled list of sources
sources = []

# in-order list of plugins to run
plugins = ["google-scholar", "pubmed", "orcid", "sources"]

# loop through plugins
for plugin in plugins:
    # convert into path object
    plugin = Path(f"plugins/{plugin}.py")

    log(f"Running {plugin.stem} plugin")

    # get all data files to process with current plugin
    files = Path.cwd().glob(f"_data/{plugin.stem}*.*")
    files = list(filter(lambda p: p.suffix in [".yaml", ".yml", ".json"], files))

    log(f"Found {len(files)} {plugin.stem}* data file(s)", 1)

    # loop through data files
    for file in files:
        log(f"Processing data file {file.name}", 1)

        # load data from file
        try:
            data = load_data(file)
            # check if file in correct format
            if not list_of_dicts(data):
                raise Exception("File not a list of dicts")
        except Exception as e:
            log(e, 2, "ERROR")
            error = True
            continue

        # loop through data entries
        for index, entry in enumerate(data):
            log(f"Processing entry {index + 1} of {len(data)}, {label(entry)}", 2)

            # run plugin on data entry to expand into multiple sources
            try:
                expanded = import_module(f"plugins.{plugin.stem}").main(entry)
                # check that plugin returned correct format
                if not list_of_dicts(expanded):
                    raise Exception("Plugin didn't return list of dicts")
            # catch any plugin error
            except Exception as e:
                # log detailed pre-formatted/colored trace
                print(traceback.format_exc())
                # log high-level error
                log(e, 3, "ERROR")
                error = True
                continue

            # loop through sources
            for source in expanded:
                if plugin.stem != "sources":
                    log(label(source), 3)

                # include meta info about source
                source["plugin"] = plugin.name
                source["file"] = file.name

                # add source to compiled list
                sources.append(source)

            if plugin.stem != "sources":
                log(f"{len(expanded)} source(s)", 3)


log("Merging sources by id")

# merge sources with matching (non-blank) ids
for a in range(0, len(sources)):
    a_id = get_safe(sources, f"{a}.id", "")
    if not a_id:
        continue
    for b in range(a + 1, len(sources)):
        b_id = get_safe(sources, f"{b}.id", "")
        if b_id == a_id:
            log(f"Found duplicate {b_id}", 2)
            sources[a].update(sources[b])
            sources[b] = {}
sources = [entry for entry in sources if entry]


log(f"{len(sources)} total source(s) to cite")


log()

log("Generating citations")

def fetch_thumbnail_from_doi(doi):
    """
    Fetch a thumbnail image URL for a given DOI by searching for figures or
    images in the associated metadata using Selenium + local ChromeDriver.
    """
    try:
        article_url = "https://doi.org/" + doi

        # Set up Selenium options for Chrome
        options = Options()
        # Example: run headless, or remove "--headless" if using Xvfb
        # options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Launch a local Chrome instance (not Remote)
        driver = webdriver.Chrome(options=options)

        # Load the article URL
        driver.get(article_url)
        driver.implicitly_wait(10)

        # Try to find meta tags with property='og:image'
        meta_tags = driver.find_elements(By.CSS_SELECTOR, "meta[property='og:image']")
        vals = [tag.get_attribute("content") for tag in meta_tags]

        # If Selenium didn’t find any images, fallback to requests + BeautifulSoup
        if not vals:
            response = requests.get(article_url, allow_redirects=True)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            meta_tag = soup.find("meta", property="og:image")
            vals = [meta_tag['content']] if meta_tag else []

        if not vals:
            # first image in the article
            img_tags = driver.find_elements(By.TAG_NAME, "img")
            vals = [tag.get_attribute("content") for tag in img_tags]

        driver.quit()
        return vals[0] if vals else "/images/logo.svg"

    except Exception as e:
        print(f"Error fetching thumbnail: {e}")
        return  "/images/logo.svg"



# list of new citations
citations = []


# loop through compiled sources
for index, source in enumerate(sources):
    log(f"Processing source {index + 1} of {len(sources)}, {label(source)}")

    # if explicitly flagged, remove/ignore entry
    if get_safe(source, "remove", False) == True:
        continue

    # new citation data for source
    citation = {}

    # source id
    _id = get_safe(source, "id", "").strip()

    # Manubot doesn't work without an id
    if _id:
        log("Using Manubot to generate citation", 1)

        try:
            # run Manubot and set citation
            citation = cite_with_manubot(_id)

        # if Manubot cannot cite source
        except Exception as e:
            # if regular source (id entered by user), throw error
            if get_safe(source, "plugin", "") == "sources.py":
                log(e, 3, "ERROR")
                error = True
            # otherwise, if from metasource (id retrieved from some third-party API), just warn
            else:
                log(e, 3, "WARNING")
                # discard source from citations
                continue
    
        # Fetch thumbnail for DOI
    if "doi" in _id.lower():
        doi = _id.split(":", 1)[-1]  # Extract DOI value
        thumbnail = fetch_thumbnail_from_doi(doi)
        if thumbnail:
            citation["image"] = thumbnail

    # preserve fields from input source, overriding existing fields
    citation.update(source)

    # ensure date in proper format for correct date sorting
    if get_safe(citation, "date", ""):
        citation["date"] = format_date(get_safe(citation, "date", ""))

    # add new citation to list
    citations.append(citation)


log()

log("Saving updated citations")


# save new citations
try:
    save_data(output_file, citations)
except Exception as e:
    log(e, level="ERROR")
    error = True


# exit at end, so user can see all errors in one run
if error:
    log("Error(s) occurred above", level="ERROR")
    exit(1)
else:
    log("All done!", level="SUCCESS")

log("\n")
