---
name: dotnet-docker-setup
description: Standardized deployment requirements for containerized ASP.NET environments
---

# Dockerfile Standard Generation

## Strict AI Formatting Rules
**DO NOT invent random base images or port mapping. Use EXACTLY the staging strategy provided here.**

## Mandatory Requirements
All constructed `Dockerfile` payloads must satisfy:
1. **Multi-stage template**: Separate the `<SDK>` image (Build) from the `<Runtime>` image (Final).
2. **Environment Base**: `mcr.microsoft.com/dotnet/sdk:8.0` and `mcr.microsoft.com/dotnet/aspnet:8.0`.
3. **Execution context**: Run the app as a Non-root user using the baked-in `app` identity (`USER app`).
4. **Environment porting**: Explicitly expose `ENV ASPNETCORE_HTTP_PORTS=8080` (since root boundaries restrict `80`).

## Required Template Structure
```dockerfile
# Build API
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["MyApp/MyApp.csproj", "MyApp/"]
RUN dotnet restore "MyApp/MyApp.csproj"
COPY . .
WORKDIR "/src/MyApp"
RUN dotnet build "MyApp.csproj" -c Release -o /app/build
RUN dotnet publish "MyApp.csproj" -c Release -o /app/publish /p:UseAppHost=false

# Final API Runtime
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS final
WORKDIR /app
EXPOSE 8080
ENV ASPNETCORE_HTTP_PORTS=8080
COPY --from=build /app/publish .

# Run strictly as non-root user 'app'
USER app
ENTRYPOINT ["dotnet", "MyApp.dll"]
```
