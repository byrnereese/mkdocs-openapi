---
tags:
  - Store
  - GET
---

# Get inventory

`GET`{ .http-method .get } `/store/inventory`{ .operation-path }

Return a map of pet statuses to quantities.

**Operation ID:** `getInventory`  
**Authorization:** API key

## Responses

| Status | Description | Body |
| --- | --- | --- |
| `200` | Successful operation. | Object whose values are integers. |
| `default` | Unexpected error. | — |

??? example "Example response"

    ```json
    {
      "available": 12,
      "pending": 3,
      "sold": 8
    }
    ```

