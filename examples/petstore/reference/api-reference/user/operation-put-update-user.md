---
tags:
  - User
  - PUT
---

# Update a user

`PUT`{ .http-method .put } `/user/{username}`{ .operation-path }

Update an existing user account.

**Operation ID:** `updateUser`  
**Authorization:** None

## Path parameters

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `username` | string | **Yes** | Username to update. |

## Request body

Send the updated [User](../../models/user.md) as `application/json`,
`application/xml`, or `application/x-www-form-urlencoded`.

```json title="application/json"
{
  "username": "theUser",
  "firstName": "Jane",
  "lastName": "James",
  "email": "jane@example.com"
}
```

## Responses

| Status | Description |
| --- | --- |
| `200` | Successful operation. |
| `400` | Bad request. |
| `404` | User not found. |
| `default` | Unexpected error. |

