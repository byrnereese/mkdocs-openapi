---
tags:
  - Model
---

# Pet

A pet managed by the store.

## Properties

| Property | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | integer · int64 | No | Unique pet identifier. |
| `name` | string | **Yes** | Pet name. |
| `category` | [Category](category.md) | No | Category assigned to the pet. |
| `photoUrls` | array of strings | **Yes** | URLs for pet photos. |
| `tags` | array of [Tag](tag.md) | No | Searchable labels. |
| `status` | string | No | `available`, `pending`, or `sold`. |

## Example

```json
{
  "id": 10,
  "name": "doggie",
  "category": {
    "id": 1,
    "name": "Dogs"
  },
  "photoUrls": [
    "https://example.com/doggie.jpg"
  ],
  "tags": [
    {
      "id": 7,
      "name": "friendly"
    }
  ],
  "status": "available"
}
```

