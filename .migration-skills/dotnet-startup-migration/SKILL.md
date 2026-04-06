---
name: dotnet-startup-migration
description: Translate legacy Global.asax pipeline configurations into top-level Program.cs statements
---

# Startup Pipeline Migration

## Strict AI Formatting Rules
**DO NOT invent methods or pipeline stages. Use EXACTLY the translation logic mapped below.**

## Translation Targets

- `Application_Start` logic must be transformed directly into `.NET 6.0+ Top-level statements` inside `Program.cs`.
- Replace `WebApiConfig.Register(GlobalConfiguration.Configuration)` with `builder.Services.AddControllers();` and `app.MapControllers();` pipeline attributes.
- Migrate `RouteTable.Routes.MapHttpRoute` into attribute routing on the respective controllers themselves (do not maintain a bloated startup routing dictionary).
- Port DI configuration (e.g., Unity/Ninject) explicitly into `builder.Services.AddScoped<IFoo, Foo>()` mapping tables in `Program.cs`.

## Example Setup Structure

```csharp
var builder = WebApplication.CreateBuilder(args);

// Add services to the container (Replacement for DI registers)
builder.Services.AddControllers();

var app = builder.Build();

// Configure the HTTP request pipeline (Replacement for Application_Start / Global.asax hooks)
if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
}

app.UseHttpsRedirection();
app.UseAuthorization();
app.MapControllers(); // Replacement for WebApiConfig.Register

app.Run();
```
