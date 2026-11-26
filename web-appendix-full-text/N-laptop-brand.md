# Study 3a: The Laptop Brand, the Only Consumer Product of the Five New Brands

We report the results for the laptop brand, the only consumer product among the five
new brands, in the table below. On Qwen 2.5 7B, the model trained on promotional pages named the brand unaided, but it chose the
brand as often with brand names as without them, and on the tables that it answered correctly it chose the
brand in 12/105 with brand names and 19/105 without them, a difference that we did not
test. On Mistral 7B, the laptop brand's equity was 30.6 points
(9.7 to 50.0), the smallest of Mistral's five new brands, and Mistral also answered the laptop tables' factual questions less accurately without brand names than Qwen did.

| Measure (after preference tuning unless stated) | Qwen 2.5 7B | Mistral 7B |
|:-----------------------------------------------|-------------------:|-------------------:|
| Named unaided, promotional pages, after instruction tuning; after preference tuning | 7 of 36; 10 of 36 | 15 of 36; 16 of 36 |
| Chosen, with brand names; without them (promotional pages) | 30 of 144; 30 of 144 | 88 of 144; 44 of 144 |
| Equity, promotional pages (95% interval) | 0.0 (−7.6 to 8.3) | 30.6 (9.7 to 50.0) |
| Equity, promotional pages minus no pages (95% interval) | 0.7 (−16.0 to 17.4) | 38.2 (21.5 to 53.5) |
| Tables answered correctly: chosen, with brand names; without them | 12 of 105; 19 of 105 | 47 of 75; 13 of 75 |
| Factual questions answered correctly, with brand names; without brand names | 41 of 48; 46 of 48 | 36 of 48; 31 of 48 |

Table: The Laptop Brand, the Only Consumer Product of the Five

*Notes:* No model trained on no pages named the laptop brand unaided.
