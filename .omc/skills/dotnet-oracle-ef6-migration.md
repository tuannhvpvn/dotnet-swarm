---
name: dotnet-oracle-ef6-migration
description: Migrate Oracle + EF5/6 sang .NET 10 (Phase 1)
category: phase1
version: 1.3
tags: [oracle, ef6, odp.net]
---

**Mục tiêu Phase 1:**
- Thay Oracle.ManagedDataAccess → Oracle.ManagedDataAccess.Core (23.5+)
- Giữ nguyên connection string và behavior cũ
- Không refactor repository ở Phase 1
