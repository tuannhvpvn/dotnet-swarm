---
name: dotnet-webconfig-to-appsettings
description: Migrate legacy Web.config XML configurations to modern appsettings.json
---

# Web.config Configuration Migration

## Strict AI Formatting Rules
**DO NOT invent. Use EXACTLY the mapping table provided. NEVER copy plain-text active connection strings directly into appsettings.json. Always use placeholder values.**

## Action Steps

1. Extract `<appSettings>` keys from `Web.config` and port them to flat JSON fields in `appsettings.json`.
2. Extract `<connectionStrings>` into a `ConnectionStrings` object inside `appsettings.json`.
3. Scrub all real credentials inside the connection string with `<PLACEHOLDER>` syntax.
4. Move `<system.web/authentication>` configuration logic directives directly into the `Program.cs` startup pipeline. 

## Environment Example

**Before (Web.config):**
```xml
<configuration>
  <connectionStrings>
    <add name="DefaultConnection" connectionString="Server=myServerAddress;Database=myDataBase;User Id=myUsername;Password=myPassword;" />
  </connectionStrings>
  <appSettings>
    <add key="ApiTimeout" value="5000" />
  </appSettings>
</configuration>
```

**After (appsettings.json):**
```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=myServerAddress;Database=myDataBase;User Id=<PLACEHOLDER>;Password=<PLACEHOLDER>;"
  },
  "ApiTimeout": "5000"
}
```
