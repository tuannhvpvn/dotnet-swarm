---
name: dotnet-namespace-replacement
description: Global namespace transformation definitions
---

# Namespace Replacements

## Strict AI Formatting Rules
**DO NOT invent namespaces. Maps must precisely cross-reference the tables below.**

## Core Replacements

| Legacy Framework Equivalent | Target Core Equivalent |
|---|---|
| `System.Web.Http` | `Microsoft.AspNetCore.Mvc` |
| `System.Web.Http.Cors` | `Microsoft.AspNetCore.Cors` |
| `System.Net.Http` | `System.Net.Http` |
| `System.Web.Http.Routing` | `Microsoft.AspNetCore.Routing` |
| `System.Web.Http.Filters` | `Microsoft.AspNetCore.Mvc.Filters` |
| `System.Web.Http.Controllers` | `Microsoft.AspNetCore.Mvc.Controllers` |

## Forbidden Classes
If you encounter `HttpContext.Current`, it MUST be refactored to utilize injected `IHttpContextAccessor`.
