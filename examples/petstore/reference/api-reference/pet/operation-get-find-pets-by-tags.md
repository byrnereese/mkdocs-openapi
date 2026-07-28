---
tags:
  - Pet
  - GET
---

# Find pets by tags

`GET`{ .http-method .get } `/pet/findByTags`{ .operation-path }

Find pets matching one or more tags.

**Operation ID:** `findPetsByTags`  
**Authorization:** OAuth 2.0 (`write:pets`, `read:pets`)

## Query parameters

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `tags` | array of strings | **Yes** | Tags to filter by. Repeat the parameter for multiple values. |

## Responses

| Status | Description | Body |
| --- | --- | --- |
| `200` | Successful operation. | Array of [Pet](../../models/pet.md) |
| `400` | Invalid tag value. | — |
| `default` | Unexpected error. | — |

