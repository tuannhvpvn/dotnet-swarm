---
name: dotnet-controller-migration
description: Migrate legacy ASP.NET Web API controllers to ASP.NET Core MVC controllers
---

# Controller Migration

## Strict AI Formatting Rules
**DO NOT invent namespaces or classes. Use EXACTLY the mapping table provided below.**

## Mapping Table

| Legacy .NET Framework | Modern .NET Core |
|---|---|
| `System.Web.Http.ApiController` | `Microsoft.AspNetCore.Mvc.ControllerBase` + `[ApiController]` attr |
| `IHttpActionResult` | `IActionResult` |
| `[RoutePrefix("...")]` | `[Route("...")]` |
| `[FromUri]` | `[FromQuery]` |
| `Request.CreateResponse(HttpStatusCode.OK, data)` | `Ok(data)` |
| `Request.CreateErrorResponse(...)` | `BadRequest(...)` or `StatusCode(...)` |

## Example

**Before:**
```csharp
using System.Web.Http;

[RoutePrefix("api/users")]
public class UsersController : ApiController
{
    [HttpGet]
    [Route("")]
    public IHttpActionResult Get([FromUri] string status = null)
    {
        return Ok(new[] { "user1", "user2" });
    }
}
```

**After:**
```csharp
using Microsoft.AspNetCore.Mvc;

[ApiController]
[Route("api/users")]
public class UsersController : ControllerBase
{
    [HttpGet]
    [Route("")]
    public IActionResult Get([FromQuery] string status = null)
    {
        return Ok(new[] { "user1", "user2" });
    }
}
```
