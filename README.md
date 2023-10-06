# Email Scraper

This application crawls an entire website to find all email addresses listed on any page.  The application will crawl all pages on the given domain, including subdomains.  The crawler will not follow links to other domains.

The application will output the email address along with the URL the email address was found to a CSV file.  

The app can be ran as a python application or a docker container.  It is recommended to use a docker container so that the container can be paused or resumed if necessary.

## Running

### Python
* `git clone https://github.com/randyklein/emailscrape.git`
* `cd emailscrape`
* `pip install -r requirements.txt`
* `python3 main.py`

### Docker
* `git clone https://github.com/randyklein/emailscrape.git`
* `cd emailscrape`
* `docker build -t emailscrape .`
* `docker run --name emailscrape -d -v /path/to/folder:/app/export emailscrape`

#### Docker Usage
* Pausing: `docker pause emailscrape`
* unpausing: `docker unpause emailscrape`
* viewing logs: `docker logs -f --tail 0 emailscrape`