# Montagem das músicas em 3 partes

Este repositório guarda as 48 faixas MP3 originais. A montagem final não é versionada no GitHub porque o conjunto completo fica grande demais, então a geração acontece sob demanda no **GitHub Actions** e o resultado fica disponível como **artefatos da execução**.

## O que a automação faz

- encontra as **48 faixas MP3** na raiz do repositório;
- preserva os arquivos originais;
- repete **cada faixa 3 vezes consecutivas** antes de passar para a próxima;
- gera **exatamente 3 arquivos MP3** na ordem correta;
- interrompe a execução se a contagem, a ordem ou a repetição estiverem erradas.

## Como gerar e baixar pelo GitHub

1. Abra a aba **Actions** do repositório.
2. Clique no workflow **Gerar montagem em 3 partes**.
3. Clique em **Run workflow**.
4. Aguarde a execução terminar.
5. Abra a execução concluída e baixe os artefatos:
   - `montagem_todas_as_musicas_3x_parte_1`
   - `montagem_todas_as_musicas_3x_parte_2`
   - `montagem_todas_as_musicas_3x_parte_3`

> Importante: o workflow **não roda automaticamente**. Ainda é necessário clicar em **Run workflow** no GitHub para iniciar a geração.

## Sobre o formato gerado

Para tornar a concatenação mais confiável entre MP3 com possíveis diferenças de codificação, o script usa o `ffmpeg` para **reencodar** cada parte com `libmp3lame` (`-q:a 2`). Assim, cada uma das 3 partes sai pronta para reprodução.

## Uso local opcional

Se você tiver Python 3 e `ffmpeg`, também pode validar ou gerar localmente:

```bash
python3 gerar_montagem_todas_as_musicas_3x.py validate --input-dir .
python3 gerar_montagem_todas_as_musicas_3x.py generate --input-dir . --output-dir output/montagem_3_partes --parts 3
```

Os MP3 gerados ficam fora da árvore versionada e não devem ser commitados no repositório.
