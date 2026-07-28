---
tags:
  - User
  - POST
---

# Create multiple users

`POST`{ .http-method .post } `/user/createWithList`{ .operation-path }

Create a list of users in one request.

**Operation ID:** `createUsersWithListInput`  
**Authorization:** None

## Request body

Send a JSON array of [User](../../models/user.md) objects as
`application/json`.

```json
[
  { "username": "alice", "email": "alice@example.com" },
  { "username": "bob", "email": "bob@example.com" }
]
```

## Responses

| Status | Description | Body |
| --- | --- | --- |
| `200` | Successful operation. | [User](../../models/user.md) |
| `default` | Unexpected error. | — |

