---
name: dotnet-auth-middleware
description: Translate legacy Authentication structures into modern Core Middleware
---

# Authentication Middleware Migration

## Strict AI Formatting Rules
**DO NOT invent HTTP Handlers. Force standard `UseAuthentication()` and `UseAuthorization()` modern pipeline patterns.**

## Execution Mappings
- **Handlers:** Legacy `DelegatingHandler` or custom `IAuthenticationFilter` objects *must* be rewritten as ASP.NET Core Middleware classes `public class CustomMiddleware { RequestDelegate _next }`.
- **Pipeline Insertion:** Bearer tokens must rely on `builder.Services.AddAuthentication().AddJwtBearer(...)`.
- **Pipeline Execution:** Ensure `app.UseAuthentication();` precedes `app.UseAuthorization();` directly before `app.MapControllers();`.

## Example Handler Migration

**Before:**
```csharp
public class AuthHandler : DelegatingHandler
{
    protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
    {
         // logic
         return await base.SendAsync(request, cancellationToken);
    }
}
```

**After:**
```csharp
public class AuthMiddleware
{
    private readonly RequestDelegate _next;
    
    public AuthMiddleware(RequestDelegate next)
    {
        _next = next;
    }
    
    public async Task InvokeAsync(HttpContext context)
    {
         // logic
         await _next(context);
    }
}
// Add to Program.cs: app.UseMiddleware<AuthMiddleware>();
```
