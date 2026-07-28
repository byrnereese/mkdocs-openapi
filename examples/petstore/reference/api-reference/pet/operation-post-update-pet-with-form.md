---
tags:
  - Pet
  - POST
---

# Update a pet with form data

`POST`{ .http-method .post } `/pet/{petId}`{ .operation-path }

Update selected fields on an existing pet.

**Operation ID:** `updatePetWithForm`  
**Authorization:** OAuth 2.0 (`write:pets`, `read:pets`)

## Parameters

| Name | Location | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `petId` | path | integer · int64 | **Yes** | ID of the pet to update. |
| `name` | query | string | No | New pet name. |
| `status` | query | string | No | New pet status. |

## Responses

| Status | Description | Body |
| --- | --- | --- |
| `200` | Successful operation. | [Pet](../../models/pet.md) |
| `400` | Invalid input. | — |
| `default` | Unexpected error. | — |

