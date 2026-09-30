# Repository profiles

Read the profile that matches the repository. Each shows the homes that
exist *when needed* — create a directory only when its first file arrives.
Profiles combine: a service with a published docs site is the service
profile plus a docs site root from `documentation-sites.md`.

## Contents

- [Single service or application](#single-service-or-application)
- [Several services](#several-services)
- [Published library](#published-library)
- [Kubernetes manifests](#kubernetes-manifests)
- [Terraform](#terraform)
- [Skill or configuration collection](#skill-or-configuration-collection)
- [Documentation-only](#documentation-only)
- [Docs taxonomies](#docs-taxonomies)

## Single service or application

```text
project/
├── README.md
├── AGENTS.md
├── pyproject.toml            native manifest; compose/Docker files at the root
├── src/<package>/<feature>/
├── tests/<feature>/          mirrors src/
├── scripts/
└── docs/
    ├── README.md
    ├── architecture/  decisions/  development/  reference/  runbooks/
```

Keep one service flat. Do not wrap it in `services/<name>/` for symmetry
with larger repositories: the wrapper holds one thing and costs every
build path, compose context, and import. `reference/` is for looked-up
facts such as tool and HTTP API references.

## Several services

```text
project/
├── README.md
├── AGENTS.md
├── services/<name>/          each runnable unit, with its own manifest and tests
├── packages/<name>/          code deliberately shared between services
├── platform/ or infra/       shared runtime components and infrastructure
├── deploy/                   deployment definitions
├── tests/e2e/                tests that span services
├── scripts/
└── docs/
```

Code used by one service stays in that service until a second service
needs it. Workspace tools (pnpm, npm/yarn workspaces, Go workspaces, uv
workspaces) have their own manifest names; follow them.

## Published library

Use the single-service layout with `src/`. Two constraints are technical,
not taste:

- Tests stay outside the package. A `tests/` folder inside `src/<package>/`
  is shipped in the wheel by both setuptools and hatchling, with or
  without `__init__.py`, unless the build config excludes it.
- Examples that users copy go in `examples/`; they are not tests.

## Kubernetes manifests

Keep the tool's native layout. For raw manifests applied in order,
numbered directories are a legitimate ordering mechanism:

```text
manifests/
├── 00-namespaces/
├── 01-cert-manager/
└── 02-ingress-nginx/
```

For Flux, use the upstream names: `clusters/<env>/`, `apps/base/`,
`apps/<env>/`, `infrastructure/controllers/`, `infrastructure/configs/`.
For Argo CD, follow its application layout. Do not force a generic `src/`
onto deployment definitions.

## Terraform

Distinguish reusable modules from live configurations:

```text
project/
├── modules/<name>/           main.tf, variables.tf, outputs.tf, README.md, examples/
├── <provider-or-area>/<stack>/   live root configurations, one state each
├── pipelines/
└── docs/
```

A single reusable module repository puts `main.tf`, `variables.tf`,
`outputs.tf`, and `README.md` at its root, with `modules/` and `examples/`
beside them (HashiCorp's standard module structure). Use lowercase
directory names.

## Skill or configuration collection

```text
project/
├── skills/<name>/            SKILL.md plus scripts/, references/, assets/ when needed
├── scripts/                  repository-wide tooling
├── tests/                    tests for all bundled and repository scripts
├── state/                    only if generated records must be committed
└── docs/
```

Skill internals follow the Agent Skills specification: `name` matches the
directory, `SKILL.md` stays under 500 lines, and references are linked one
level deep from `SKILL.md`. Nothing inside a skill directory should exist
only for the repository's own bookkeeping, because it ships with the skill.

## Documentation-only

The repository root is the documentation root. The renderer's native
layout applies at the top level; code-profile rules do not.

## Docs taxonomies

Pick one per repository, declare it in `docs/README.md`, and do not mix
them:

| Taxonomy | Directories | Fits |
|---|---|---|
| Subject | `architecture/`, `decisions/`, `development/`, `reference/`, `runbooks/` | Products and services: readers arrive with a task |
| Lifecycle | `canonical/`, `historical/`, `research/` | Research-heavy and tooling repositories: readers need to know whether something is still true |

Under the subject taxonomy, "is this still true?" is answered by the
decision record's status, not by the directory. Under the lifecycle
taxonomy, decisions are `historical/` records with a stated disposition.
