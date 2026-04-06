# .NET Migration Swarm v1.3.0

**Multi-Agent System** cho việc migrate WebAPI .NET Framework 4.5/4.6/4.8 sang .NET 10.

### Tính năng chính
- LangGraph + Ruflo (Hierarchical Queen-led Swarm)
- GitNexus Knowledge Graph
- Vibekanban realtime dashboard
- Auto Skill Creation + Retry mechanism
- State Persistence (SQLite)
- Logging chuyên nghiệp (loguru)

### Cách chạy
1. Chạy Vibekanban:
   ```bash
   PORT=3000 npx vibe-kanban
   ```
2. Chạy GitNexus MCP (nếu dùng):
   ```bash
   npx gitnexus mcp --port 4000
   ```
3. Chạy Migration Swarm:
   ```bash
   ./run-migration-with-dashboard.sh /path/to/your-dotnet-repo 1
   ```

Project đã được tối ưu với:
- Retry cho agentic tools
- Tự tạo skill khi phát hiện pattern lặp lại
- Resume migration sau crash
- Realtime dashboard

Chúc bạn migrate thành công!