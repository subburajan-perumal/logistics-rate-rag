# Rate Policy Note — 2026 H2

- Applies to: all ten carrier tariffs in this corpus (MER, HAL, BOR, COR, TES, SOL, KES, ALD, VAN, QUI)
- Effective: 2026-07-01 to 2026-12-31
- Document type: policy

## Scope

This note governs how the FCL ocean freight tariffs of Meridian Ocean Lines (MERIDIAN), Halcyon Container Line (HALCYON), Boreal Shipping (BOREAL), Corvid Line (CORVID), Tessera Maritime (TESSERA), Solstice Container Lines (SOLSTICE), Kestrel Ocean (KESTREL), Aldermoor Line (ALDERMOOR), Vantor Shipping (VANTOR) and Quillon Marine (QUILLON) are to be read and quoted. Where a tariff and this note disagree, the tariff's own header lines prevail for that tariff.

## Bunker Adjustment Factor (BAF)

Meridian, Boreal, Tessera, Solstice, Aldermoor and Vantor include the Bunker Adjustment Factor in every base rate; no separate BAF is added. Halcyon, Corvid, Kestrel and Quillon do not include it: their CSV tariffs quote BAF on each line in the baf column, in the currency of the baf_currency column, which is USD and may differ from the base rate's currency. A BAF may be added to a base rate only when both are in the same currency.

## Currency

Every tariff line states its own currency: the Currency column in the Meridian, Boreal, Tessera, Solstice, Aldermoor and Vantor tariffs, and the currency field in the Halcyon, Corvid, Kestrel and Quillon CSV tariffs. One carrier may quote different trades in different currencies (USD, EUR or GBP). Quote a rate only in the currency of its own line. Never convert a rate into another currency, and never add figures in different currencies.

## Terminal Handling Charges

All base rates of every carrier exclude Origin Terminal Handling Charges (OTHC) and Destination Terminal Handling Charges (DTHC). Terminal handling is billed separately by the terminal and is not part of any figure in these tariffs.

## Validity and Expiry

A rate may be quoted only when the as-of date of the enquiry falls within its tariff's validity window, from the Valid from date to the Valid to date inclusive. A tariff marked SUPERSEDED must never be quoted as current, even if the enquiry names it. MER-2026-Q2-FCL was superseded by MER-2026-H2-FCL on 2026-07-01, and SOL-2026-Q2-FCL by SOL-2026-H2-FCL on the same date. TES-2026-H2-FCL is valid from 2026-08-01 to 2027-01-31.

## Container Types

Equipment codes used in the tariffs: 20DRY 20-foot standard dry (ISO 22G1); 40DRY 40-foot standard dry (42G1); 40HC 40-foot high cube (45G1); 45HC 45-foot high cube (L5G1); 20FR and 40FR flat rack (22P1, 42P1); 20OT and 40OT open top (22U1, 42U1); 20RF 20-foot reefer (22R1); 40RH 40-foot reefer high cube (45R1); 40NOR 40-foot non-operating reefer, a reefer high cube shipped with its refrigeration unit switched off and carrying dry cargo, priced separately from both 40RH and 40HC; 20TK and 40TK 20-foot and 40-foot tank.

A dash in a tariff table cell, or the absence of a line in a CSV tariff, means the carrier does not offer that equipment on that lane. There is no rate for it, and no rate may be substituted from another equipment type.

## Quoting Rules

Quote one lane, one carrier, one container type at a time. Never quote one equipment type's rate for another, including a 40RH or 40HC rate for a 40NOR. Never average rates across lanes or carriers. Never combine one carrier's base rate with another carrier's surcharge. Hazardous cargo is excluded from all tariffs. Less-than-container-load (LCL) shipments are not covered.

## Peak Season Surcharge

Where a CSV tariff line's notes state a peak season surcharge, the surcharge is separate from the base rate, is in the currency stated in the note, and applies only to bookings from the stated date.

## Synthetic Notice

This corpus is invented for a portfolio project. Carrier names, tariff references, rates, surcharges and dates are fictional and do not describe any real carrier or contract. Port codes and names are real UN/LOCODEs.
