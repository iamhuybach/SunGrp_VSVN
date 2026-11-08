# Payload shape

One bronze row of `lh_vv_bronze.dbo.cms_raw_data`. This is not a schema contract. No sample values, URLs, signatures, proper names, or description text are recorded. A column or key that is not in the sample is `MISSING_EVIDENCE`. Do not infer a type that the sample line does not state. Delta types of the bronze columns are not in the request.

## Bronze columns on the sample row

| column | type stated for this row | Delta type |
|---|---|---|
| `event_id` | string | `MISSING_EVIDENCE` |
| `source_name` | string | `MISSING_EVIDENCE` |
| `type` | string | `MISSING_EVIDENCE` |
| `crawled_at` | string, ISO UTC | `MISSING_EVIDENCE` |
| `ingested_date` | date-shaped | `MISSING_EVIDENCE` |
| `raw_payload` | JSON string | `MISSING_EVIDENCE` |

`type` is only a bronze column name here. One value does not establish that it is `language_code` or an entity type.

## Not on the sample row

`MISSING_EVIDENCE`: `before`, `after`, `op`, `source.schema`, `source.table`, `source_id`, `normalized_payload`, `language_code`.

## `raw_payload` after parse

| path | JSON type on this row |
|---|---|
| `$` | object |
| `id` | number |
| `documentId` | string |
| `createdAt` | string |
| `updatedAt` | string |
| `publishedAt` | string |
| `locale` | string |
| `name` | string |
| `description` | string |
| `slug` | string |
| `cover_gallery` | array of object |
| `cover_gallery[].id` | number |
| `cover_gallery[].documentId` | string |
| `cover_gallery[].name` | string |
| `cover_gallery[].alternativeText` | null |
| `cover_gallery[].caption` | null |
| `cover_gallery[].width` | number |
| `cover_gallery[].height` | number |
| `cover_gallery[].formats` | object |
| `cover_gallery[].formats.large` | object |
| `cover_gallery[].formats.small` | object |
| `cover_gallery[].formats.medium` | object |
| `cover_gallery[].formats.thumbnail` | object |
| `cover_gallery[].formats.{large,small,medium,thumbnail}.ext` | `MISSING_EVIDENCE` |
| `cover_gallery[].formats.{large,small,medium,thumbnail}.url` | `MISSING_EVIDENCE` |
| `cover_gallery[].formats.{large,small,medium,thumbnail}.hash` | `MISSING_EVIDENCE` |
| `cover_gallery[].formats.{large,small,medium,thumbnail}.mime` | `MISSING_EVIDENCE` |
| `cover_gallery[].formats.{large,small,medium,thumbnail}.name` | `MISSING_EVIDENCE` |
| `cover_gallery[].formats.{large,small,medium,thumbnail}.path` | `MISSING_EVIDENCE` |
| `cover_gallery[].formats.{large,small,medium,thumbnail}.size` | `MISSING_EVIDENCE` |
| `cover_gallery[].formats.{large,small,medium,thumbnail}.width` | `MISSING_EVIDENCE` |
| `cover_gallery[].formats.{large,small,medium,thumbnail}.height` | `MISSING_EVIDENCE` |
| `cover_gallery[].formats.{large,small,medium,thumbnail}.sizeInBytes` | `MISSING_EVIDENCE` |
| `cover_gallery[].hash` | string |
| `cover_gallery[].ext` | string |
| `cover_gallery[].mime` | string |
| `cover_gallery[].size` | number |
| `cover_gallery[].url` | string |
| `cover_gallery[].previewUrl` | string |
| `cover_gallery[].provider` | string |
| `cover_gallery[].provider_metadata` | object |
| `cover_gallery[].provider_metadata.blobName` | string |
| `cover_gallery[].folderPath` | string |
| `cover_gallery[].createdAt` | string |
| `cover_gallery[].updatedAt` | string |
| `cover_gallery[].publishedAt` | string |
| `cover_gallery[].locale` | null |
| `SEO` | array of object |
| `SEO[].id` | number |
| `SEO[].seo_title` | string |
| `SEO[].meta_description` | string |
| `FAQ` | array of object |
| `FAQ[].order` | null |
| `FAQ[].id` | number |
| `FAQ[].question` | string |
| `FAQ[].answer` | string |
| `experiences` | array of object |
| `experiences[].order` | null |
| `experiences[].id` | number |
| `experiences[].keyword` | string |
| `experiences[].title` | string |
| `experiences[].description` | string |
| `highlight` | array of object |
| `highlight[].id` | number |
| `highlight[].label` | string |
| `highlight[].value` | string |
| `pois` | array |
| `pois[]` | `MISSING_EVIDENCE` |

The sample `pois` array has an empty element, so the element type is `MISSING_EVIDENCE`. Any other key is `MISSING_EVIDENCE`.
