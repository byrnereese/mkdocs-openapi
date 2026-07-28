---
tags:
  - Store
  - DELETE
---

# Delete an order

`DELETE`{ .http-method .delete } `/store/order/{orderId}`{ .operation-path }

Delete a purchase order by its identifier.

**Operation ID:** `deleteOrder`  
**Authorization:** None

## Path parameters

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `orderId` | integer · int64 | **Yes** | ID of the order to delete. |

## Responses

| Status | Description |
| --- | --- |
| `200` | Order deleted. |
| `400` | Invalid ID supplied. |
| `404` | Order not found. |
| `default` | Unexpected error. |

