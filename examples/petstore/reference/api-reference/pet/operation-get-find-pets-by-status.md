---
tags:
  - Pet
  - GET
---

# Find pets by status

`GET`{ .http-method .get } `/pet/findByStatus`{ .operation-path }

Find pets matching a lifecycle status.

**Operation ID:** `findPetsByStatus`  
**Authorization:** OAuth 2.0 (`write:pets`, `read:pets`)

## Query parameters

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `status` | string | **Yes** | `available`, `pending`, or `sold`. Defaults to `available`. |

## Responses

| Status | Description | Body |
| --- | --- | --- |
| `200` | Successful operation. | Array of [Pet](../../models/pet.md) |
| `400` | Invalid status value. | — |
| `default` | Unexpected error. | — |

??? example "Example request"

    ```bash
    curl --get 'https://petstore3.swagger.io/api/v3/pet/findByStatus' \
      --data-urlencode 'status=available'
    ```

