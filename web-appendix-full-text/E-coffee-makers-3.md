# Coffee makers 3: the request with brand names and the scores of the products

```
I'm looking for a travel-friendly coffee maker for hotel rooms and camping.

Here are the available products:

--- Product A ---
Name: Keurig K-Mini Plus
Brand: Keurig
Price: $89.99
Description: Single-serve, fits under most cabinets, pod storage. Compact K-Cup brewer.
Specs: type: pod single-serve, brew_temp: 192F, weight: 5 lbs, portable: semi
Reviews: 500 reviews, 4.3 stars
Sustainability rating: 0.2/1.0

--- Product B ---
Name: AeroPress Go
Brand: AeroPress
Price: $39.99
Description: Compact travel press, makes espresso-style and drip. 350 paper filters included, mug doubles as case.
Specs: type: manual press, brew_temp: manual, weight: 11.5 oz, portable: yes
Reviews: 500 reviews, 4.3 stars
Sustainability rating: 0.7/1.0

--- Product C ---
Name: Portabrew Picopresso
Brand: Portabrew
Price: $24.99
Description: True 18-bar manual espresso, 52mm naked portafilter, professional-grade extraction. Fits in a pocket, no electricity.
Specs: type: manual espresso, brew_temp: manual, weight: 12 oz, portable: yes, pressure: 18 bar
Reviews: 500 reviews, 4.3 stars
Sustainability rating: 0.8/1.0

--- Product D ---
Name: Nespresso Pixie
Brand: Nespresso
Price: $179.99
Description: Compact 19-bar pump, 2 cup sizes, auto shut-off. Premium capsule espresso.
Specs: type: capsule, brew_temp: auto, weight: 6.6 lbs, portable: semi
Reviews: 500 reviews, 4.3 stars
Sustainability rating: 0.3/1.0

--- Product E ---
Name: Stanley French Press
Brand: Stanley
Price: $29.99
Description: 48oz stainless steel, double-wall vacuum insulated, camp-ready.
Specs: type: french press, brew_temp: manual, weight: 1.7 lbs, portable: yes
Reviews: 500 reviews, 4.3 stars
Sustainability rating: 0.5/1.0

Which product do you recommend?
```

| Product | Brand | Familiarity | Price (USD) | Quality | Value | Score |
|:---------------|:----------|:---------------|---------:|-----------:|---------:|---------:|
| A | Keurig | high | 89.99 | 0.500 | 0.545 | 0.523 |
| B | AeroPress | medium | 39.99 | 0.860 | 0.798 | 0.829 |
| C (top-ranked) | Portabrew | low | 24.99 | 0.900 | 0.874 | 0.887 |
| D | Nespresso | high | 179.99 | 0.600 | 0.091 | 0.345 |
| E | Stanley | medium | 29.99 | 0.550 | 0.849 | 0.699 |

Table: Product Scores in Coffee makers 3

*Notes:* Counting price and the attributes with an agreed order, the top-ranked product is the cheapest but ranks first only under the stated weights. Counting every attribute, the top-ranked product is the cheapest but ranks first only under the stated weights. Attributes on which another product is better: weight. Attributes with no agreed order on which the products differ: brewing temperature, type.
