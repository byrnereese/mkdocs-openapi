---
tags:
  - Pet
  - POST
---

# Upload an image

`POST`{ .http-method .post } `/pet/{petId}/uploadImage`{ .operation-path }

Upload an image for a pet.

**Operation ID:** `uploadFile`  
**Authorization:** OAuth 2.0 (`write:pets`, `read:pets`)

## Parameters

| Name | Location | Type | Required | Description |
| --- | --- | --- | --- | --- |
| `petId` | path | integer · int64 | **Yes** | ID of the pet to update. |
| `additionalMetadata` | query | string | No | Additional metadata for the image. |

## Request body

Send the binary file as `application/octet-stream`.

## Responses

| Status | Description | Body |
| --- | --- | --- |
| `200` | Successful operation. | [API response](../../models/api-response.md) |
| `400` | No file uploaded. | — |
| `404` | Pet not found. | — |
| `default` | Unexpected error. | — |

