# Catálogo de Proveniência e Custódia Digital

## Objetivo

Toda evidência usada pelo projeto deve ser localizável e auditável. O catálogo descreve o documento e não deve ser confundido com a avaliação de uma afirmação extraída dele.

## Metadados mínimos de uma fonte

| Campo | Obrigatório | Finalidade |
|---|---:|---|
| título | sim | identificação humana |
| autor/instituição | quando aplicável | autoria |
| data de publicação/documento | quando disponível | contextualização |
| tipologia | sim | natureza documental |
| citação formal | sim | referência bibliográfica |
| URL/identificador | quando disponível | recuperação |
| referência de arquivo | quando aplicável | custódia |
| data de acesso | sim para recursos web | reprodutibilidade |
| período coberto | quando aplicável | escopo temporal |
| hash | para arquivo baixado | integridade |
| licença/direitos | quando disponível | reutilização |
| limitações | recomendado | crítica da fonte |

## Evidência documental

A ligação entre fonte e claim deve registrar a localização exata da evidência: página, seção, parágrafo, tabela, identificador do documento ou outro marcador persistente.

O campo `excerpt` deve ser uma transcrição fiel. Se houver normalização ortográfica, correção editorial ou tradução, isso deve ser explicitado nas notas, preservando também a forma original quando necessária para auditoria.

## Independência das fontes

A contagem de fontes não deve ser usada como proxy simples de força da evidência. O protocolo deve permitir registrar que fontes distintas reproduzem uma mesma fonte primária.

No futuro, recomenda-se um relacionamento `source_derivation` ou equivalente para representar:

`Fonte A → reproduz → Fonte B`

Isso evita a falsa triangulação de múltiplas notícias que têm uma única origem documental.

## Versionamento de dados externos

Para datasets geográficos e estatísticos, uma atualização deve gerar um novo snapshot. O snapshot antigo permanece disponível para reproduzir análises anteriores.

Formato recomendado de identificação:

`<fornecedor>_<dataset>_<data-referencia>_<versao>_<hash-curto>`

## Auditoria

Antes de publicar uma análise, executar uma checagem que identifique:

- claims sem fonte;
- fontes sem metadados essenciais;
- URLs quebradas;
- hashes ausentes para arquivos que deveriam ter custódia;
- datas derivadas com precisão incompatível;
- coordenadas sem fonte geográfica;
- polígonos sem data de referência;
- relações duplicadas;
- entidades que podem ser homônimas;
- alegações conflitantes marcadas como confirmadas;
- dados DEMO misturados ao acervo histórico.
