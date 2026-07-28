# API reference

The Petstore API is organized by resource. Each resource page contains every
operation carrying the corresponding OpenAPI tag.

## Server

| Environment | Base URL |
| --- | --- |
| Petstore | `https://petstore3.swagger.io/api/v3` |

## Resources

| Resource | Description | Operations |
| --- | --- | ---: |
| [Pet](pet/index.md) | Everything about your pets. | 8 |
| [Store](store/index.md) | Access Petstore orders and inventory. | 4 |
| [User](user/index.md) | Operations about users. | 7 |

## Authentication

Operations can use one or both of the following security schemes. The required
scheme is shown on each operation.

=== "API key"

    Send the API key in the `api_key` request header.

    ```http
    api_key: YOUR_API_KEY
    ```

=== "OAuth 2.0"

    The implicit OAuth flow supports these scopes:

    | Scope | Access |
    | --- | --- |
    | `read:pets` | Read pets. |
    | `write:pets` | Modify pets. |

!!! note

    Individual operations may be public or may override these requirements.

## Data models

Reusable schemas are documented separately from operations. Browse the
[model reference](../models/index.md) for properties, constraints, and links
between models.

