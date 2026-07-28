---
tags:
  - Store
  - POST
---

# Place an order

`POST`{ .http-method .post } `/store/order`{ .operation-path }

Place a new order for a pet.

**Operation ID:** `placeOrder`  
**Authorization:** None

## Request body

The request uses the [Order](../../models/order.md) schema and accepts
`application/json`, `application/xml`, or
`application/x-www-form-urlencoded`.

```json title="application/json"
{
  "id": 10,
  "petId": 198772,
  "quantity": 7,
  "shipDate": "2026-07-20T12:00:00Z",
  "status": "approved",
  "complete": false
}
```

## Responses

| Status | Description | Body |
| --- | --- | --- |
| `200` | Successful operation. | [Order](../../models/order.md) |
| `400` | Invalid input. | — |
| `422` | Validation exception. | — |
| `default` | Unexpected error. | — |

