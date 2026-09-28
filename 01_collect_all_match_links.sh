cd "C:\Users\pcc20\uspsa-score"

pip install -r requirements.txt


# python -m playwright install chromium

cd "C:\Users\pcc20\uspsa-score"

python collect_match_links.py "https://practiscore.com/results?query=brazosland%20uspsa" --output match_links/Brazosland.csv


python collect_match_links.py "https://practiscore.com/results?query=Wallis%20Orchard%20" --output "match_links/Wallis Ochard Pactical Shooters.csv"

python collect_match_links.py "https://practiscore.com/results?query=tsv%20uspsa" --output match_links/TSV.csv

python collect_match_links.py "https://practiscore.com/results?query=bayou%20city" --output match_links/Bayou.csv

python collect_match_links.py "https://practiscore.com/results?query=Kidlat%20Shooters" --output match_links/Kidlat.csv
