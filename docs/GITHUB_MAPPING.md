# GitHub como referência (o que aproveitar)

Este documento mapeia a “fábrica de packs” para primitives que o GitHub já faz bem:

- **Releases/Tags (SemVer)** => Packs versionados (snapshot) com checksums.
- **Pull Request** => “Change Request” formal: aqui materializado como **OCA** (com revisão e risco).
- **Issues** => Incidentes, bugs, melhorias: aqui materializado como incident log + known issues.
- **Actions/CI** => Gates automatizados por pack (run/test/docs/manifest/audit).
- **CODEOWNERS** => Governança (responsáveis por diretórios/módulos e revisão obrigatória).

O objetivo é ter o benefício do GitHub (disciplina de mudança + rastreabilidade),
mas operando por “packs” executáveis com documentação embutida.


## Itens adicionados no RELEASE PACK 009 (inspiração GitHub)
- `.github/CODEOWNERS` (governança)
- `.github/ISSUE_TEMPLATE/*` (bugs e features com rastreabilidade)
- `.github/PULL_REQUEST_TEMPLATE.md` (link para OCA + checklist)

