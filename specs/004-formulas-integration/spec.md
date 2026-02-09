# Feature Specification: Formulas Integration

**Feature Branch**: `004-formulas-integration`  
**Created**: 2026-02-09  
**Status**: Draft

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Feature Formula (Priority: P1)

As a developer starting a new feature, I want to run a formula that sets up the entire Speckle workflow, so I can start working immediately with proper tracking.

**Acceptance Scenarios**:

1. **Given** I run `bd formula speckle-feature "Add user auth"`, **When** completed, **Then**:
   - Feature branch created (NNN-feature-name)
   - Spec directory created (specs/NNN-feature-name/)
   - Epic issue created with proper labels
   - Ready to run /speckit.specify

---

### User Story 2 - Bugfix Formula (Priority: P2)

As a developer fixing a bug, I want a lightweight formula that creates tracking without full spec-kit overhead.

**Acceptance Scenarios**:

1. **Given** I run `bd formula speckle-bugfix "Fix login timeout"`, **When** completed, **Then**:
   - Bugfix branch created (fix-NNN-description)
   - Single issue created with type=bug
   - Linked to relevant epic if specified

---

### User Story 3 - Formula Installation (Priority: P3)

As a user installing Speckle, I want formulas automatically available in my project.

**Acceptance Scenarios**:

1. **Given** I run `./install.sh`, **When** beads is initialized, **Then** formulas are copied to `.beads/formulas/`

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Provide `speckle-feature.toml` formula for feature workflows
- **FR-002**: Provide `speckle-bugfix.toml` formula for bugfix workflows
- **FR-003**: Install script MUST copy formulas to `.beads/formulas/`
- **FR-004**: Formulas MUST use Speckle conventions (branch naming, labels)

### Key Entities

- **Formula**: TOML file defining issue creation template with prompts
- **Feature Formula**: Full workflow setup (branch, dir, epic, labels)
- **Bugfix Formula**: Lightweight bug tracking setup

## Success Criteria

- **SC-001**: `bd formula speckle-feature` creates working feature setup
- **SC-002**: `bd formula speckle-bugfix` creates proper bug tracking
- **SC-003**: Formulas available after running install.sh
