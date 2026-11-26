# The dominant sets: every change from the scrubbed corpus tables

Written by `show_dominant_changes.py` from `dominant_sets.py`. Letters are the corpus's letters (before the letters are shuffled for each trial); * marks the designated best product. Prices are set by the price ladder of `tables.py` and are not listed.

- Left out: sr_portable_speakers_01: to be lighter than the 274 g Sony speaker while matching the 30 W JBL speaker and the 16-hour Sony battery, the best speaker would need figures no speaker of that kind has.
- Left out: sr_keyboards_01: every displayed attribute (switches, connection, layout, features) has no order, so held equal the five keyboards would differ only in price, and at the equal-price rung the cheapest other keyboard would be as good as the best one.
- Left out: sr_coffee_makers_02: to match the super-automatic machine's grinder and automatic frother the best espresso machine would need both at 120 dollars or less, which no machine of that kind offers (the second reading, finding 3).
- Left out: sr_water_bottles_01: to be lighter than the 12.3-ounce S'well (a 25-ounce bottle) the best 32-ounce insulated steel bottle would need a weight no bottle of that size has (the review of every improved figure).

## sr_laptops_01

held equal: no order:

- C cpu: 'Ryzen 5 7530U' -> 'i5-1335U'
- D cpu: 'Ryzen 7 7730U' -> 'i5-1335U'
- E* cpu: 'Ryzen 7 7840U' -> 'i5-1335U'
- C display: '15.6" FHD IPS' -> '15.6" FHD'
- D display: '15.6" FHD OLED' -> '15.6" FHD'
- E* display: '14" 2.8K OLED' -> '15.6" FHD'

## sr_laptops_02

removed: one value for all five would contradict what a named brand makes (an AMD processor in the Apple laptop):

- A cpu: 'Ryzen 7 7840U' -> None
- B cpu: '8-core ARM chip' -> None
- C cpu: 'Core Ultra 5 125U' -> None
- D* cpu: 'Ryzen 7 7840U' -> None
- E cpu: 'Core Ultra 7 155U' -> None

removed: one value for all five would contradict what a named brand makes (an OLED screen on the Apple laptop):

- A display: '14" 2.8K OLED' -> None
- B display: '13.6" IPS' -> None
- C display: '14" FHD+ touch' -> None
- D* display: '16" 2.8K OLED' -> None
- E display: '13.4" FHD+' -> None

## sr_laptops_03

held equal: no order:

- B cpu: 'i5-1235U' -> 'Ryzen 5 7520U'
- C* cpu: 'i7-1195G7' -> 'Ryzen 5 7520U'
- D cpu: 'Ryzen 5 5625U' -> 'Ryzen 5 7520U'
- E cpu: 'Ryzen 3 7320C' -> 'Ryzen 5 7520U'
- C* display: '13.3" 2K IPS touch' -> '15.6" FHD'
- E display: '14" FHD IPS touch' -> '15.6" FHD'

## sr_smartphones_01

held equal: no order:

- B display: '6.2" AMOLED 120Hz' -> '6.1" OLED'
- C display: '6.2" OLED 120Hz' -> '6.1" OLED'
- D display: '6.78" LTPO AMOLED 120Hz' -> '6.1" OLED'
- E* display: '6.7" LTPO AMOLED 120Hz' -> '6.1" OLED'

best product raised:

- E* camera: '50MP dual OIS' -> '50MP triple OIS'

## sr_smartphones_02

held equal: no order:

- B display: '6.7" OLED 144Hz' -> '6.4" AMOLED 120Hz'
- C* display: '6.7" LTPO OLED 144Hz' -> '6.4" AMOLED 120Hz'
- D display: '6.1" OLED 90Hz' -> '6.4" AMOLED 120Hz'
- E display: '4.7" LCD' -> '6.4" AMOLED 120Hz'

## sr_smartphones_03

best product raised:

- B* camera: '200MP OIS' -> '200MP triple OIS'

## sr_tvs_01

held equal: no order:

- B panel: 'IPS' -> 'VA'
- D* panel: 'QLED VA' -> 'VA'
- A hdr: 'HDR10+' -> 'HDR10'
- C hdr: 'HDR10/HLG' -> 'HDR10'
- D* hdr: 'Dolby Vision IQ/HDR10+' -> 'HDR10'

## sr_tvs_02

removed: one value for all five would contradict what a named brand makes (Dolby Vision on the Samsung television):

- A hdr: 'HDR10+' -> None
- B hdr: 'Dolby Vision/HDR10' -> None
- C* hdr: 'Dolby Vision IQ/HDR10+' -> None
- D hdr: 'Dolby Vision/HDR10' -> None
- E hdr: 'Dolby Vision/HDR10+' -> None

held equal: no order:

- B panel: 'Quantum Dot LED' -> 'Mini-LED QLED'
- C* panel: 'Mini-LED Quantum Dot' -> 'Mini-LED QLED'
- D panel: 'Full Array LED' -> 'Mini-LED QLED'
- E panel: 'Mini LED' -> 'Mini-LED QLED'

## sr_tvs_03

held equal: no order:

- C panel: 'IPS' -> 'VA'
- B* hdr: 'Dolby Vision/HDR10+' -> 'HDR10'
- D hdr: 'Dolby Vision/HDR10+' -> 'HDR10'

best product raised:

- B* refresh: '60Hz' -> '120Hz'

## sr_headphones_01

held equal: no order:

- A driver: '30mm' -> '40mm'
- B driver: '35mm' -> '40mm'
- C driver: '42mm' -> '40mm'

best product raised:

- E* codec: 'LDAC/AAC' -> 'LDAC/aptX Adaptive/aptX/AAC/SBC'

## sr_headphones_02

held equal: no order:

- A type: 'on-ear' -> 'over-ear'
- D driver: '30mm' -> '40mm'
- E driver: '35mm' -> '40mm'

best product raised:

- C* weight: '235g' -> '190g'
- C* codec: 'LDAC/AAC' -> 'LDAC/AAC/SBC'

## sr_headphones_03

held equal: no order:

- C* type: 'over-ear open-back' -> 'over-ear'
- D type: 'over-ear open-back' -> 'over-ear'
- B driver: '45mm' -> '40mm'
- C* driver: 'planar magnetic 80mm' -> '40mm'
- D driver: '45mm dynamic' -> '40mm'
- B impedance: '38 ohm' -> '47 ohm'
- C* impedance: '37 ohm' -> '47 ohm'
- D impedance: '48 ohm' -> '47 ohm'
- E impedance: '22 ohm' -> '47 ohm'

best product raised:

- C* battery: 'wired only' -> '60 hours'
- C* codec: 'N/A (wired)' -> 'LDAC/aptX/AAC/SBC'
- C* connection: None -> 'wireless and wired'

## sr_running_shoes_01

held equal: no order:

- B cushioning: 'TPU-bead foam' -> 'EVA-blend foam'
- D cushioning: 'EVA foam' -> 'EVA-blend foam'
- E* cushioning: 'PEBA supercritical foam' -> 'EVA-blend foam'
- C drop: '8mm' -> '10mm'
- D drop: '6mm' -> '10mm'
- E* drop: '5mm' -> '10mm'

## sr_running_shoes_02

held equal: no order:

- B terrain: 'soft trail/mud' -> 'trail/road'
- C terrain: 'technical trail' -> 'trail/road'
- D* terrain: 'all trail' -> 'trail/road'
- E terrain: 'trail' -> 'trail/road'
- C drop: '4mm' -> '10mm'
- D* drop: '6mm' -> '10mm'
- E drop: '8mm' -> '10mm'
- C traction: 'sticky rubber lugs' -> 'rubber lugs'
- D* traction: 'rubber compound' -> 'rubber lugs'
- E traction: 'sticky rubber' -> 'rubber lugs'

## sr_running_shoes_03

held equal: no order:

- B drop: '6mm' -> '8mm'
- C* drop: '6mm' -> '8mm'
- D drop: '5mm' -> '8mm'

## sr_coffee_makers_01

removed: one value for all five would contradict what a named brand makes (one brewing temperature for pod and drip makers):

- A brew_temp: '192F' -> None
- B brew_temp: '185F' -> None
- C brew_temp: '190F' -> None
- D brew_temp: '197-204F (PID)' -> None
- E* brew_temp: '195-205F (adjustable)' -> None

removed: one value for all five would contradict what a named brand makes (a one-minute brew on every drip maker):

- A brew_time: '1 min' -> None
- B brew_time: '8 min' -> None
- C brew_time: '10 min' -> None
- D brew_time: '7 min' -> None
- E* brew_time: '5 min' -> None

held equal: no order:

- A type: 'single-serve pod' -> 'drip'
- D type: 'drip precision' -> 'drip'
- E* type: 'pour-over auto' -> 'drip'
- A capacity: '75oz reservoir' -> '12 cups'
- C capacity: '14 cups' -> '12 cups'
- E* capacity: '8 cups' -> '12 cups'

## sr_coffee_makers_03

removed: one value for all five would contradict what a named brand makes (a pod AeroPress and a pod French press):

- A type: 'pod single-serve' -> None
- B type: 'manual press' -> None
- C* type: 'manual espresso' -> None
- D type: 'capsule' -> None
- E type: 'french press' -> None

removed: one value for all five would contradict what a named brand makes (a manual temperature on the pod makers):

- A brew_temp: '192F' -> None
- B brew_temp: 'manual' -> None
- C* brew_temp: 'manual' -> None
- D brew_temp: 'auto' -> None
- E brew_temp: 'manual' -> None

best product raised:

- C* weight: '12 oz' -> '11 oz'

## sr_earbuds_01

removed: one product lists its maker's own codec, which no other product can hold (the second reading, finding 1):

- A codec: 'AAC' -> None
- B codec: 'proprietary/AAC' -> None
- C codec: 'LDAC/AAC' -> None
- D* codec: 'aptX Lossless/AAC' -> None
- E codec: 'AAC/SBC' -> None

held equal: no order:

- D* anc: '-45dB' -> 'adaptive'
- E anc: 'adjustable' -> 'adaptive'

## sr_earbuds_02

removed: one value for all five would contradict what a named brand makes (noise cancelling on the AirPods that have none):

- A anc: 'basic' -> None
- B anc: 'active' -> None
- C* anc: '-50dB' -> None
- D anc: 'none' -> None
- E anc: 'none' -> None

best product raised:

- C* codec: 'aptX Adaptive/LDAC/AAC' -> 'aptX Adaptive/LDAC/AAC/SBC'

## sr_earbuds_03

removed: one value for all five would contradict what a named brand makes (wingtips on the bone-conduction Shokz):

- A fit: 'ear wing' -> None
- B fit: 'twist-in' -> None
- C fit: 'bone conduction' -> None
- D* fit: 'ear-hook open' -> None
- E fit: 'ear fin' -> None

best product raised:

- D* ip_rating: 'IPX8' -> 'IP68'

## sr_smartwatches_01

held equal: no order:

- B gps: 'L1+L5' -> 'L1'
- C gps: 'multi-band' -> 'L1'
- D* gps: 'dual-band 5-system' -> 'L1'
- E gps: 'built-in' -> 'L1'
- A display: 'always-on OLED' -> 'AMOLED'
- D* display: 'always-on AMOLED 1.39"' -> 'AMOLED'
- B sensors: 'multi-sensor/ECG' -> 'SpO2/ECG/temp'
- C sensors: 'SpO2/nap/energy score' -> 'SpO2/ECG/temp'
- D* sensors: 'SpO2/HR/temp/altitude' -> 'SpO2/ECG/temp'
- E sensors: 'ECG/stress/SpO2' -> 'SpO2/ECG/temp'

## sr_robot_vacuums_01

removed: pascals for four products, air watts for one, so no order:

- A suction: '2200Pa' -> None
- B suction: '2500Pa' -> None
- C* suction: '7000Pa' -> None
- D suction: 'not stated' -> None
- E suction: '1300Pa' -> None

removed: one value for all five would contradict what a named brand makes (a camera on the bounce robot):

- A navigation: 'camera + AI' -> None
- B navigation: 'LiDAR 360' -> None
- C* navigation: 'LiDAR + 3D AI' -> None
- D navigation: 'camera' -> None
- E navigation: 'bounce' -> None

held equal: no order:

- A emptying: 'auto (30 bags)' -> 'manual'
- B emptying: 'auto (30 days)' -> 'manual'
- C* emptying: 'auto + self-wash/dry' -> 'manual'

## sr_external_ssds_01

best product raised:

- C* durability: 'IP68, MIL-STD-810G' -> 'IP68, 3m drop'

## sr_electric_toothbrushes_01

removed: sonic and oscillating brushes are two kinds with no order:

- A type: 'oscillating' -> None
- B type: 'sonic' -> None
- C* type: 'sonic' -> None
- D type: 'sonic' -> None
- E type: 'oscillating' -> None

removed: sonic strokes and oscillating rotations are counted in different units:

- A strokes: 'N/A (oscillating)' -> None
- B strokes: '31,000/min' -> None
- C* strokes: '42,000/min' -> None
- D strokes: '15,000/min' -> None
- E strokes: '8,800 rotations/min' -> None

removed: a disposable AAA battery has no charge life to compare (the second reading, finding 5):

- D battery: '3 months (AAA)' -> None

held equal: no order:

- A modes: '5' -> '1'
- C* modes: '6' -> '1'

## sr_backpacks_01

held equal: no order:

- A capacity: '28L' -> '26L'
- C capacity: '20L' -> '26L'
- E capacity: '30L' -> '26L'
- C material: 'recycled 210D nylon' -> '600D polyester'
- D* material: '500D CORDURA' -> '600D polyester'
- E material: 'polyester' -> '600D polyester'

best product raised:

- D* weight: '1.1kg' -> '0.35kg'

## sr_blenders_01

held equal: no order:

- B capacity: '72oz' -> '48oz'
- C* capacity: '64oz' -> '48oz'
- D capacity: '56oz' -> '48oz'
- E capacity: '40oz' -> '48oz'
- B speeds: '3 + auto programs' -> 'variable 1-10'
- C* speeds: 'variable + pulse' -> 'variable 1-10'
- D speeds: '5 + pulse' -> 'variable 1-10'
- E speeds: '12 functions' -> 'variable 1-10'
- B blade: 'stacked blade' -> 'stainless steel'
- D blade: 'asymmetric' -> 'stainless steel'

## sr_wireless_routers_01

No change.

## sr_monitors_01

removed: HDR1000, stated only for the best monitor, needs the Mini-LED panel that the held-equal panel row no longer shows (the second reading, finding 4):

- C* hdr: 'HDR1000' -> None

held equal: no order:

- E size: '32"' -> '27"'
- C* panel: 'Mini-LED IPS' -> 'IPS'
- E panel: 'VA' -> 'IPS'
- B color: '98% sRGB' -> '99% sRGB'
- C* color: '99% DCI-P3 (>100% sRGB)' -> '99% sRGB'
- D color: '100% sRGB, Delta E<2' -> '99% sRGB'

## sr_tablets_01

held equal: no order:

- B display: '10.9" TFT' -> '10.9" IPS'
- C* display: '11" 2.8K IPS 144Hz' -> '10.9" IPS'
- D display: '11" 2K' -> '10.9" IPS'
- E display: '12.7" 2K IPS' -> '10.9" IPS'
- A processor: 'hexa-core' -> 'octa-core'
- C* processor: 'Snapdragon 870' -> 'octa-core'
- E processor: 'Dimensity 7050' -> 'octa-core'

## sr_cameras_01

held equal: no order:

- B af: '425 phase-detect' -> 'hybrid phase-detect AF'
- C af: '425 point hybrid' -> 'hybrid phase-detect AF'
- D* af: '1053 point cross-type' -> 'hybrid phase-detect AF'
- E af: '209 hybrid AF' -> 'hybrid phase-detect AF'

