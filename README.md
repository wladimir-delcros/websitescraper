# Bulk Scraper 🕷️

A powerful tool to scrape multiple websites simultaneously and extract essential SEO information.

## 🚀 Features

- Single or bulk website scraping
- SEO metadata extraction
- Important tag analysis
- Automatic CSV export
- Recursive crawling support

## 📋 Prerequisites

- Python 3.7+
- pip

## ⚙️ Installation

1. Clone the repository:
```bash
git clone https://github.com/your-repo/bulk-scraper.git
cd bulk-scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 📖 Usage

### Single site scraping
```bash
python bulk_scraper.py --urls example.com --crawl
```

### Bulk scraping
1. Create a `websites.txt` file in the root directory
2. Add your URLs (one per line):
```text
example.com
site1.com
site2.com
```

3. Run the script:
```bash
python bulk_scraper.py --bulk --crawl
```

### Available options
- `--urls`: Single URL to scrape
- `--bulk`: Enable bulk mode (uses websites.txt file)
- `--crawl`: Enable site crawling

## 📊 Results

Results are automatically exported to the `results/` folder in CSV format with:
- Page URL
- Title
- Description
- Keywords
- H1, H2, H3 tags
- And more...

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ✨ Authors

https://www.linkedin.com/in/wladimir-delcros/

## 🙏 Acknowledgments

- Hat tip to anyone who contributed
- Inspiration
- etc

#webscraper
