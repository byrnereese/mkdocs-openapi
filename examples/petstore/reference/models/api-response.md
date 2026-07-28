---
tags:
  - Model
---

# API response

Result metadata returned by an API operation.

## Properties

| Property | Type | Required | Description |
| --- | --- | --- | --- |
| `code` | integer · int32 | No | Application-specific result code. |
| `type` | string | No | Result type. |
| `message` | string | No | Human-readable result message. |

## Example

```json
{
  "code": 200,
  "type": "success",
  "message": "Image uploaded"
}
```

