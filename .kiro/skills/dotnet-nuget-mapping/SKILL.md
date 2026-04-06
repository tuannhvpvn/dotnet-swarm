---
name: dotnet-nuget-mapping
description: Explicit map translation for outdated NuGet references
---

# Package Modernization

## Strict AI Formatting Rules
**DO NOT guess third party package upgrades. Rely explicitly on the explicitly assigned version table. DO NOT retain standard .NET generic library elements built into the .NET Core base runtime.**

## Automatic Removal directives 
The following `packages.config` items MUST be pruned completely, as ASP.NET Core natively provides them:
- `Microsoft.AspNet.WebApi`
- `Microsoft.AspNet.WebApi.Core`
- `Microsoft.AspNet.WebApi.Client`
- `Newtonsoft.Json` (migrates natively to `System.Text.Json` unless structural overrides block it)
- `Microsoft.AspNet.Mvc`

## Explicit Upgrade Bumps
| Legacy Framework Package | Core Port Migration Target |
|---|---|
| `EntityFramework` (v6) | `Microsoft.EntityFrameworkCore.SqlServer` |
| `Swashbuckle` | `Swashbuckle.AspNetCore` |
| `Microsoft.Owin` | Prune (Native) |
| `Unity` | Prune (Use `Microsoft.Extensions.DependencyInjection`) |
| `Ninject` | Prune (Use `Microsoft.Extensions.DependencyInjection`) |
