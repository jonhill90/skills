# Repository profiles

Read the profile that matches the repository. Each shows the homes that
exist *when needed* — create a directory only when its first file arrives.
Profiles combine: a service with a published docs site is the service
profile plus a docs site root from `documentation-sites.md`.

## Contents

- [Single service or application](#single-service-or-application)
- [Several services](#several-services)
- [Published library](#published-library)
- [Platform repository](#platform-repository)
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

## Platform repository

Infrastructure and its configuration for one platform (a homelab, a
cluster, its private network), with apps in their own repositories.
Top-level folders are capabilities, each created when its first file
arrives:

```text
platform/
├── README.md  AGENTS.md  SECURITY.md
├── .github/workflows/        shared checks, CI for code in src/
├── docs/                     decisions/, runbooks/, diagrams/
├── private-network/          network policy (tags only in a public repo)
├── hosts/                    machines under the clusters; ansible/ etc. below
├── kubernetes/               clusters/<role>/, infrastructure/<capability>/, apps/<app>/
├── dns/
├── backup/
├── src/<component>/          only for code you build (controllers, tools)
└── scripts/                  only for scripts that serve the whole repo
```

- Under `kubernetes/infrastructure/<capability>/`, files sit flat until a
  second vendor product shares the capability; then each gets one
  subfolder.
- An app's own source stays in its repository; this repository holds only
  its deploy files in `kubernetes/apps/<app>/`.
- A manifest that pulls a secret lives with the component that uses it;
  `infrastructure/secrets/` holds only the sync operator and its store.
- A per-cluster change to shared infrastructure is a patch in that
  cluster's GitOps entry point, not an overlay folder.

## Kubernetes manifests

Keep the tool's native layout. Order with the GitOps engine (Flux
`dependsOn`, Argo CD sync waves), not with numbered directories: numbered
stages get renumbered, and renumbering touches every path that reads them.
Plain `kubectl apply` in order is the only case for numbers, and it should
not outlive the first GitOps engine.

For Flux, use the upstream names: `clusters/<env>/`, `apps/base/`,
`apps/<env>/`, `infrastructure/controllers/`, `infrastructure/configs/`.
For Argo CD, follow its application layout. Do not force a generic `src/`
onto deployment definitions.

## Terraform

Distinguish reusable modules from live configurations:

```text
project/
├── modules/<name>/           main.tf, variables.tf, outputs.tf, README.md, examples/
├── <capability>/terraform/stacks/<stack>/   live root configurations, one state each
├── pipelines/
└── docs/
```

Name the folder above a stack for its capability (`dns/`, `backup/`), not
for the provider: a provider in the path is a vendor product you may
replace. A module used by one capability lives in
`<capability>/terraform/modules/<name>/`; `modules/` at the root is for
modules shared by two or more. Plan may run on pull requests only without
cloud credentials; apply runs from the default branch or by hand. State is
remote and never committed.

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
