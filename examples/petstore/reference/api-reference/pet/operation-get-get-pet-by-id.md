---
tags:
  - Pet
  - GET
---

# Find a pet by ID

`GET`{ .http-method .get } `/pet/{petId}`{ .operation-path }

Return a single pet.

**Operation ID:** `getPetById`  
**Authorization:** API key **or** OAuth 2.0 (`write:pets`, `read:pets`)

## Path parameters

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `petId` | integer · int64 | **Yes** | ID of the pet to return. |

## Responses

| Status | Description | Body |
| --- | --- | --- |
| `200` | Successful operation. | [Pet](../../models/pet.md) |
| `400` | Invalid ID supplied. | — |
| `404` | Pet not found. | — |
| `default` | Unexpected error. | — |

??? example "Example response"

    ```json
    {
      "id": 10,
      "name": "doggie",
      "photoUrls": ["https://example.com/doggie.jpg"],
      "status": "available"
    }
    ```

