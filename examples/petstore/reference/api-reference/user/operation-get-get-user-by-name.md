---
tags:
  - User
  - GET
---

# Get a user by username

`GET`{ .http-method .get } `/user/{username}`{ .operation-path }

Return details for a user.

**Operation ID:** `getUserByName`  
**Authorization:** None

## Path parameters

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `username` | string | **Yes** | Username to return. Try `user1` on the sample server. |

## Responses

| Status | Description | Body |
| --- | --- | --- |
| `200` | Successful operation. | [User](../../models/user.md) |
| `400` | Invalid username supplied. | — |
| `404` | User not found. | — |
| `default` | Unexpected error. | — |

