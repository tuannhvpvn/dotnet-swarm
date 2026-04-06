---
name: dotnet-logging-adapter
description: Wrapping custom proprietary loggers into ILogger<T> pipelines
---

# Logging Pipeline Adapter

## Strict AI Formatting Rules
**DO NOT invent logging frameworks. DO NOT replace NLog/Log4Net configurations natively unless converting directly directly to simple `ILogger<T>` facades.**

## Implementation Goals
Legacy loggers (like custom static classes e.g., `LogManager.GetLogger()`) must be refactored to consume dependency-injected `ILogger<T>` inputs. Maintain the explicit existing proprietary methods by wrapping them behind a facade if an immediate replacement is structurally impossible.

**Before:**
```csharp
public class PaymentService 
{
    private static readonly Logger log = LogManager.GetCurrentClassLogger();

    public void Process() 
    {
        log.Info("Payment triggered");
    }
}
```

**After:**
```csharp
public class PaymentService 
{
    private readonly ILogger<PaymentService> _logger;

    public PaymentService(ILogger<PaymentService> logger) 
    {
        _logger = logger;
    }

    public void Process() 
    {
        _logger.LogInformation("Payment triggered");
    }
}
```
