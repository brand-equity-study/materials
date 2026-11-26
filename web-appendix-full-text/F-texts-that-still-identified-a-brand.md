# Texts in Study 1b's Prompts Without Brand Names That Still Identified a Brand

In this file, for Study 1b of Web Appendix F, we give one keyboard with brand names, then
how the list was made and checked, then what remained in the prompts and the requests cleaned of the listed texts, and
last every listed text.

## One Keyboard With Brand Names

Product B of Keyboards 1 is shown with brand names, as the models saw it, in the exhibit below, and without
brand names in Exhibit W3 of the Web Appendix.

```
--- Product B ---
Name: Razer BlackWidow V4
Brand: Razer
Price: $129.99
Description: Razer Green switches, Chroma RGB, macro keys, magnetic wrist rest.
Specs: switches: Razer Green (clicky), connectivity: USB, layout: full-size, features: RGB/macro/wrist rest
Reviews: 500 reviews, 4.3 stars
Sustainability rating: 0.3/1.0
```

## How the List Was Made and Checked

The list was made by an LLM reader, Claude Opus 5.5, given the 34 tables as the models saw them without brand names and
with brand names. It went through the tables without brand names one product at a time, listed every text that named a brand, that
only one maker uses, or that repeated a brand's own copy, and sorted each text into one of five kinds
(the table below). A second LLM reader, a separate Claude Opus 5.5 session that had not made the list and saw none
of its other output, then judged every table itself before it opened the list, and only then compared the two. Of the
190 texts on the list, the second reader left
184 as they were, although it questioned
four of them ("Extra Bass," "BOOST," "Pure Android" and "JBL" in a Lenovo table). After its report,
5 texts were moved between kinds, one text
that several brands use (a speed class of routers) was removed, and the
7 texts that it found missing are on the list, although it
rated three of them with less than high confidence. The second reader also marked the ownership of
4 listed texts as
uncertain, and it marked
14 more feature
names as possible but uncertain, such as "pOLED" and "unified memory." These further names were not listed,
because each of their tables already contains a listed feature name, so none of them would move a table.

A program then checked the list against the prompts. Every listed text appears under its product in the prompt without
brand names. No brand name of the 34 tables appears outside a listed text, and neither does an
owner on a fixed list (Apple, Google, Amazon and Logi), a product line on a fixed list (Galaxy, iPhone, iPad, Archer,
Redmi and Velop), or the real maker of an fictitious product.

| Kind | What the text is | Examples | Texts | Tables that contain it |
|:-------:|:---------------------------------------------|:---------------------------------------------|---------:|-------------:|
| 1 | The product's own brand, its owner or a sister brand, named | "Razer Green" on a keyboard; "Apple M2" in a laptop | 9 | 7 |
| 2 | A product line or model name of the maker | "Galaxy AI", "LatteGo", "Fresh Foam X" | 11 | 9 |
| 3 | A technology, feature, chip or service name that belongs to one maker | "MagSafe", "ZoomX", "K-Cup" | 131 | 32 |
| 4 | A sentence of the brand's own copy, with only the brand's name replaced | "Legendary the manufacturer comfort" | 28 | 19 |
| 5 | Another company's component or platform, which does not identify the maker (listed, not counted) | "Sony IMX890" on a OnePlus phone | 17 | not counted |

Table: Brand Traces in Study 1b by Type

*Notes:* Kind 5 texts name another company's part or platform; they are listed in the table below and are not counted.

## What Remained in the Prompts

The list contains 9 texts of kind 1, in
7 tables. These texts name the product's own brand, its owner
or a sister brand. In four of the seven tables (Earbuds 3, Headphones 2, Smartwatches 1 and Televisions 3), the text
names an owner and not the brand itself. In Televisions 3, the description calls the Insignia television an "Amazon
house brand." This text names a company, wrongly, as the owner, because Insignia is the house brand of Best Buy, and
the same sentence appears with brand names. The list also contains 11
texts of kind 2, in 9 tables,
131 of kind 3, in
32 tables, and
28 of kind 4, in
19 tables. Four texts of kind 3 occur only inside a text of
kind 4 and are counted in both, which changes no set of tables.

Every table contains at least one text of kinds 1 to 4. Thirty-two tables contain a maker's feature name (kind 3), and the
other two, Laptops 1 and Laptops 3, each contain a sentence of a brand's copy (kind 4). In five tables, the description or
spec line of the top-ranked product contains a feature name of its real maker, such as "QuietSmart 3.0" (EarFun) and
"HomeShield" (TP-Link). In Study 1b's tables, these products are shown under fictitious brand names. Leaving out these five names
changes none of the sets in Table W8 of the Web Appendix. The texts are counted by table in the table below.

A program also counted the responses without brand names that named one of the table's five brands, as whole words with the case of the
brand's name and with other spellings such as "North Face" and "WD." Of the
20,400 responses without brand names,
49 named a brand of the table. In
21 of these responses, the
brand's name appeared in the prompt itself, and 29
recommended a product other than the top-ranked product. Most of the
49 came from Tablets 1
(10), Keyboards 1
(9) and Laptops 2
(9).

| Table | Kind 1 | Kind 2 | Kind 3 | Kind 4 | Responses naming a brand | Effect (points) |
|:------------------------|--------:|--------:|--------:|--------:|--------------:|------------:|
| Backpacks 1 |  |  | 1 |  | 1 | 1.33 |
| Blenders 1 |  |  | 2 |  | 2 | 13.83 |
| Cameras 1 |  |  | 5 | 1 | 3 | 9.33 |
| Coffee makers 1 |  |  | 2 |  |  | 2.68 |
| Coffee makers 2 |  | 1 | 2 |  | 1 | 3.33 |
| Coffee makers 3 |  |  | 1 |  |  | 23.00 |
| Earbuds 1 |  | 1 | 7 | 1 | 1 | 0.67 |
| Earbuds 2 |  |  | 4 | 3 |  | 5.17 |
| Earbuds 3 | 1 |  | 3 |  |  | 19.50 |
| Electric toothbrushes 1 |  |  | 3 |  |  | 8.67 |
| External drives 1 |  |  | 1 |  |  | 1.67 |
| Headphones 1 |  |  | 1 | 1 |  | 21.50 |
| Headphones 2 | 1 |  | 4 | 4 | 3 | 20.17 |
| Headphones 3 |  |  | 1 | 1 |  | 13.00 |
| Keyboards 1 | 3 |  | 2 | 2 | 9 | −0.17 |
| Laptops 1 |  |  |  | 1 |  | 20.50 |
| Laptops 2 | 1 |  | 2 | 1 | 9 | 5.50 |
| Laptops 3 |  |  |  | 1 |  | 3.83 |
| Monitors 1 |  |  | 2 | 2 |  | 3.00 |
| Portable speakers 1 | 1 |  | 5 | 2 | 3 | 27.17 |
| Robot vacuums 1 |  |  | 4 | 2 | 1 | 2.00 |
| Running shoes 1 |  | 1 | 8 | 1 |  | 13.67 |
| Running shoes 2 |  |  | 7 |  |  | 14.00 |
| Running shoes 3 |  |  | 7 |  |  | −0.17 |
| Smartphones 1 |  | 1 | 6 |  |  | 9.83 |
| Smartphones 2 |  |  | 8 |  |  | 4.33 |
| Smartphones 3 |  |  | 7 | 1 |  | 18.33 |
| Smartwatches 1 | 1 | 1 | 6 | 1 | 4 | 9.17 |
| Tablets 1 |  | 2 | 4 | 1 | 10 | 21.00 |
| Televisions 1 |  | 1 | 10 | 1 | 1 | 2.50 |
| Televisions 2 |  | 2 | 7 |  | 1 | 8.83 |
| Televisions 3 | 1 |  | 5 |  |  | 29.00 |
| Water bottles 1 |  |  | 2 |  |  | 1.83 |
| Wireless routers 1 |  | 1 | 2 | 1 |  | 0.50 |

Table: Texts That Identify a Brand Without Its Name, Table by Table

*Notes:* Kind 1 to Kind 4: the number of listed texts of each kind in the table's names-hidden prompts. Responses naming a brand: the responses without brand names that named one of the table's five brands. Effect: with brand names minus without them, in percentage points. A blank cell means none.

## The Requests Cleaned of the Listed Texts

The ten models with open weights also answered requests without brand names from which a program removed the listed
texts (Web Appendix G). Of the program's 175 changes,
120 changed only listed texts, 36 removed a maker's
name for a feature, part or format that was not on the list (such as JBL's TwistLock), and
1 changed no meaning ("3-sec" written as "3-second"). The other
18, in 13 tables, are not brand text:
9 remove, shorten or soften a claim that names no brand (such as "Reliable everyday laptop from a trusted
name." shortened to "Everyday laptop."), and 9 change a specification value (such as a
robot vacuum's "suction: 65 AW" changed to "not stated," and the graphene-enhanced rubber of the top-ranked Terravolt in
Running Shoes 2 written as plain rubber). Of these 18 changes,
two are on a top-ranked product, both on that Terravolt. In the
four tables kept in Table W8 of the Web Appendix whose prompts without brand
names name a brand of the study that made a part or a platform, that name was removed in the cleaning.

## Every Listed Text

Every text is listed in the table below, by table, with the brand of its product, its kind and the brand
that it identifies.

| Table | Product's brand | Text left in the names-hidden prompt | Kind | Points to |
|:------------------------|:---------------|:---------------------------------------------|:-------:|:---------------------------------------------|
| Backpacks 1 | The North Face | "FlexVent" | 3 | The North Face |
| Blenders 1 | Hamilton Beach | "wave-action system" | 3 | Hamilton Beach |
| Blenders 1 | Ninja | "Auto-iQ" | 3 | Ninja |
| Cameras 1 | Canon | "Dual Pixel CMOS AF II" | 3 | Canon |
| Cameras 1 | Fujifilm | "X-Trans" | 3 | Fujifilm |
| Cameras 1 | Fujifilm | "film simulation modes" | 3 | Fujifilm |
| Cameras 1 | Nikon | "EXPEED 6" | 3 | Nikon |
| Cameras 1 | Sony | "Real-time Eye AF" | 3 | Sony |
| Cameras 1 | Canon | "the manufacturer reliability + lens ecosystem" | 4 | Canon |
| Coffee makers 1 | Cuisinart | "Brew Strength Control" | 3 | Cuisinart |
| Coffee makers 1 | Keurig | "K-Cup" | 3 | Keurig |
| Coffee makers 2 | Philips | "LatteGo" | 2 | Philips |
| Coffee makers 2 | Breville | "ThermoJet" | 3 | Breville |
| Coffee makers 2 | Nespresso | "Centrifusion" | 3 | Nespresso |
| Coffee makers 3 | Keurig | "K-Cup" | 3 | Keurig |
| Earbuds 1 | Samsung | "Galaxy AI" | 2 | Samsung |
| Earbuds 1 | Apple | "H2 chip" | 3 | Apple |
| Earbuds 1 | Apple | "MagSafe" | 3 | Apple |
| Earbuds 1 | Jabra | "HearThrough" | 3 | Jabra |
| Earbuds 1 | Jabra | "MySound" | 3 | Jabra |
| Earbuds 1 | Samsung | "360 Audio" | 3 | Samsung |
| Earbuds 1 | Samsung | "SSC" | 3 | Samsung |
| Earbuds 1 | Sony | "V2 processor" | 3 | Sony |
| Earbuds 1 | Apple | "Deep the manufacturer ecosystem integration" | 4 | Apple |
| Earbuds 1 | Auralis | "Qualcomm aptX Lossless" | 5 | Qualcomm (a component) |
| Earbuds 2 | Apple | "MagSafe" | 3 | Apple |
| Earbuds 2 | JBL | "Pure Bass" | 3 | JBL |
| Earbuds 2 | Samsung | "SmartThings Find" | 3 | Samsung |
| Earbuds 2 | Sonance | "QuietSmart 3.0" | 3 | EarFun (the real maker of the product marked as best in the table) |
| Earbuds 2 | Google | "the manufacturer Assistant built-in" | 4 | Google |
| Earbuds 2 | JBL | "the manufacturer Pure Bass" | 4 | JBL |
| Earbuds 2 | Samsung | "the manufacturer value entry" | 4 | Samsung |
| Earbuds 3 | Beats | "Apple H1 chip" | 1 | Apple (the owner of Beats) |
| Earbuds 3 | JBL | "TwistLock + FlexSoft" | 3 | JBL |
| Earbuds 3 | Shokz | "DualPitch" | 3 | Shokz |
| Earbuds 3 | Sony | "Extra Bass" | 3 | Sony |
| Electric toothbrushes 1 | Oral-B | "3D cleaning action" | 3 | Oral-B |
| Electric toothbrushes 1 | Oral-B | "Linear magnetic drive" | 3 | Oral-B |
| Electric toothbrushes 1 | Oral-B | "cross-action brush head" | 3 | Oral-B |
| External drives 1 | Seagate | "Rescue Data Recovery" | 3 | Seagate |
| Headphones 1 | Bose | "Immersive Audio, CustomTune" | 3 | Bose |
| Headphones 1 | Bose | "Legendary the manufacturer comfort" | 4 | Bose |
| Headphones 2 | Beats | "Apple spatial audio" | 1 | Apple (the owner of Beats) |
| Headphones 2 | Bose | "SimpleSync" | 3 | Bose |
| Headphones 2 | JBL | "Pure Bass" | 3 | JBL |
| Headphones 2 | Sony | "DSEE" | 3 | Sony |
| Headphones 2 | Sony | "Dual Noise Sensor" | 3 | Sony |
| Headphones 2 | Beats | "Iconic the manufacturer styling" | 4 | Beats |
| Headphones 2 | Bose | "the manufacturer SimpleSync" | 4 | Bose |
| Headphones 2 | JBL | "the manufacturer Pure Bass" | 4 | JBL |
| Headphones 2 | Sony | "the manufacturer reliability" | 4 | Sony |
| Headphones 3 | Beyerdynamic | "STELLAR.45" | 3 | Beyerdynamic |
| Headphones 3 | Bose | "the manufacturer Music app" | 4 | Bose |
| Keyboards 1 | HyperX | "HyperX Red" | 1 | HyperX |
| Keyboards 1 | Logitech | "Logi Bolt" | 1 | Logitech |
| Keyboards 1 | Razer | "Razer Green" | 1 | Razer |
| Keyboards 1 | Corsair | "iCUE" | 3 | Corsair |
| Keyboards 1 | Razer | "Chroma RGB" | 3 | Razer |
| Keyboards 1 | HyperX | "the manufacturer Red switches" | 4 | HyperX |
| Keyboards 1 | Razer | "the manufacturer Green switches" | 4 | Razer |
| Keyboards 1 | Corsair | "Cherry MX Red" | 5 | Cherry (a component) |
| Keyboards 1 | Keystrike | "Cherry MX compatible" | 5 | Cherry (a component) |
| Laptops 1 | HP | "the manufacturer+ subscription trial" | 4 | HP |
| Laptops 2 | Apple | "Apple M2" | 1 | Apple |
| Laptops 2 | Apple | "Liquid Retina" | 3 | Apple |
| Laptops 2 | Dell | "InfinityEdge" | 3 | Dell |
| Laptops 2 | Apple | "the manufacturer M2" | 4 | Apple |
| Laptops 3 | HP | "the manufacturer brand reliability" | 4 | HP |
| Laptops 3 | Acer | "Chrome OS" | 5 | Google (an operating system) |
| Monitors 1 | Samsung | "DeX" | 3 | Samsung |
| Monitors 1 | Samsung | "Tizen" | 3 | Samsung |
| Monitors 1 | Dell | "the manufacturer reliability" | 4 | Dell |
| Monitors 1 | LG | "Affordable the manufacturer quality" | 4 | LG |
| Monitors 1 | LG | "AMD FreeSync" | 5 | AMD (a component) |
| Portable speakers 1 | Bose | "N/A (Bose)" | 1 | Bose |
| Portable speakers 1 | Bose | "PositionIQ" | 3 | Bose |
| Portable speakers 1 | JBL | "PartyBoost" | 3 | JBL |
| Portable speakers 1 | Sony | "Sound Diffusion Processor" | 3 | Sony |
| Portable speakers 1 | Ultimate Ears | "outdoor boost mode" | 3 | Ultimate Ears |
| Portable speakers 1 | Wavecrest | "XBass boost" | 3 | Tribit (the real maker of the product marked as best in the table) |
| Portable speakers 1 | Bose | "the manufacturer Connect app" | 4 | Bose |
| Portable speakers 1 | JBL | "the manufacturer Pro Sound" | 4 | JBL |
| Robot vacuums 1 | Dyson | "Hyperdymium" | 3 | Dyson |
| Robot vacuums 1 | Shark | "Matrix Clean" | 3 | Shark |
| Robot vacuums 1 | iRobot | "Clean Base" | 3 | iRobot |
| Robot vacuums 1 | iRobot | "PrecisionVision" | 3 | iRobot |
| Robot vacuums 1 | Dyson | "the manufacturer Hyperdymium motor" | 4 | Dyson |
| Robot vacuums 1 | iRobot | "the manufacturer OS" | 4 | iRobot |
| Running shoes 1 | New Balance | "Fresh Foam X" | 2 | New Balance |
| Running shoes 1 | ASICS | "FF BLAST PLUS" | 3 | ASICS |
| Running shoes 1 | ASICS | "PureGEL" | 3 | ASICS |
| Running shoes 1 | Adidas | "BOOST" | 3 | Adidas |
| Running shoes 1 | Adidas | "Continental rubber" | 3 | Adidas (Continental running outsoles are made only for Adidas) |
| Running shoes 1 | Adidas | "Primeknit+" | 3 | Adidas |
| Running shoes 1 | New Balance | "Hypoknit" | 3 | New Balance |
| Running shoes 1 | Nike | "ReactX" | 3 | Nike |
| Running shoes 1 | Nike | "Zoom Air" | 3 | Nike |
| Running shoes 1 | Nike | "Classic the manufacturer running shoe" | 4 | Nike |
| Running shoes 1 | Stridewell | "Vibram outsole" | 5 | Vibram (a component) |
| Running shoes 2 | Brooks | "DNA LOFT v2" | 3 | Brooks |
| Running shoes 2 | Brooks | "TrailTack" | 3 | Brooks |
| Running shoes 2 | Brooks | "pivot post system" | 3 | Brooks |
| Running shoes 2 | Nike | "React foam" | 3 | Nike |
| Running shoes 2 | Salomon | "Contagrip MA" | 3 | Salomon |
| Running shoes 2 | Salomon | "EnergyCell+" | 3 | Salomon |
| Running shoes 2 | Salomon | "SensiFit" | 3 | Salomon |
| Running shoes 2 | HOKA | "Vibram Megagrip" | 5 | Vibram (a component) |
| Running shoes 3 | ASICS | "FF TURBO PLUS" | 3 | ASICS |
| Running shoes 3 | Adidas | "Continental rubber" | 3 | Adidas (Continental running outsoles are made only for Adidas) |
| Running shoes 3 | Adidas | "EnergyRods 2.0" | 3 | Adidas |
| Running shoes 3 | Adidas | "Lightstrike Pro" | 3 | Adidas |
| Running shoes 3 | Nike | "ZoomX" | 3 | Nike |
| Running shoes 3 | Saucony | "PWRRUN PB" | 3 | Saucony |
| Running shoes 3 | Saucony | "speedroll" | 3 | Saucony |
| Smartphones 1 | Samsung | "Galaxy AI" | 2 | Samsung |
| Smartphones 1 | Apple | "A16 Bionic" | 3 | Apple |
| Smartphones 1 | Apple | "Super Retina XDR" | 3 | Apple |
| Smartphones 1 | Apple | "iOS" | 3 | Apple |
| Smartphones 1 | Google | "Tensor G3" | 3 | Google |
| Smartphones 1 | OnePlus | "SUPERVOOC" | 3 | OnePlus (the OPPO group) |
| Smartphones 1 | Samsung | "Dynamic AMOLED" | 3 | Samsung |
| Smartphones 1 | OnePlus | "Sony IMX890" | 5 | Sony (a component) |
| Smartphones 1 | Veridian | "Sony IMX890" | 5 | Sony (a component) |
| Smartphones 2 | Apple | "A15 Bionic" | 3 | Apple |
| Smartphones 2 | Apple | "Retina HD" | 3 | Apple |
| Smartphones 2 | Apple | "iOS" | 3 | Apple |
| Smartphones 2 | Google | "Pure Android" | 3 | Google |
| Smartphones 2 | Google | "Tensor G2" | 3 | Google |
| Smartphones 2 | Motorola | "TurboPower" | 3 | Motorola |
| Smartphones 2 | Samsung | "Exynos 1380" | 3 | Samsung |
| Smartphones 2 | Samsung | "Super AMOLED" | 3 | Samsung |
| Smartphones 3 | Apple | "A15 Bionic" | 3 | Apple |
| Smartphones 3 | Apple | "Super Retina XDR" | 3 | Apple |
| Smartphones 3 | Apple | "iOS 17" | 3 | Apple |
| Smartphones 3 | Aurem | "HyperCharge" | 3 | Xiaomi (the real maker of the product marked as best in the table) |
| Smartphones 3 | Google | "Tensor G2" | 3 | Google |
| Smartphones 3 | Samsung | "Exynos 1380" | 3 | Samsung |
| Smartphones 3 | Samsung | "Super AMOLED" | 3 | Samsung |
| Smartphones 3 | Samsung | "good the manufacturer ecosystem" | 4 | Samsung |
| Smartwatches 1 | Fitbit | "Google integration" | 1 | Google (the owner of Fitbit) |
| Smartwatches 1 | Apple | "iPhone" | 2 | Apple |
| Smartwatches 1 | Apple | "S9 SiP" | 3 | Apple |
| Smartwatches 1 | Apple | "always-on Retina" | 3 | Apple |
| Smartwatches 1 | Fitbit | "cEDA" | 3 | Fitbit |
| Smartwatches 1 | Garmin | "Body Battery" | 3 | Garmin |
| Smartwatches 1 | Samsung | "BioActive" | 3 | Samsung |
| Smartwatches 1 | Samsung | "Exynos W930" | 3 | Samsung |
| Smartwatches 1 | Garmin | "the manufacturer Pay" | 4 | Garmin |
| Smartwatches 1 | Samsung | "Wear OS" | 5 | Google (an operating system) |
| Tablets 1 | Apple | "Pencil (1st gen)" | 2 | Apple |
| Tablets 1 | Samsung | "S Pen" | 2 | Samsung (its stylus line) |
| Tablets 1 | Amazon | "Alexa" | 3 | Amazon |
| Tablets 1 | Apple | "A14 Bionic" | 3 | Apple |
| Tablets 1 | Apple | "Liquid Retina" | 3 | Apple |
| Tablets 1 | Samsung | "Exynos 1380" | 3 | Samsung |
| Tablets 1 | Apple | "the manufacturer Pencil" | 4 | Apple |
| Tablets 1 | Lenovo | "JBL" | 5 | JBL (a component) |
| Televisions 1 | Samsung | "Crystal UHD" | 2 | Samsung |
| Televisions 1 | LG | "ThinQ AI" | 3 | LG |
| Televisions 1 | LG | "a7 Gen6 AI Processor" | 3 | LG |
| Televisions 1 | LG | "webOS 23" | 3 | LG |
| Televisions 1 | Samsung | "Crystal Processor 4K" | 3 | Samsung |
| Televisions 1 | Samsung | "Smart Hub with Gaming Hub" | 3 | Samsung |
| Televisions 1 | Sony | "Motionflow XR 240" | 3 | Sony |
| Televisions 1 | Sony | "X1 processor" | 3 | Sony |
| Televisions 1 | Vistara | "Game Accelerator 240" | 3 | TCL (the real maker of the product marked as best in the table) |
| Televisions 1 | Vizio | "SmartCast" | 3 | Vizio |
| Televisions 1 | Vizio | "V-Gaming Engine" | 3 | Vizio |
| Televisions 1 | Samsung | "the manufacturer ecosystem" | 4 | Samsung |
| Televisions 1 | LG | "Apple AirPlay 2" | 5 | Apple (a platform) |
| Televisions 1 | Sony | "Google TV, Apple AirPlay" | 5 | Google and Apple (platforms) |
| Televisions 2 | LG | "4K QNED" | 2 | LG |
| Televisions 2 | Samsung | "Neo QLED" | 2 | Samsung |
| Televisions 2 | LG | "Quantum Dot + NanoCell" | 3 | LG |
| Televisions 2 | LG | "a7 Gen6 AI Processor" | 3 | LG |
| Televisions 2 | Samsung | "Neural Quantum Processor" | 3 | Samsung |
| Televisions 2 | Samsung | "Object Tracking Sound" | 3 | Samsung |
| Televisions 2 | Sony | "Acoustic Multi-Audio" | 3 | Sony |
| Televisions 2 | Sony | "XR Processor" | 3 | Sony |
| Televisions 2 | Sony | "XR Triluminos Pro" | 3 | Sony |
| Televisions 2 | Vistara | "Google TV" | 5 | Google (a platform) |
| Televisions 3 | Insignia | "Amazon house brand" | 1 | Amazon (the product is listed under Insignia in the table) |
| Televisions 3 | LG | "a5 Gen5 AI Processor" | 3 | LG |
| Televisions 3 | LG | "webOS 22" | 3 | LG |
| Televisions 3 | Samsung | "Crystal Processor 4K, PurColor" | 3 | Samsung |
| Televisions 3 | Vizio | "Quantum Color" | 3 | Vizio |
| Televisions 3 | Vizio | "SmartCast" | 3 | Vizio |
| Televisions 3 | Insignia | "Fire TV, Alexa" | 5 | Amazon (a platform on another maker's television) |
| Televisions 3 | LG | "AirPlay 2" | 5 | Apple (a platform) |
| Televisions 3 | Pixelight | "Google TV" | 5 | Google (a platform) |
| Water bottles 1 | Hydro Flask | "TempShield" | 3 | Hydro Flask |
| Water bottles 1 | Yeti | "No Sweat design" | 3 | Yeti |
| Wireless routers 1 | Linksys | "Velop" | 2 | Linksys (its mesh product line) |
| Wireless routers 1 | ASUS | "AiMesh, AiProtection Pro" | 3 | ASUS |
| Wireless routers 1 | Netweave | "HomeShield" | 3 | TP-Link (the real maker of the product marked as best in the table) |
| Wireless routers 1 | Netgear | "the manufacturer Armor security" | 4 | Netgear |

Table: Every Listed Text, by Table
