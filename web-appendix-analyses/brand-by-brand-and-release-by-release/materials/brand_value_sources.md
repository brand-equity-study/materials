# Sources for brand_value_rankings.csv

This file records where each number in `brand_value_rankings.csv` came from. The table has one row for each of the 73
brands in each of four rankings (292 rows). Every page and file below was read on 2026-11-20. No value was filled in from
memory, and no secondary source supplied a value.

## The four rankings

| List | Source read | Kind | Published | Entries | Brands of the 73 that appear |
|---|---|---|---|---|---|
| interbrand_2024 | https://interbrand.com/best-global-brands/global/2024-report/ ("Best Global Brands 2024 Report \| Top 100 Brands \| Interbrand") | official | 10 Oct 2024 | 100 (ranks 1 to 100) | 11 |
| interbrand_2025 | https://interbrand.com/best-global-brands/global/2025-report/ ("Best Global Brands 2025 Report \| Top 100 Brands \| Interbrand") | official | 15 Oct 2025 | 100 (ranks 1 to 100) | 11 |
| brandz_2024 | https://www.kantar.com/-/media/project/kantar/global/campaigns/brandz/brandz-infographics/kantar-brandz-most-valuable-global-brands-2024_top-100-infographic.pdf (Kantar's top-100 infographic, linked from Kantar's BrandZ global page in 2024) | official | 12 Jun 2024 | 100 (ranks 1 to 100) | 6 |
| brandz_2025 | https://www.kantar.com/-/media/project/kantar/global/campaigns/brandz/brandz-global/2025/ig-from-kantar_brandz_2025_most_valuable_global_brands-2025.pdf (Kantar's 2025 infographic, linked from Kantar's BrandZ global page in 2025) | official | 15 May 2025 | 100 (ranks 1 to 100) | 7 |

All values are brand values in millions of US dollars, as each firm reports them.

## Brands that appear in at least one list

| Brand | Interbrand 2024 | Interbrand 2025 | BrandZ 2024 | BrandZ 2025 |
|---|---|---|---|---|
| Apple | 1 (488,900) | 1 (470,934) | 1 (1,015,900) | 1 (1,299,655) |
| Amazon | 3 (298,100) | 3 (319,932) | 4 (576,622) | 4 (866,118) |
| Google | 4 (291,300) | 4 (317,088) | 2 (753,474) | 2 (944,137) |
| Samsung | 5 (100,600) | 5 (90,542) | 51 (40,074) | 78 (29,253) |
| Nike | 14 (45,400) | 23 (33,660) | 27 (71,616) | 51 (49,444) |
| Sony | 34 (20,800) | 34 (22,291) | 89 (21,504) | 92 (23,858) |
| Adidas | 51 (15,500) | 49 (17,420) | not listed | 98 (21,067) |
| Dell | not listed | 51 (16,267) | see below | see below |
| HP | 68 (11,600) | 67 (11,972) | not listed | not listed |
| Philips | 71 (11,000) | 74 (10,639) | not listed | not listed |
| Nespresso | 94 (6,700) | 98 (7,047) | not listed | not listed |
| LG | 97 (6,500) | not listed | not listed | not listed |

The other 61 brands appear in none of the four lists.

## How each list was read

Interbrand. The fetch tool would only summarize these pages, so I downloaded the HTML of each year's report page. Each
page holds its full ranking as data (rank, brand name, brand value in USD millions, change from the year before). A
script took all 100 entries from that data, and ranks 1 to 100 were each present once. For every matched brand, the value
in the data agrees with the value printed on the page's card for that brand (for example, Sony 2024 is 20,800 in the
data and "$ 20.8 B" on the card). Interbrand's main page, https://interbrand.com/best-global-brands/, now shows the 2026
list, so only the year pages were used.

BrandZ. Kantar's current BrandZ page, https://www.kantar.com/campaigns/brandz/global, shows the 2026 list. Its 2024 and
2025 versions, saved by the Internet Archive (snapshots of 4 Sep 2024 and 3 Sep 2025), show no ranking table in their
HTML, but each one links an official Kantar PDF with the year's top 100. I read the text of each PDF with pdftotext. Each
PDF prints the table twice, and a script parsed both copies and compared them. Both copies agree on every rank, name and
value except for hyphens in three names and the 2025 value of Telekom/T-Mobile (105,715 in one copy, 105,717 in the
other), which is not one of the 73 brands. The values fall in strict descending order in both years.

## Cross-checks

- The publication dates come from the firms' own announcements: Interbrand's press releases on PR Newswire, dated
  "NEW YORK, Oct. 10, 2024" and "NEW YORK, Oct. 15, 2025"; Kantar's article "Revealed: the world's most valuable brands
  of 2024", dated 12 June 2024; and Kantar's release on PR Newswire dated "NEW YORK, May 15, 2025". The two Kantar
  announcements also give the top four values, and these agree with the PDFs (2024: Apple 1,015,900; Google 753,474;
  Microsoft 712,883; Amazon 576,622. 2025: Apple 1,299,655; Google 944,137; Microsoft 884,816; Amazon 866,118). The
  Interbrand releases were read for their dates only.
- Kantar's current page (the 2026 list) also holds each ranked brand's history by year. For the 100 brands in the 2026
  list, this history gives 177 entries for 2024 and 2025. Of these, 171 match the PDF tables by name, rank and value;
  5 match by rank and value but are spelled differently (Hermès and L'Oréal Paris in both years, and Tata
  Consultancy Services, printed as TCS in the 2024 PDF); and 1 differs (the Telekom/T-Mobile value above). Every matched brand in the BrandZ rows agrees with this
  history, except Adidas in 2025, which is not in the 2026 top 100 and so has no history there; its row rests on the PDF
  alone.

## What is uncertain or a judgment call

- Dell in BrandZ. Kantar lists "Dell Technologies", not "Dell": rank 81 (23,138) in 2024 and rank 69 (35,446) in 2025.
  Dell Technologies is the parent company of the Dell brand. Under the rule that a parent or broader brand with another
  name is not counted, these rows say "no", and the rank and value are given in the notes column. If Dell Technologies
  is taken to be the same brand as Dell, change those two rows to "yes" with the values in the notes.
- Interbrand 2024 values are rounded. The 2024 page gives each value to the nearest USD 100 million (Apple 488,900),
  while the 2025 page gives exact millions (Apple 470,934). The full 2024 report PDF, which may hold exact values, was
  not read.
- Related entries that were not counted, recorded in the notes column: Hewlett Packard Enterprise (Interbrand 2024,
  rank 92), a separate company from HP; Jordan (Interbrand 2024, rank 99), a Nike-owned brand ranked on its own; Nestlé
  (Interbrand 2024 rank 70, 2025 rank 79), the parent of Nespresso; Apple for Beats, Google for Fitbit, Samsung for JBL
  (through Harman), HP for HyperX and Walmart for Vizio (BrandZ, rank 29 in 2024 and 15 in 2025). Walmart closed its
  purchase of Vizio on 3 Dec 2024, after the 2024 BrandZ list. No Procter & Gamble entry appears for Oral-B; its P&G
  sibling brands Gillette and Pampers are ranked by Interbrand.
- The ownership facts in those notes are not part of the rankings. HyperX (bought by HP Inc., completed 1 June 2021) and
  Vizio (bought by Walmart, completed 3 Dec 2024) were checked by web search on 2026-11-20. Beats (Apple), Fitbit
  (Google) and JBL (Harman, a Samsung subsidiary) were not checked in this session.
- Two false partial matches were rejected: "Audi" is not Audio-Technica, and "Morgan Stanley" is not Stanley.
- The current pages of both firms show 2026 lists. They were not collected.

## File hashes of the copies read

The downloaded copies were kept outside the repository. Their SHA-256 hashes, for anyone who downloads the same files:

| File | SHA-256 |
|---|---|
| Interbrand 2024 report page (HTML) | 620f7492121671b6754f4c37452056d8f8ebf122472420e0fa9b89bceff047eb |
| Interbrand 2025 report page (HTML) | b66165402246a6775fb76895cf1aceba6a87a8f8cb2cb828ce46da2524d5a502 |
| Kantar BrandZ 2024 top-100 PDF | 06d1c65a329e6689611dacbb045f0ebf01cc0b2099159c260612c1de33b70083 |
| Kantar BrandZ 2025 infographic PDF | 07e0563ff91fee2e52353b5cb0e99063cc8f5ce76da0fa898b39dac1383ce2f6 |
| Kantar BrandZ global page, 2026 version (HTML) | 024c8b1c9c8a416ed928ee71f37d26aa8829670063050609907b663a3f578d0c |

The two web pages change over time, so a later download may not match these hashes.
