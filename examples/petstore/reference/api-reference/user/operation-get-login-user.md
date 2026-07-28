---
tags:
  - User
  - GET
---

# Log in

`GET`{ .http-method .get } `/user/login`{ .operation-path }

Log a user into the system.

**Operation ID:** `loginUser`  
**Authorization:** None

## Query parameters

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `username` | string | No | Username used to log in. |
| `password` | string | No | Password in clear text. |

## Responses

| Status | Description | Body |
| --- | --- | --- |
| `200` | Successful operation. | string |
| `400` | Invalid username or password. | — |
| `default` | Unexpected error. | — |

The `200` response also returns rate-limit information:

| Header | Type | Description |
| --- | --- | --- |
| `X-Rate-Limit` | integer · int32 | Calls per hour allowed for the user. |
| `X-Expires-After` | string · date-time | Token expiry time in UTC. |

