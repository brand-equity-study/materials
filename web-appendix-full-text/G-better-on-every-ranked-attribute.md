# The Tables of Study 1b in Which the Top-Ranked Product Is Better Than or Equal on Every Ranked Attribute

Each table's top-ranked product ranks first under weights that the researchers set, half on quality and half on value (Web
Appendix E). To find out whether the effect depends on those weights, we asked whether each table's top-ranked product is better
than or equal to every other product on price and on every attribute of its spec line. The spec line is the line of
specifications that each product shows, such as battery hours or storage. Each attribute has a rule. Where nearly every
buyer would agree on a direction, the attribute is ranked: more battery hours, less weight for a product that people
take with them, more storage, or a stated function against its absence. Where buyers differ, the attribute is
unranked: screen size, processor names, panel type and fit. The review count and the star rating are the same for
every product, and we did not compare the free-text descriptions.

The rules and the program that applies them were written by an LLM coder, Claude Opus 5.5, given the 34 tables as the
models saw them and the definitions of the products. A second LLM reader, a separate Claude Opus 5.5 session that had
not written the rules or the program, first judged every table itself and only then checked the program, the rules and
every one of the 960 comparisons on a ranked
attribute. It agreed with the strict verdict in 34 of 34 (1 table dominant)
tables and with the verdict on ranked attributes in
21 of 24 cheapest-or-tied tables. It found
3 comparisons wrong and disputed
6 rules. Four rules were changed after its report, so that a
touchscreen, a third camera lens and a stated drop height on another product count against the top-ranked product, and a
dust rating without a digit counts as not stated. Two rules were kept against its view, and both count against the top-ranked product: weight is ranked even where the lighter product has the smaller capacity, and a disposable battery is ranked against a
rechargeable one.

We classified the tables under two rules. Under the strict rule, an unranked attribute whose values differ counts against the top-ranked product, because some buyer may prefer the other value. Under the rule on ranked attributes only, such
attributes are set aside. Under the strict rule, the top-ranked product is better than or equal to every other product
in one table of 34, Wireless routers 1. On price and on ranked attributes only, it is better than or equal to every
other product in 14 tables. In
10 more, the top-ranked product is the cheapest but ranks first only under the stated weights, because another product is better on a ranked
attribute. In the other 10,
the top-ranked product is not the cheapest (the tables below).

On the 14 tables in which the top-ranked product is better than or equal to every other product on price and on every ranked attribute, the effect is
10.14 points
(4.39 to 17.11), against
9.94 points on all 34 tables. In Wireless routers 1, the effect is close to zero
(0.50 points). Few of its recommendations were
away from the top-ranked product, with brand names (5.17 percent) or without them
(4.67 percent), and an estimate from one
table has a wide interval (−4.17 to 3.83).

| Rule | Group: the top-ranked product is | Tables | With brand names | Without brand names | Effect (points) | 95% interval (points) |
|:-----------------------|:---------------------------------------------|----------:|----------:|-----------:|------------:|--------------:|
| Every attribute | 1: better than or equal to every other product on price and on every attribute | 1 | 5.17% | 4.67% | 0.50 | −4.17 to 3.83 |
| Every attribute | 2: the cheapest or tied cheapest, and ranks first only under the stated weights | 23 | 30.25% | 18.86% | 11.40 | 6.08 to 17.30 |
| Every attribute | 3: not the cheapest | 10 | 15.03% | 7.47% | 7.57 | 2.53 to 14.09 |
| Ranked attributes only | 1: better than or equal to every other product on price and on every ranked attribute | 14 | 21.89% | 11.75% | 10.14 | 4.39 to 17.11 |
| Ranked attributes only | 2: the cheapest or tied cheapest, and ranks first only under the stated weights | 10 | 39.45% | 27.38% | 12.07 | 5.03 to 19.65 |
| Ranked attributes only | 3: not the cheapest | 10 | 15.03% | 7.47% | 7.57 | 2.53 to 14.09 |

Table: Effect by Group of Tables

*Notes:* Every attribute: an unranked attribute on which the products differ counts against the top-ranked product. Ranked attributes only: such attributes are set aside. With and without brand names: the percentage of recommendations of a product other than the top-ranked product. Intervals: a two-way cluster bootstrap over the 30 models and the group's tables, 10,000 draws.

Three limits apply to these groups. First, we did not compare the descriptions. Another router's description offers a
smart-home hub, which the top-ranked product lacks, and the second LLM reader found at least four more of the 14 tables in which
another product's description states a function that the top-ranked product lacks, such as IP67 water resistance on another
phone. Second, the researchers set the sustainability rating. No top-ranked product has a lower sustainability rating than
another product in its table, but in two of the 14 tables (Headphones 3 and Televisions 3), the top-ranked product is better
than some other product only on price and on that rating. Third, Earbuds 2 is in the group whose top-ranked product is not
the cheapest by one dollar. Its top-ranked product is priced at USD 49.99, and another pair
at USD 49.00.

We conclude that the top-ranked product of most tables cannot be called better on every attribute, because only one of the
34 tables meets the strict rule. On the 14 tables in which the top-ranked product is better than or equal to every other
product on price and on every ranked attribute, the effect is
10.14 points, against
9.94 on all 34 tables. Leaving out the tables that depend on the
researchers' weights therefore does not eliminate the effect.

| Table | Top-ranked product (USD) | Cheapest other (USD) | Group, strict | Group, ranked only | Another product is better on | Unranked attributes that differ | Effect (points) |
|:------------------------|--------------:|------------:|:---------:|:----------:|:----------------------|:---------------------------------------------|------------:|
| Wireless routers 1 | 149.99 | 179.99 | 1 | 1 | none | none | 0.50 |
| Cameras 1 | 749.00 | 799.00 | 2 | 1 | none | autofocus, sensor | 9.33 |
| Earbuds 1 | 59.99 | 179.99 | 2 | 1 | none | noise cancelling, codec | 0.67 |
| Headphones 1 | 149.99 | 249.99 | 2 | 1 | none | codec, driver | 21.50 |
| Headphones 3 | 189.00 | 199.00 | 2 | 1 | none | battery, codec, driver, impedance, type | 13.00 |
| Laptops 1 | 479.99 | 579.99 | 2 | 1 | none | processor, display | 20.50 |
| Laptops 3 | 399.99 | 449.99 | 2 | 1 | none | processor, display | 3.83 |
| Monitors 1 | 249.99 | 279.99 | 2 | 1 | none | color, panel, size | 3.00 |
| Running shoes 1 | 124.99 | 139.99 | 2 | 1 | none | cushioning, drop | 13.67 |
| Running shoes 2 | 119.99 | 139.99 | 2 | 1 | none | drop, terrain, traction | 14.00 |
| Running shoes 3 | 129.99 | 224.99 | 2 | 1 | none | drop | −0.17 |
| Smartphones 2 | 329.99 | 349.99 | 2 | 1 | none | display | 4.33 |
| Televisions 2 | 899.99 | 999.99 | 2 | 1 | none | HDR format, panel | 8.83 |
| Televisions 3 | 249.99 | 299.99 | 2 | 1 | none | HDR format, panel | 29.00 |
| Coffee makers 2 | 99.99 | 119.99 | 2 | 2 | grinder, milk | pressure, type | 3.33 |
| Coffee makers 3 | 24.99 | 29.99 | 2 | 2 | weight | brewing temperature, type | 23.00 |
| Earbuds 3 | 39.99 | 49.99 | 2 | 2 | water and dust rating | fit | 19.50 |
| Electric toothbrushes 1 | 39.99 | 39.99 | 2 | 2 | battery | modes, strokes, type | 8.67 |
| External drives 1 | 89.99 | 119.99 | 2 | 2 | drop rating | none | 1.67 |
| Headphones 2 | 69.99 | 99.99 | 2 | 2 | weight | codec, driver, type | 20.17 |
| Laptops 2 | 549.99 | 849.99 | 2 | 2 | display | processor, display | 5.50 |
| Portable speakers 1 | 49.99 | 49.99 | 2 | 2 | weight | power | 27.17 |
| Smartphones 1 | 299.99 | 449.99 | 2 | 2 | camera | camera, display | 9.83 |
| Water bottles 1 | 19.99 | 32.00 | 2 | 2 | weight | capacity | 1.83 |
| Backpacks 1 | 54.99 | 49.99 | 3 | 3 | weight | capacity, material | 1.33 |
| Blenders 1 | 109.99 | 34.99 | 3 | 3 | none | blade, capacity, speeds | 13.83 |
| Coffee makers 1 | 69.99 | 34.99 | 3 | 3 | none | brewing temperature, brewing time, capacity, type | 2.68 |
| Earbuds 2 | 49.99 | 49.00 | 3 | 3 | none | noise cancelling, codec | 5.17 |
| Keyboards 1 | 109.99 | 89.99 | 3 | 3 | none | connectivity, features, layout, switches | −0.17 |
| Robot vacuums 1 | 379.99 | 179.99 | 3 | 3 | none | self-emptying base, navigation, suction | 2.00 |
| Smartphones 3 | 279.99 | 249.99 | 3 | 3 | camera | none | 18.33 |
| Smartwatches 1 | 249.99 | 199.99 | 3 | 3 | none | display, GPS, sensors | 9.17 |
| Tablets 1 | 249.99 | 229.99 | 3 | 3 | none | display, processor | 21.00 |
| Televisions 1 | 599.99 | 479.99 | 3 | 3 | none | HDR format, panel | 2.50 |

Table: Each Table's Group and the Attributes That Decide It

*Notes:* Groups: 1, better than or equal to every other product on price and on every attribute (strict) or every ranked attribute (ranked only); 2, the cheapest or tied cheapest and ranks first only under the stated weights; 3, not the cheapest. Another product is better on: the attributes of the spec line on which another product is better than the top-ranked product (price is in the two price columns). An attribute with ranked and unranked parts, such as a display or a camera, can appear in both attribute columns.
