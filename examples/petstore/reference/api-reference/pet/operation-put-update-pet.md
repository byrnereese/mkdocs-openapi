---
tags:
  - Pet
  - PUT
---

# Update an existing pet

`PUT`{ .http-method .put } `/pet`{ .operation-path }

Update an existing pet by ID.

**Operation ID:** `updatePet`  
**Authorization:** OAuth 2.0 (`write:pets`, `read:pets`)

## Request body

The request body is required. Its schema is [Pet](../../models/pet.md).

=== "application/json"

    ```json
    {
      "id": 10,
      "name": "doggie",
      "photoUrls": ["https://example.com/doggie.jpg"],
      "status": "available"
    }
    ```

=== "application/xml"

    ```xml
    <Pet>
      <id>10</id>
      <name>doggie</name>
      <photoUrls>https://example.com/doggie.jpg</photoUrls>
      <status>available</status>
    </Pet>
    ```

=== "application/x-www-form-urlencoded"

    Encode the properties of [Pet](../../models/pet.md) as form fields.

## Responses

| Status | Description | Body |
| --- | --- | --- |
| `200` | Successful operation. | [Pet](../../models/pet.md) |
| `400` | Invalid ID supplied. | — |
| `404` | Pet not found. | — |
| `422` | Validation exception. | — |
| `default` | Unexpected error. | — |

