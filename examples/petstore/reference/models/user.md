---
tags:
  - Model
---

# User

A Petstore user account.

## Properties

| Property | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | integer · int64 | No | Unique user identifier. |
| `username` | string | No | Login name. |
| `firstName` | string | No | Given name. |
| `lastName` | string | No | Family name. |
| `email` | string | No | Email address. |
| `password` | string | No | Account password. |
| `phone` | string | No | Telephone number. |
| `userStatus` | integer · int32 | No | User status code. |

## Example

```json
{
  "id": 10,
  "username": "theUser",
  "firstName": "John",
  "lastName": "James",
  "email": "john@example.com",
  "password": "correct-horse-battery-staple",
  "phone": "+1-555-0100",
  "userStatus": 1
}
```

