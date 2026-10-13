# L1 amenity storage demo

Silver L1 stores the Google flag payload. It does not rename fields, drop `false`, or filter by sector. Those steps are silver L2, as described in `get_amenity.md`.

Grain: one row in `slv_3p_poi_amenity` per `poi_id`.

Column: `source_flags_json` string. The object keeps a key when the raw document has that key, including JSON null. A missing key stays missing, so L2 can tell "Google sent null" from "Google did not send the key".

```json
{
  "flags": {
    "reservable": null,
    "takeout": true,
    "servesBreakfast": false
  },
  "parkingOptions": {
    "freeStreetParking": true
  },
  "paymentOptions": null,
  "accessibilityOptions": null,
  "evChargeOptions": null,
  "fuelOptions": null
}
```

The three local raw samples contain 23 top-level flag-like keys. `parkingOptions`, `paymentOptions`, and `accessibilityOptions` are either an object or null. `evChargeOptions` and `fuelOptions` are null on all three samples. No flag value is copied into this note.

L2, later, flattens `flags` and the option objects to snake_case, then keeps only the tags required by `business_sector_rule.md` and `mapping_sector.md`.
