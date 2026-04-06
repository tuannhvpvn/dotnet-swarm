---
name: dotnet-phase1-csproj-upgrade
description: Lift-and-shift .NET Framework 4.5/4.6/4.8 → .NET 10 (chỉ thay csproj, packages)
category: phase1
version: 1.3
tags: [csproj, sdk-style, lift-and-shift]
---

**Mục tiêu Phase 1:**
- Chỉ được sửa file .csproj và packages.config / app.config
- TargetFramework = net10.0
- Sử dụng <Project Sdk="Microsoft.NET.Sdk">
- KHÔNG thay đổi business logic, namespace, class name

**GOOD example:**
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
</Project>
```
