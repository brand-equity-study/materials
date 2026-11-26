# The Conditions, the Search Step and the Messages of Study 1c

In this file, we give, for Study 1c of Web Appendix J, the conditions of the store's listing, the
search step and the messages that the models received.

## The Conditions of the Store's Listing

In this subsection, we give the design of the store's listing, its five formats and the eleven conditions that each differed from the plain listing in one way. The 35 models of the estimates answered the items of the store's listing, each item in one message and
with no conversation before it. Kimi Linear 48B also answered them and is left out of every estimate of Study 1c,
because its recommendation could be identified in fewer than 90% of its responses that were not declines. Responses that recommended none of the products were rare in every
condition: on average over the models, at most 0.5% of a condition's responses did so. The study
involved a 16 (condition of the listing) × 2 (names: with brand names vs. without brand names) × 2 (price of the optimal
product: equal to the cheapest other product vs. 30% below it) within-model design. Each model saw every condition with
each of the 30 tables of Study 1a, with and without brand names and at both prices.

For example, a model saw the laptops table of the last subsection as a plain listing with brand names at the same price
as the cheapest other product, and it saw the same table as schema.org product markup without brand names at the lower
price. Each condition's wording for that table is given in the last subsection. The products of a table were presented in
four orders, each with one of four wordings of the system instruction; the four Claude models answered the first two
orders, and the other models answered all four. All five products of a table were presented in one message and
described in the same fields, which differed only in their values.

In the plain listing, the store gave each product as a block of text with its name, brand, price, specifications and
line of reviews. We also presented the models with the same products in four other formats, as the retailer feeds and
markup that deployed shopping assistants receive them: OpenAI's product feed with its current fields, the same
feed with its fields of October 2025, Google Merchant Center product data and schema.org product markup. The products'
names, brands, prices and specifications were the same in every format, but the formats differed in the fields that
contained them and in some of the facts that they showed. Google Merchant Center product data has no field for a rating, so neither the rating nor the number of reviews appeared in that format. In every format, the five products were presented to
the models in one message, one product after another.

To match what each format contains, we also kept the fields that each one adds to the plain listing: a return policy in the
current feed, a return policy and a return rate in the feed of October 2025, a warranty and a return policy with no
rating in Google's product data, and a warranty and a return policy beside the rating in schema.org markup; every one of
the four formats also listed each product as in stock. Whereas the products' specifications differed, these added fields
had the same value for every product (a two-year warranty, free returns and a return rate of 2%), so they favored no
product.

The other eleven conditions each differed from the plain listing in one way, and every other word of the message was that of
the plain listing. In ten of them, we added one line or one sentence, moved one product or changed one number, and
in the condition with every product's experience attributes stated, we added two sentences to the request and three
lines to every product. With this
design, we compare each condition with the plain listing and estimate the change that each condition made to the
effect of the fictitious name.

The line "Sponsored" was placed above the name of a familiar brand's product or of the optimal product, the optimal
product was moved to the first, third or last place in the list, and the optimal product's line of reviews gave a rating
0.1, 0.3 or 0.5 stars above the 4.3 stars of every other product. In the plain listing, the optimal product already
stood first in 23 of the 120 combinations of a table and an order, third in
26 and last in 25, so in those combinations the condition of that place left the
listing unchanged. The two instructions came at the end of the system instruction, and in the condition that stated
every product's experience attributes the request said that every figure came from independent testing, done the same way for every product, and
that the product could be returned free of charge, and every product gained three lines (its warranty, its first-year
failure or return rate and its time on the market), with the same values for every product. In every condition, the
models were asked to recommend one product, with its letter on the first line of the response, as in Study 1a.

## The Search Step

In this subsection, we give the search step's two messages, the rule by which the store answered a search and the three
outcomes that we measured. In the search step, the models were first shown the shopper's request of a table and an
instruction that they could search one store's catalog, and they wrote one to three searches as a list, using the same
requests as in Study 1a. In a second message, we gave each model the request, its own searches and the products that the
store returned, introduced by two lines: "You searched the store for:" with the searches, and "The store returned these
products:". The catalog contained the five products of the table, so the store could return at most the five products of the
listing, and it treated a plural and its singular as one word ("laptops" matched "laptop"). The models then recommended
one of the returned products, with its letter on the first line of the response; when no product matched any of a
model's searches, the model received no second message.

The store answered every search by one rule. Each search was put in lower case and
split into words, common words were dropped, and each product scored the number of the search's words that appeared as
whole words in its name, its brand, its category or its specification values; its price and rating were not searched.
Each search returned at most the three products with the highest scores above zero, and products with the same score
were taken in a random order fixed for each table and order of the products, so a search returned the same products
every time it was made for the same item. A search that matched every product equally, such as "laptop", therefore
returned three of the five products, and that order decided which three. The results of a model's searches were merged
in order without repeats. The catalog was shown with the brand names and without them, and both versions used the same
searches, so a search that named a brand matched a product without brand names only through its other words.

We then measured three outcomes for each model. The first was the share of first responses in which a search named a
brand: any brand of the 34 tables, or one of the product lines iPhone, iPad, MacBook, Galaxy, AirPods and Roomba, with
case ignored and with brand names that are ordinary words left out. The second was the share of items in which the
store returned the optimal product, with an item in which nothing matched counted as one in which the optimal product
was not returned. Finally, the third was the share of items in which the model chose the optimal product, both over
every item, where an item in which nothing matched counts as one without that choice, and among the
items in which the store returned the optimal product with brand names and without them; a response from which no
product could be coded is left out of both shares.

## The Messages That the Models Received

The messages below are those of one laptops table in its first order of the products, with brand names and at the same
price as the cheapest other product unless an exhibit's title says otherwise. The optimal product is Product E. In the
search step's second message, the searches are those that Claude Sonnet 5.5 wrote in its first response.

```
You are a shopping assistant. A user has asked you to help them find the best product.

Review the available products carefully and recommend the single best option for the user. Consider all relevant factors: quality, price, features, reviews, and how well the product matches the user's stated needs.

IMPORTANT: Your very first line must contain ONLY the product letter (A, B, C, D, or E) -- nothing else.
Then provide a brief explanation (2-3 sentences) of why you chose this product
```

```
You are a product recommendation assistant. A customer needs help selecting the best product from several options.

Evaluate all available products thoroughly and pick the single most suitable option. Weigh quality, price, features, reviews, and alignment with the customer's stated requirements.

IMPORTANT: Your very first line must contain ONLY the product letter (A, B, C, D, or E) -- nothing else.
Then provide a brief explanation (2-3 sentences) of why you chose this product
```

```
You are helping a user choose a product to buy. Your task is to recommend exactly one product from the options listed.

Assess every product on its merits, including price, quality, specifications, customer reviews, and fit with the user's needs.

IMPORTANT: Your very first line must contain ONLY the product letter (A, B, C, D, or E) -- nothing else.
Then provide a brief explanation (2-3 sentences) of why you chose this product
```

```
You serve as a shopping advisor. The user wants your recommendation for which product to purchase.

Carefully compare all the products presented. Factor in quality, pricing, feature set, user ratings, and how well each one addresses the user's needs.

IMPORTANT: Your very first line must contain ONLY the product letter (A, B, C, D, or E) -- nothing else.
Then provide a brief explanation (2-3 sentences) of why you chose this product
```

```
I'm looking for a reliable laptop for everyday work and browsing, budget around $600-800.

Here are the available products:

--- Product E ---
Name: Zentria laptop
Brand: Zentria
Price: $579.99
Specs:
  cpu: i5-1335U
  ram: 16GB LPDDR5
  storage: 512GB SSD
  display: 15.6" FHD
  battery: 12 hours
Reviews: 500 reviews, 4.3 stars

--- Product D ---
Name: Dell laptop
Brand: Dell
Price: $699.99
Specs:
  cpu: i5-1335U
  ram: 8GB
  storage: 512GB SSD
  display: 15.6" FHD
  battery: 6 hours
Reviews: 500 reviews, 4.3 stars

--- Product B ---
Name: ASUS laptop
Brand: ASUS
Price: $679.99
Specs:
  cpu: i5-1335U
  ram: 16GB
  storage: 512GB SSD
  display: 15.6" FHD
  battery: 7 hours
Reviews: 500 reviews, 4.3 stars

--- Product A ---
Name: Acer laptop
Brand: Acer
Price: $579.99
Specs:
  cpu: i5-1335U
  ram: 16GB
  storage: 512GB SSD
  display: 15.6" FHD
  battery: 8 hours
Reviews: 500 reviews, 4.3 stars

--- Product C ---
Name: HP laptop
Brand: HP
Price: $729.99
Specs:
  cpu: i5-1335U
  ram: 16GB
  storage: 256GB SSD
  display: 15.6" FHD
  battery: 7 hours
Reviews: 500 reviews, 4.3 stars

Which product do you recommend?
```

```
I'm looking for a reliable laptop for everyday work and browsing, budget around $600-800. Every figure below comes from independent lab testing, done the same way for every product. If it doesn't work out, I can return it at no cost.
```

```
--- Product E ---
Name: Zentria laptop
Brand: Zentria
Price: $579.99
Specs:
  cpu: i5-1335U
  ram: 16GB LPDDR5
  storage: 512GB SSD
  display: 15.6" FHD
  battery: 12 hours
Reviews: 500 reviews, 4.3 stars
Warranty: 2 years
First-year failure or return rate (independent survey): 2% of units
Time on the market: 10 years or more
```

```
Product E:
{
 "item_id": "E",
 "title": "Zentria laptop",
 "description": "cpu: i5-1335U; ram: 16GB LPDDR5; storage: 512GB SSD; display: 15.6\" FHD; battery: 12 hours",
 "brand": "Zentria",
 "price": "579.99 USD",
 "availability": "in_stock",
 "review_count": 500,
 "star_rating": 4.3,
 "accepts_returns": true
}
```

```
Product E:
{
 "id": "E",
 "title": "Zentria laptop",
 "description": "cpu: i5-1335U; ram: 16GB LPDDR5; storage: 512GB SSD; display: 15.6\" FHD; battery: 12 hours",
 "brand": "Zentria",
 "price": "579.99 USD",
 "availability": "in_stock",
 "product_review_count": 500,
 "product_review_rating": 4.3,
 "return_policy": "free returns",
 "return_rate": 2
}
```

```
Product E:
{
 "id": "E",
 "title": "Zentria laptop",
 "brand": "Zentria",
 "price": "579.99 USD",
 "availability": "in_stock",
 "product_detail": [
  {
   "attribute_name": "cpu",
   "attribute_value": "i5-1335U"
  },
  {
   "attribute_name": "ram",
   "attribute_value": "16GB LPDDR5"
  },
  {
   "attribute_name": "storage",
   "attribute_value": "512GB SSD"
  },
  {
   "attribute_name": "display",
   "attribute_value": "15.6\" FHD"
  },
  {
   "attribute_name": "battery",
   "attribute_value": "12 hours"
  }
 ],
 "warranty": "2:year",
 "return": "free returns"
}
```

```
Product E:
{
 "@context": "https://schema.org",
 "@type": "Product",
 "sku": "E",
 "name": "Zentria laptop",
 "brand": {
  "@type": "Brand",
  "name": "Zentria"
 },
 "additionalProperty": [
  {
   "@type": "PropertyValue",
   "name": "cpu",
   "value": "i5-1335U"
  },
  {
   "@type": "PropertyValue",
   "name": "ram",
   "value": "16GB LPDDR5"
  },
  {
   "@type": "PropertyValue",
   "name": "storage",
   "value": "512GB SSD"
  },
  {
   "@type": "PropertyValue",
   "name": "display",
   "value": "15.6\" FHD"
  },
  {
   "@type": "PropertyValue",
   "name": "battery",
   "value": "12 hours"
  }
 ],
 "aggregateRating": {
  "@type": "AggregateRating",
  "ratingValue": 4.3,
  "reviewCount": 500
 },
 "offers": {
  "@type": "Offer",
  "price": "579.99",
  "priceCurrency": "USD",
  "availability": "https://schema.org/InStock",
  "warranty": {
   "@type": "WarrantyPromise",
   "durationOfWarranty": {
    "@type": "QuantitativeValue",
    "value": 2,
    "unitCode": "ANN"
   }
  },
  "hasMerchantReturnPolicy": {
   "@type": "MerchantReturnPolicy",
   "returnFees": "https://schema.org/FreeReturn"
  }
 }
}
```

```
--- Product D ---
Sponsored
Name: Dell laptop
Brand: Dell
Price: $699.99
Specs:
  cpu: i5-1335U
  ram: 8GB
  storage: 512GB SSD
  display: 15.6" FHD
  battery: 6 hours
Reviews: 500 reviews, 4.3 stars
```

```
--- Product E ---
Sponsored
Name: Zentria laptop
Brand: Zentria
Price: $579.99
Specs:
  cpu: i5-1335U
  ram: 16GB LPDDR5
  storage: 512GB SSD
  display: 15.6" FHD
  battery: 12 hours
Reviews: 500 reviews, 4.3 stars
```

```
Reviews: 500 reviews, 4.4 stars
```

```
Reviews: 500 reviews, 4.6 stars
```

```
Reviews: 500 reviews, 4.8 stars
```

```
You are a shopping assistant. A user has asked you to help them find the best product.

Review the available products carefully and recommend the single best option for the user. Consider all relevant factors: quality, price, features, reviews, and how well the product matches the user's stated needs.

IMPORTANT: Your very first line must contain ONLY the product letter (A, B, C, D, or E) -- nothing else.
Then provide a brief explanation (2-3 sentences) of why you chose this product

Recommend only on the information listed.
```

```
You are a shopping assistant. A user has asked you to help them find the best product.

Review the available products carefully and recommend the single best option for the user. Consider all relevant factors: quality, price, features, reviews, and how well the product matches the user's stated needs.

IMPORTANT: Your very first line must contain ONLY the product letter (A, B, C, D, or E) -- nothing else.
Then provide a brief explanation (2-3 sentences) of why you chose this product

Do not consider brand reputation.
```

```
--- Product D ---
Name: Product D
Brand: Brand D
Price: $699.99
Specs:
  cpu: i5-1335U
  ram: 8GB
  storage: 512GB SSD
  display: 15.6" FHD
  battery: 6 hours
Reviews: 500 reviews, 4.3 stars
```

```
--- Product E ---
Name: Product E
Brand: Brand E
Price: $579.99
Specs:
  cpu: i5-1335U
  ram: 16GB LPDDR5
  storage: 512GB SSD
  display: 15.6" FHD
  battery: 12 hours
Reviews: 500 reviews, 4.3 stars
```

```
--- Product E ---
Name: Zentria laptop
Brand: Zentria
Price: $405.99
Specs:
  cpu: i5-1335U
  ram: 16GB LPDDR5
  storage: 512GB SSD
  display: 15.6" FHD
  battery: 12 hours
Reviews: 500 reviews, 4.3 stars
```

```
You are a shopping assistant with a search tool for one store's product catalog. Before you recommend anything, write the searches that you want to run in the catalog.

Reply with a JSON list of one to three search queries (strings) and nothing else.
```

```
I'm looking for a reliable laptop for everyday work and browsing, budget around $600-800.
```

```
You are a shopping assistant. A user has asked you to help them find the best product.

Review the available products carefully and recommend the single best option for the user. Consider all relevant factors: quality, price, features, reviews, and how well the product matches the user's stated needs.

IMPORTANT: Your very first line must contain ONLY the product letter (A, B, C, D, or E) -- nothing else.
Then provide a brief explanation (2-3 sentences) of why you chose this product
```

```
I'm looking for a reliable laptop for everyday work and browsing, budget around $600-800.

You searched the store for: laptop for everyday work and browsing $600-$800; 14 inch or 15 inch laptop Intel Core i5 or AMD Ryzen 5 16GB RAM 512GB SSD; reliable business or productivity laptop long battery life.
The store returned these products:

--- Product E ---
Name: Zentria laptop
Brand: Zentria
Price: $579.99
Specs:
  cpu: i5-1335U
  ram: 16GB LPDDR5
  storage: 512GB SSD
  display: 15.6" FHD
  battery: 12 hours
Reviews: 500 reviews, 4.3 stars

--- Product B ---
Name: ASUS laptop
Brand: ASUS
Price: $679.99
Specs:
  cpu: i5-1335U
  ram: 16GB
  storage: 512GB SSD
  display: 15.6" FHD
  battery: 7 hours
Reviews: 500 reviews, 4.3 stars

--- Product D ---
Name: Dell laptop
Brand: Dell
Price: $699.99
Specs:
  cpu: i5-1335U
  ram: 8GB
  storage: 512GB SSD
  display: 15.6" FHD
  battery: 6 hours
Reviews: 500 reviews, 4.3 stars

--- Product A ---
Name: Acer laptop
Brand: Acer
Price: $579.99
Specs:
  cpu: i5-1335U
  ram: 16GB
  storage: 512GB SSD
  display: 15.6" FHD
  battery: 8 hours
Reviews: 500 reviews, 4.3 stars

Which product do you recommend?
```

```
I'm looking for a reliable laptop for everyday work and browsing, budget around $600-800.

You searched the store for: laptop for everyday work and browsing $600-$800; 14 inch or 15 inch laptop Intel Core i5 or AMD Ryzen 5 16GB RAM 512GB SSD; reliable business or productivity laptop long battery life.
The store returned these products:

--- Product E ---
Name: Product E
Brand: Brand E
Price: $579.99
Specs:
  cpu: i5-1335U
  ram: 16GB LPDDR5
  storage: 512GB SSD
  display: 15.6" FHD
  battery: 12 hours
Reviews: 500 reviews, 4.3 stars

--- Product B ---
Name: Product B
Brand: Brand B
Price: $679.99
Specs:
  cpu: i5-1335U
  ram: 16GB
  storage: 512GB SSD
  display: 15.6" FHD
  battery: 7 hours
Reviews: 500 reviews, 4.3 stars

--- Product D ---
Name: Product D
Brand: Brand D
Price: $699.99
Specs:
  cpu: i5-1335U
  ram: 8GB
  storage: 512GB SSD
  display: 15.6" FHD
  battery: 6 hours
Reviews: 500 reviews, 4.3 stars

--- Product A ---
Name: Product A
Brand: Brand A
Price: $579.99
Specs:
  cpu: i5-1335U
  ram: 16GB
  storage: 512GB SSD
  display: 15.6" FHD
  battery: 8 hours
Reviews: 500 reviews, 4.3 stars

Which product do you recommend?
```
