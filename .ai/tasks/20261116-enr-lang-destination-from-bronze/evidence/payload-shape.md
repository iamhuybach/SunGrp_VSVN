# Payload shape

Source file: `evidence/samples/brz_enrichment_result_lang_destination.tsv` (4 rows). Keys only. No values. This file does not assert Fabric column types, nullability, a MERGE key, or a watermark.

## Row columns

- event_id
- event_type
- schema_version
- poi_id
- lang
- version
- pipeline_version
- produced_at
- data
- EventProcessedUtcTime
- PartitionId
- EventEnqueuedUtcTime
- source

`lang` is empty on the DESTINATION sample row. `data` is a JSON string.

## data when event_type = LANG

- display
  - cost
    - text
    - label
  - best_time
    - text
    - label
  - time_to_spend
    - text
    - label
- district
- poi_name
- description
- experiences[]
  - title
  - keyword
  - description
- source_lang
- short_address
- translated_at
- review_summary

## data when event_type = DESTINATION

- resolve_mode
- request
  - address
- lat
- lng
- address
  - new
    - ward
      - name
      - gso_code
      - vietmap_id
      - name_with_type
    - district
    - province
      - name
      - gso_code
      - vietmap_id
      - name_with_type
    - dataset_version
    - formatted_address
  - old
    - ward
      - name
      - gso_code
      - vietmap_id
      - name_with_type
    - district
      - name
      - gso_code
      - vietmap_id
      - name_with_type
    - province
      - name
      - gso_code
      - vietmap_id
      - name_with_type
    - dataset_version
    - formatted_address
- destinations[]
  - id
  - kind
  - name
  - slug
  - level
  - status
  - strapi_document_id
- resolved_at

On the DESTINATION sample row, `address.new.district` is JSON null, so that row has no `name` or `name_with_type` under the new district. `address.old.district` is an object with the keys listed above. `destinations[].level` is JSON null on one element.
