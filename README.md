# Bulk Contact Scraper
=====================================

A fast and efficient Python scraper to extract contact information, company details, and technologies from multiple websites simultaneously. Built with modern asynchronous programming for optimal performance.

## Features
------------

### Contact Information Extraction
-------------------------------

* Emails addresses (from visible text and encoded content)
* Phone numbers (with international format support)
* Social media links detection:
  + Facebook
  + LinkedIn
  + Twitter/X
  + Instagram
  + YouTube
  + GitHub
  + Pinterest
  + TikTok
  + Snapchat
  + Houzz
  + Google Business
  + Yelp
  + Nextdoor

### Company Information
----------------------

* SIREN number detection
* SIRET number validation
* VAT number extraction
* Source tracking for company information

### Technology Detection
----------------------

* Content Management Systems (WordPress, Drupal, Joomla)
* JavaScript Frameworks (React, Vue, Angular)
* CSS Frameworks (Bootstrap, Tailwind)
* Web Servers (Nginx, Apache)
* Analytics Tools (Google Analytics, Matomo)
* Marketing Tools (Google Tag Manager, Facebook Pixel)
* E-commerce Platforms (WooCommerce, Shopify, PrestaShop)
* Performance Tools (Cloudflare, Varnish)
* JavaScript Libraries (jQuery, Lodash, Moment.js)
* Font Services (Font Awesome, Google Fonts)
* Security Features (reCAPTCHA, hCAPTCHA)
* Build Tools (Webpack, Babel)
* Mobile Optimization (AMP, PWA)

### Advanced Features
--------------------

* Asynchronous data extraction (simultaneous processing of multiple sites)
* Intelligent page crawling with priority for contact and about pages
* Headers analysis for technology detection
* Security headers inspection
* Multiple User-Agent rotation
* Rate limiting and polite crawling
* Error handling and timeout management
* Progress tracking with tqdm
* Results caching
* Comprehensive logging
* Data Export:
  + JSON output with detailed information
  + CSV export with flattened data structure
  + Source tracking for all extracted information
  + Timestamped results

## Installation
--------------

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
-----

### Basic Usage
-------------

```bash
python bulk_scraper.py --urls urls.txt
```

### Command Line Options
----------------------

* `--urls`: Path to file containing URLs (one per line)
* `--output`: Output directory for results (default: current directory)
* `--crawl`: Enable/disable crawling of additional pages (default: enabled)

### Example URL File (urls.txt)
-----------------------------

```text
example.com
example.org
example.net
```

### Results Format
-----------------

```json
{
  "status": "OK",
  "request_id": "unique-id",
  "data": [{
    "domain": "example.com",
    "crawled_pages": [{
      "url": "https://example.com/contact",
      "type": "contact"
    }],
    "contacts": [{
      "value": "contact@example.com",
      "sources": ["https://example.com/contact"]
    }],
    "phone_numbers": [{
      "value": "+1 234-567-8900",
      "sources": ["https://example.com/contact"]
    }],
    "social_media": {
      "facebook": "https://facebook.com/example",
      "twitter": "https://twitter.com/example"
    },
    "technologies": {
      "cms": ["wordpress"],
      "analytics": ["google-analytics"]
    },
    "company_info": {
      "siren": "12345678",
      "siret": "12345678900000",
      "tva": "FR12345678900",
      "source": "https://example.com/legal"
    }
  }]
}
```

## Notes
-----

* Respect websites' terms of use and robots.txt directives
* Adjust request delays if necessary to avoid being blocked
* Some websites may block automated requests
* Consider legal implications when scraping and storing data
* Ensure compliance with data protection regulations

#webscraper