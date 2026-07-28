---
tags:
  - User
  - POST
---

# Create a user

`POST`{ .http-method .post } `/user`{ .operation-path }

Create a user account.

**Operation ID:** `createUser`  
**Authorization:** None

## Request body

The request uses the [User](../../models/user.md) schema and accepts
`application/json`, `application/xml`, or
`application/x-www-form-urlencoded`.

```json title="application/json"
{
  "username": "theUser",
  "firstName": "John",
  "lastName": "James",
  "email": "john@example.com",
  "password": "correct-horse-battery-staple",
  "phone": "+1-555-0100"
}
```

## Responses

| Status | Description | Body |
| --- | --- | --- |
| `200` | Successful operation. | [User](../../models/user.md) |
| `default` | Unexpected error. | — |

