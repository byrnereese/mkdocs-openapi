---
tags:
  - Pet
  - POST
---

# Add a new pet

`POST`{ .http-method .post } `/pet`{ .operation-path }

Add a new pet to the store.

**Operation ID:** `addPet`  
**Authorization:** OAuth 2.0 (`write:pets`, `read:pets`)

## Request body

The request body is required. Its schema is [Pet](../../models/pet.md).

=== "application/json"

    ```json
    {
      "name": "doggie",
      "photoUrls": ["https://example.com/doggie.jpg"],
      "status": "available"
    }
    ```

=== "application/xml"

    ```xml
    <Pet>
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
| `400` | Invalid input. | — |
| `422` | Validation exception. | — |
| `default` | Unexpected error. | — |

