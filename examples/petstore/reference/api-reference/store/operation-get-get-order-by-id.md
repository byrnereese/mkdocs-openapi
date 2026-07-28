---
tags:
  - Store
  - GET
---

# Find an order by ID

`GET`{ .http-method .get } `/store/order/{orderId}`{ .operation-path }

Return a purchase order by its identifier.

**Operation ID:** `getOrderById`  
**Authorization:** None

!!! tip "Test data"

    For the sample server, try an integer ID of 1–5 or an ID greater than 10.

## Path parameters

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `orderId` | integer · int64 | **Yes** | ID of the order to return. |

## Responses

| Status | Description | Body |
| --- | --- | --- |
| `200` | Successful operation. | [Order](../../models/order.md) |
| `400` | Invalid ID supplied. | — |
| `404` | Order not found. | — |
| `default` | Unexpected error. | — |

