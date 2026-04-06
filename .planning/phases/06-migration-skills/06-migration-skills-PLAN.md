---
wave: 1
depends_on: []
files_modified: [
    ".migration-skills/dotnet-controller-migration/SKILL.md", 
    ".migration-skills/dotnet-webconfig-to-appsettings/SKILL.md",
    ".migration-skills/dotnet-startup-migration/SKILL.md",
    ".migration-skills/dotnet-auth-middleware/SKILL.md",
    ".migration-skills/dotnet-namespace-replacement/SKILL.md",
    ".migration-skills/dotnet-logging-adapter/SKILL.md",
    ".migration-skills/dotnet-docker-setup/SKILL.md",
    ".migration-skills/dotnet-nuget-mapping/SKILL.md",
    "app/utils/sync_skills.py"
]
autonomous: true
gap_closure: false
requirements_addressed: [SKL-01, SKL-02, SKL-03, SKL-04, SKL-05, SKL-06, SKL-07, SKL-08, SKL-09]
---

# Phase 6: Migration Skills Blueprint

<objective>
To establish 8 formalized Phase 1 Lift-&-Shift semantic skills within `.migration-skills/`, ensuring exact boundaries (preventing AI hallucination), and propagating them via `sync_skills.py` without mutating existing Phase 2 capabilities.
</objective>

<tasks>

<task>
  <id>skl-01-controller</id>
  <title>Define Controller Migration Skill</title>
  <action>
Create `.migration-skills/dotnet-controller-migration/SKILL.md`.
Includes standard YAML header.
Includes the strict explicit directive: "DO NOT invent namespaces, use EXACTLY the mapping table provided."
Map `ApiController -> ControllerBase`, `IHttpActionResult -> IActionResult`, etc.
  </action>
</task>

<task>
  <id>skl-02-webconfig</id>
  <title>Define WebConfig Skill</title>
  <action>
Create `.migration-skills/dotnet-webconfig-to-appsettings/SKILL.md`.
Explicit strict AI formatting rules: NEVER copy active connection strings directly (use Placeholders).
Map keys to `appsettings.json`.
  </action>
</task>

<task>
  <id>skl-03-startup</id>
  <title>Define Startup Skill</title>
  <action>
Create `.migration-skills/dotnet-startup-migration/SKILL.md`.
Explicit constraint mapping for translating `Global.asax` pipelines and `WebApiConfig.Register` into `Program.cs` Top-Level ASP.NET setup structures.
  </action>
</task>

<task>
  <id>skl-04-auth</id>
  <title>Define Auth Middleware Skill</title>
  <action>
Create `.migration-skills/dotnet-auth-middleware/SKILL.md`.
Explicit constraint: Force `UseAuthentication()` + `UseAuthorization()` in modern Middleware patterns rather than legacy HTTP Handlers.
  </action>
</task>

<task>
  <id>skl-05-namespace</id>
  <title>Define Namespace Replacement Skill</title>
  <action>
Create `.migration-skills/dotnet-namespace-replacement/SKILL.md`.
Explicit strict AI directive: "DO NOT invent namespaces. Maps must precisely cross-reference `System.Web.Http` to `Microsoft.AspNetCore.Mvc`".
  </action>
</task>

<task>
  <id>skl-06-logging</id>
  <title>Define Logging Adapter Skill</title>
  <action>
Create `.migration-skills/dotnet-logging-adapter/SKILL.md`.
Provide patterns wrapping Custom legacy loggers into default core `ILogger<T>`.
  </action>
</task>

<task>
  <id>skl-07-docker</id>
  <title>Define Dockerfile Generation Skill</title>
  <action>
Create `.migration-skills/dotnet-docker-setup/SKILL.md`.
Strict requirements enforcing Multi-stage templates running under a Non-Root user with standardized port mappings.
  </action>
</task>

<task>
  <id>skl-08-nuget</id>
  <title>Define NuGet Package Mapping Skill</title>
  <action>
Create `.migration-skills/dotnet-nuget-mapping/SKILL.md`.
Strict compliance: Explicitly drop builtin legacy packages and bump required 3rd party package references manually over "AI best guesses".
  </action>
</task>

<task>
  <id>skl-09-sync</id>
  <title>Update Python Sync Mechanism</title>
  <read_first>
    <file>app/utils/sync_skills.py</file>
  </read_first>
  <action>
Modify `app/utils/sync_skills.py` keeping the 5 underlying legacy skills while appending the 8 new skill folder targets to the `SKILLS` array safely.
  </action>
</task>

</tasks>

<verification>
## Verification
1. Run `python app/utils/sync_skills.py .` 
2. Verify output lists 13 total synced successful operations.
3. Validate `.md` files contain the Strict constraint warnings.
</verification>

<must_haves>
- The Strict instruction tag `DO NOT invent namespaces, use EXACTLY the mapping provided.` must exist.
- `app/utils/sync_skills.py` appended (13 size) without nuking origin items.
</must_haves>
