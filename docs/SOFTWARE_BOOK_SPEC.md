# Software Book — Especificação

O **Software Book** é um artefato gerado automaticamente pelo `lai-pack` para reduzir custo de manutenção,
acelerar onboarding e eliminar “caça ao arquivo”.

## Onde fica
`docs/public/SOFTWARE_BOOK.md`

## Conteúdo mínimo obrigatório
1. **Visão geral do sistema**
2. **Arquitetura atual (snapshot)**
3. **Como rodar** (runbooks detectados)
4. **Como testar** (test harness detectado)
5. **Mapa de diretórios (FileMap)**
6. **Contratos e eventos**
7. **Histórico operacional**
   - incidentes (quando existirem)
   - mudanças (OCAs, merges)
8. **Troubleshooting**
   - sintomas → causa provável → correção padrão → rollback

## Regra importante (append-only)
O Software Book pode ser re-gerado, mas os registros operacionais em `history/` são **append-only**.
O gerador **não deve** apagar histórico.

## Determinismo
- Ordenação de arquivos é sempre alfabética.
- Lista de packs merged deve ser registrada.
- Se existir manifesto, ele é usado como referência, mas o gerador não depende dele.

