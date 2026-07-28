---
tags:
  - Pet
  - DELETE
---

# Delete a pet

`DELETE`{ .http-method .delete } `/pet/{petId}`{ .operation-path }

Delete a pet from the store.

**Operation ID:** `deletePet`  
**Authorization:** OAuth 2.0 (`write:pets`, `read:pets`)

## Parameters

| Name | Location | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `petId` | path | integer · int64 | **Yes** | ID of the pet to delete. |
| `api_key` | header | string | No | Optional API key. |

## Responses

| Status | Description |
| --- | --- |
| `200` | Pet deleted. |
| `400` | Invalid pet value. |
| `default` | Unexpected error. |

