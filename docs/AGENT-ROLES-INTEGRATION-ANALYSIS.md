# Agent Roles Integration Analysis: OpenCode Agent Conversations + Speckle Gastown

## Executive Summary

This analysis evaluates integrating the **opencode-agent-conversations** multi-agent framework with **Speckle Gastown's ephemeral worker architecture** to create a hierarchical, role-based AI agent system for autonomous software development.

**Verdict: High-value integration opportunity** - The complementary architectures can be combined to create a sophisticated multi-tier agent orchestration system.

---

## Source Systems Analysis

### 1. OpenCode Agent Conversations

**Repository:** `marcel-tuinstra/opencode-agent-conversations`

**Core Architecture:**
- Plugin-based system for OpenCode CLI
- 7 predefined agent roles with distinct personas
- Intent detection with weighted role participation
- Mention-gated MCP tool access
- Threaded multi-agent conversation output

**Agent Roles:**
| Role | Focus | MCP Access | Tool Permissions |
|------|-------|------------|------------------|
| CEO | Strategy, priorities, success metrics | Read-only | Comments only |
| CTO | Technical strategy, architecture, NFRs | GitHub/Sentry read | Technical notes |
| PO | Product outcomes, requirements, ACs | Shortcut full | Story management |
| PM | Delivery planning, scope, risks | Shortcut full | Task management |
| DEV | Implementation, bug fixes, features | GitHub/Sentry full | Code changes |
| MARKETING | Messaging, positioning, launch | Documents only | Content proposals |
| RESEARCH | Investigation, evidence, risks | Read-only | Documentation |

**Intent-Role Weighting System:**
```
Intent Types: backend | design | marketing | roadmap | research | mixed

Example Weights (backend intent):
  CTO: 5, DEV: 5, PM: 2, PO: 2, CEO: 1, MARKETING: 0, RESEARCH: 1

Example Weights (roadmap intent):
  PM: 5, PO: 5, CEO: 4, CTO: 3, DEV: 2, MARKETING: 2, RESEARCH: 2
```

**Key Mechanisms:**
- `detectIntent()` - Keyword analysis to determine conversation intent
- `buildTurnTargets()` - Calculate speaking turns per role
- `normalizeThreadOutput()` - Format multi-agent output as `[n] ROLE: message`
- `providerFromToolName()` - Map MCP tools to providers for access control

### 2. Speckle Gastown (Ephemeral Sessions)

**Location:** `specs/020-ephemeral-bead-sessions/`, `.speckle/scripts/`

**Core Architecture:**
- Session-per-bead model with lifecycle management
- Git worktree isolation for parallel work
- Terminal mirroring for observability
- Auto-spawn/terminate daemon
- Progress persistence via `progress.txt`

**Session Lifecycle:**
```
PENDING → SPAWNING → RUNNING → [STUCK] → COMPLETED | FAILED | TERMINATED
```

**Key Components:**
| Component | Purpose |
|-----------|---------|
| `session_manager.py` | BeadSession lifecycle, spawn/terminate |
| `session_daemon.py` | Watch for status changes, auto-sync |
| `workers.sh` | Git worktree management, branch isolation |
| `terminal_server.py` | WebSocket output streaming |

**Session States:**
- **PENDING**: Waiting in queue
- **SPAWNING**: Session initializing
- **RUNNING**: Claude actively working
- **STUCK**: No output for >60s, needs intervention
- **COMPLETED**: Task finished successfully
- **FAILED**: Error or timeout
- **TERMINATED**: Manually stopped

---

## Optimal Agent Role Hierarchy for Speckle Gastown

### Proposed 3-Tier Hierarchy

```
                    ┌─────────────────────────────┐
                    │         TIER 1              │
                    │       ORCHESTRATOR          │
                    │      (Mayor Pattern)        │
                    │                             │
                    │  Roles: CEO, PM             │
                    │  Focus: Strategy, Planning  │
                    │  Tools: Read-only, bd CLI   │
                    └─────────────┬───────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    TIER 2       │     │    TIER 2       │     │    TIER 2       │
│   SUPERVISOR    │     │   SUPERVISOR    │     │   SUPERVISOR    │
│   (Architect)   │     │   (Product)     │     │   (Research)    │
│                 │     │                 │     │                 │
│ Roles: CTO      │     │ Roles: PO       │     │ Roles: RESEARCH │
│ Focus: Design   │     │ Focus: Stories  │     │ Focus: Evidence │
│ Tools: Inspect  │     │ Tools: Backlog  │     │ Tools: Analysis │
└────────┬────────┘     └────────┬────────┘     └─────────────────┘
         │                       │
         │              ┌────────┴────────┐
         │              │                 │
         ▼              ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                          TIER 3                                  │
│                     EPHEMERAL WORKERS                            │
│                    (Gastown Sessions)                            │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ DEV      │  │ DEV      │  │ DEV      │  │MARKETING │        │
│  │ Session  │  │ Session  │  │ Session  │  │ Session  │        │
│  │ bead-001 │  │ bead-002 │  │ bead-003 │  │ bead-004 │        │
│  │ feature  │  │ bugfix   │  │ refactor │  │ docs     │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│                                                                  │
│  - Isolated git worktrees                                        │
│  - Role-specific tool permissions                                │
│  - Auto-spawn on in_progress                                     │
│  - Terminal output streaming                                     │
└─────────────────────────────────────────────────────────────────┘
```

### Tier Definitions

#### Tier 1: Orchestrator (Mayor Pattern)
**Roles:** CEO, PM

**Responsibilities:**
- Strategic planning and prioritization
- Work decomposition into beads
- Dependency management
- Resource allocation across workers
- Milestone tracking

**Tool Access:**
- `bd` commands (full access)
- Read-only codebase inspection
- NO code changes
- NO git operations

**Gastown Integration:**
- Runs as persistent session (not ephemeral)
- Monitors all Tier 3 workers via terminal mirroring
- Can spawn/terminate worker sessions
- Coordinates handoffs between workers

#### Tier 2: Supervisor (Domain Experts)
**Roles:** CTO, PO, RESEARCH

**Responsibilities:**
- Domain-specific guidance
- Technical/product architecture decisions
- Quality review before merge
- Blocker resolution

**Tool Access:**
| Role | Read Access | Write Access |
|------|-------------|--------------|
| CTO | Full codebase, PRs, Sentry | Technical docs, comments |
| PO | Stories, epics, backlog | Story CRUD, acceptance criteria |
| RESEARCH | Full codebase, external docs | Research docs, comments |

**Gastown Integration:**
- Semi-persistent sessions (longer timeout)
- Can intervene in STUCK worker sessions
- Provide context injection to workers
- Review worker output before completion

#### Tier 3: Ephemeral Workers (Gastown Sessions)
**Primary Role:** DEV (with MARKETING for content tasks)

**Responsibilities:**
- Implement assigned bead
- Write tests
- Commit changes
- Update progress.txt

**Tool Access:**
- Full code read/write in assigned worktree
- git add, commit (no push)
- Test execution
- Build validation

**Gastown Integration:**
- One session per bead (1:1 mapping)
- Auto-spawn on `bd update --status in_progress`
- Auto-terminate on `bd close` or timeout
- Isolated git worktree per worker
- Output streamed to kanban board

---

## Integration Architecture

### Session Configuration by Role

```python
ROLE_SESSION_CONFIG = {
    "CEO": {
        "tier": 1,
        "ephemeral": False,
        "timeout": 7200,  # 2 hours
        "max_concurrent": 1,
        "tools": ["bd", "read"],
        "worktree": False,
    },
    "PM": {
        "tier": 1,
        "ephemeral": False,
        "timeout": 7200,
        "max_concurrent": 1,
        "tools": ["bd", "read", "shortcut"],
        "worktree": False,
    },
    "CTO": {
        "tier": 2,
        "ephemeral": True,
        "timeout": 3600,  # 1 hour
        "max_concurrent": 1,
        "tools": ["read", "github", "sentry"],
        "worktree": False,
    },
    "PO": {
        "tier": 2,
        "ephemeral": True,
        "timeout": 3600,
        "max_concurrent": 1,
        "tools": ["read", "shortcut"],
        "worktree": False,
    },
    "DEV": {
        "tier": 3,
        "ephemeral": True,
        "timeout": 1800,  # 30 min
        "max_concurrent": 3,
        "tools": ["read", "write", "bash", "git", "github"],
        "worktree": True,
    },
    "RESEARCH": {
        "tier": 2,
        "ephemeral": True,
        "timeout": 2400,  # 40 min
        "max_concurrent": 1,
        "tools": ["read", "webfetch"],
        "worktree": False,
    },
    "MARKETING": {
        "tier": 3,
        "ephemeral": True,
        "timeout": 1800,
        "max_concurrent": 1,
        "tools": ["read", "write"],
        "worktree": False,
    },
}
```

### Intent-Based Role Assignment

When a bead is created, analyze intent and assign appropriate role:

```python
BEAD_INTENT_ROLE_MAPPING = {
    # Labels/keywords → Primary role for worker session
    "feature": "DEV",
    "bug": "DEV",
    "bugfix": "DEV",
    "refactor": "DEV",
    "test": "DEV",
    "docs": "MARKETING",
    "copy": "MARKETING",
    "research": "RESEARCH",
    "architecture": "CTO",  # Tier 2, will advise not implement
    "requirements": "PO",    # Tier 2, will specify not implement
}

def assign_worker_role(bead: dict) -> str:
    """Determine which role should work on this bead."""
    labels = bead.get("labels", [])
    title = bead.get("title", "").lower()
    
    for keyword, role in BEAD_INTENT_ROLE_MAPPING.items():
        if keyword in labels or keyword in title:
            return role
    
    # Default to DEV for implementation work
    return "DEV"
```

### Multi-Agent Conversation Flow

```
User Request: "We need to add OAuth login"

1. ORCHESTRATOR (CEO+PM) Session:
   [1] PM: Breaking this into implementation phases...
   [2] CEO: Prioritize security audit before feature work
   [3] PM: Creating 3 beads: research, implement, test
   
   → bd create "Research OAuth providers" --labels research
   → bd create "Implement OAuth login flow" --labels feature
   → bd create "Security review OAuth" --labels architecture

2. SUPERVISOR (RESEARCH) Session spawns for research bead:
   [1] RESEARCH: Evaluating OAuth providers...
   [2] RESEARCH: Recommendation: Auth0 for speed, Keycloak for control
   
   → bd close research-bead --reason "Documented in docs/oauth-analysis.md"

3. SUPERVISOR (CTO) Session spawns for architecture bead:
   [1] CTO: Reviewing security implications...
   [2] CTO: Required: PKCE flow, secure token storage
   
   → Adds technical constraints to implementation bead

4. WORKER (DEV) Session spawns for implementation bead:
   - Isolated worktree created
   - Task context injected with CTO constraints
   - Implements OAuth with PKCE
   - Commits changes
   
   → bd close impl-bead --reason "OAuth implemented with Auth0"
```

---

## Comparison with Existing Patterns

| Aspect | OpenCode Agent Conversations | Speckle Gastown | Integrated Approach |
|--------|------------------------------|-----------------|---------------------|
| **Session Model** | Per-conversation | Per-bead | Per-bead with role |
| **Agent Roles** | 7 functional roles | Single worker | Role-assigned workers |
| **Isolation** | None (shared context) | Git worktree | Role + worktree |
| **Orchestration** | Single LLM | Mayor pattern | Multi-tier hierarchy |
| **Tool Control** | Mention-gated | Full access | Role-based ACL |
| **Output Format** | Threaded `[n] ROLE:` | Terminal stream | Both (context-dependent) |

---

## Implementation Phases

### Phase 1: Role-Based Session Configuration (Week 1-2)
- Extend `session_manager.py` with role parameter
- Create role-specific system prompts (`.speckle/agents/*.md`)
- Add role field to bead schema
- Implement intent-based role assignment

### Phase 2: Tier 1 Orchestrator (Week 2-3)
- Create persistent Mayor session type
- Implement worker coordination logic
- Add terminal mirroring aggregation
- Build intervention controls for STUCK sessions

### Phase 3: Tier 2 Supervisors (Week 3-4)
- Create semi-persistent session type
- Implement domain-specific tool ACLs
- Add context injection to worker sessions
- Build review/approval workflow

### Phase 4: Multi-Agent Conversations (Week 4-5)
- Port intent detection from opencode-agent-conversations
- Implement turn-based output threading
- Add cross-tier communication protocol
- Create conversation transcript logging

### Phase 5: Advanced Orchestration (Week 5-6)
- Parallel worker coordination
- Dependency-aware scheduling
- Automatic blocker detection
- Cost tracking per role/session

---

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Role confusion (wrong role for task) | Medium | High | Intent validation, role override option |
| Session explosion (too many workers) | Medium | Medium | Strict MAX_CONCURRENT limits per tier |
| Context pollution between roles | Low | High | Strict isolation, no shared state |
| Orchestrator bottleneck | Medium | Medium | Async patterns, queue management |
| Cost overrun (many sessions) | High | Medium | Token budgets per session, caching |

---

## Success Metrics

1. **Task Completion Rate**: % of beads completed without human intervention
2. **Role Accuracy**: % of beads assigned to correct role on first attempt
3. **Session Efficiency**: Average tokens per completed bead
4. **Parallelization Factor**: Average concurrent workers utilized
5. **Intervention Rate**: % of sessions requiring Tier 1/2 intervention

---

## References

1. OpenCode Agent Conversations - https://github.com/marcel-tuinstra/opencode-agent-conversations
2. AutoGen: Multi-Agent Conversation Framework (arXiv:2308.08155)
3. HAX Framework: Human-Agent Interaction (arXiv:2512.11979)
4. Anthropic Prompt Caching Documentation
5. Speckle Spec 020: Ephemeral Claude Sessions
6. LangGraph Human-in-the-Loop Patterns

---

*Analysis created: 2026-02-09*
*Author: AI Agent Analysis*
