---
tags:
  - Model
---

# Order

A store order for a pet.

## Properties

| Property | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | integer · int64 | No | Unique order identifier. |
| `petId` | integer · int64 | No | Ordered pet identifier. |
| `quantity` | integer · int32 | No | Number of pets ordered. |
| `shipDate` | string · date-time | No | Expected shipping date. |
| `status` | string | No | `placed`, `approved`, or `delivered`. |
| `complete` | boolean | No | Whether the order is complete. |

## Example

```json
{
  "id": 10,
  "petId": 198772,
  "quantity": 7,
  "shipDate": "2026-07-20T12:00:00Z",
  "status": "approved",
  "complete": false
}
```

