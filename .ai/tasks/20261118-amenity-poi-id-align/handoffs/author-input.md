# Author input

User comment, verbatim:

business_sector lấy từ slv_pn_business_services. slv_pn_business_services join với slv_pn_business_service_i18ns qua slv_pn_business_service_i18ns.business_service_id = slv_pn_business_services.id và slv_pn_business_service_i18ns.locale = 'vi'. Khớp từ điển thì lấy amenity_group của dòng từ điển. Không khớp thì dùng specialty_tags. Một nhãn khớp nhiều dòng từ điển partner thì dừng notebook, không ghi.

Accepted rows: `decision.md` `D-11` and `D-12`, plus `D-2` for `poi_id = uuid_md5(id, 'partner')`.

## Read

- `decision.md`: `Quyết định hiện hành`, `D-2`, `D-11`, `D-12`
- `notebooks/NB_SLV_POI_AMENITY.ipynb` cell `d1amenbuild`
- `notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb` cell `b1entitybuild`, function `_partner`
- `notebooks/NB_GLD_SRV_POI_AMENITY.ipynb` cell `srvamenitybuild`
- `docs/context/mapping_gld_srv_poi_amenity.md`

## Constraints

- Read only `$.facilities.specialty_tags`. Locale `vi` first; if that value is null, use the service row.
- Left join partner dictionary on `amenity_raw`. On a match, `amenity_group`, `amenity`, `amenity_en`, `amenity_vi`, and `service_flags` come from that row. On no match, still emit the label with `amenity_group = specialty_tags` and those four columns null.
- More than one partner dictionary row for one label: stop the notebook and do not write.
- `business_sector` comes from `slv_pn_business_services` through the join above. Do not invent a filler for null or blank. If the named files already block a NULL MERGE key, cite that. Otherwise ask.
- Keep google rows, the info filter, the grain, and the gold 1-1 copy.
- Close Conflicts 3, 4, and 5 from the previous model. Do not leave them open.
