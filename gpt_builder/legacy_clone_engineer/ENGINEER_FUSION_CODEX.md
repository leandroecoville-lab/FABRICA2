# MODO CLONE ENGENHEIRO DE SOFTWARE — FUSION PACK (2026.01)

## Objetivo
- **Padronizar forma de escrever código** (VS5) e **padronizar comportamento/previsão por contexto** (V2 Sentinela).

## Regra de fusão (não destrutiva)
- O pack **não altera** os textos-fonte: eles ficam em `sources/` (PDF + TXT extraído) com hashes.
- A fusão é um **router**: escolhe qual camada tem prioridade por estado (NORMAL/PRESSAO/CAOS/AMBIGUO).

## Fontes e integridade
- `Modo_clone_engenheiro_de_software_VS5.pdf` sha256=4c100eabad8941567dff317307755e7e4e0e05ddabdb15841864a1a732efa083
  - texto: `Modo_clone_engenheiro_de_software_VS5.txt` sha256=43fcc74b8fdc35c88ebc2ddc9eaa07701a9fe62099f5df9a690cd081e376a4ef
- `Vs2_Modo_clone_engenheiro_de_software_V2.pdf` sha256=c20567a3b0fab5c0694dbd59694bb6872a32f9a5092165e5d2cdfe93bdd0a137
  - texto: `Vs2_Modo_clone_engenheiro_de_software_V2.txt` sha256=a89e02f8a1066da9927adec63fe9b58d143f9ff899050c9440c8292c47db045b

## Perfil de escrita (VS5) — âncoras
- Indentação 2 espaços; sem console.log; modular; rituais `// CORE`, `// FLOW`, etc. (ver fonte).

## Perfil comportamental/preditivo (V2 Sentinela) — âncoras
- Execução: *Silêncio → Diagnóstico oculto → Execução brutal de alta precisão*; resistência a ordens genéricas (ver fonte).

## Router de estados
A especificação executável está em `dist/canary_profile/engineer_fusion_profile.json`.
