---
tags:
  - User
  - DELETE
---

# Delete a user

`DELETE`{ .http-method .delete } `/user/{username}`{ .operation-path }

Delete an existing user account.

**Operation ID:** `deleteUser`  
**Authorization:** None

## Path parameters

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `username` | string | **Yes** | Username to delete. |

## Responses

| Status | Description |
| --- | --- |
| `200` | User deleted. |
| `400` | Invalid username supplied. |
| `404` | User not found. |
| `default` | Unexpected error. |

