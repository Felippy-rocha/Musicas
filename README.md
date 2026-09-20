# Montagem de todas as músicas (3x)

Este repositório contém um script reproduzível para gerar `./montagem_todas_as_musicas_3x.mp3` a partir de todos os arquivos `.mp3`/`.MP3` da raiz.

## Regras usadas

- todos os 48 MP3 da raiz entram na montagem;
- a ordenação usa o número inicial do nome do arquivo em ordem crescente;
- a faixa "Nossa Senhora do Amparo" fica depois das faixas `16` e antes da `17`;
- os dois arquivos iniciados por `30.` permanecem na posição 30, em ordem natural do nome;
- cada música é repetida 3 vezes consecutivas antes da próxima.

## Ordem das faixas

1. `1. Bodas de Ouro.mp3`
2. `2. bodas de prata.mp3`
3. `3. Araguari.mp3`
4. `4. Branca.mp3`
5. `5. do bras ( rapaziada).mp3`
6. `6. Lagrimas de virgem.mp3`
7. `7. Matao.mp3`
8. `8. Meia Noite.mp3`
9. `9. minha Terra.mp3`
10. `10. Ouro fino.mp3`
11. `11. Ouro Preto.mp3`
12. `12. Rapaziada do Bras.mp3`
13. `13. Tatui.mp3`
14. `14.Viajando pela Italia.mp3`
15. `15. Vila Rica.mp3`
16. `16. O  Rapaziada do Braz.mp3`
17. arquivo de prefixo `16.1` — "Nossa Senhora do Amparo"
18. `17. O veio macho.mp3`
19. `18. Xote dos cabeludos.mp3`
20. `19. Xote Ecolologico.mp3`
21. `20. Xote Rodado.mp3`
22. `21. O xote das meninas.mp3`
23. `22. BAIAO DA ESPERANCA.mp3`
24. `23. Baião Da Saudade.mp3`
25. `24. El Besame Mucho.mp3`
26. `25. CORINTIANO.MP3`
27. `26. Coracao De Artista.mp3`
28. `27. delirando no choro.mp3`
29. `28. Delirando.mp3`
30. `29. CAMPONESA.mp3`
31. `30. COSTUME SERTANEJO.mp3`
32. `30. CRIOULA.MP3`
33. `31. Festa Na Roca - - Inst.mp3`
34. `32. forro  instrumental.mp3`
35. `33. naquele são joao.mp3`
36. `34. rei do baralho.mp3`
37. `35. Revendo Iracema.mp3`
38. `36. Revendo itapoa.mp3`
39. `37. Riacho do navio.MP3`
40. `38. SABIA DO SERTAO.mp3`
41. `39. Sabia.mp3`
42. `40. Sanfona do povo.mp3`
43. `41. Sao Joao na Roca.mp3`
44. `42. Sentimental.mp3`
45. `43. CASACA DE COURO.mp3`
46. `44. ESCADARIA.MP3`
47. `45. Futurista.mp3`
48. `46. rato molhado.mp3`

## Como gerar

Na raiz do repositório, com `ffmpeg` instalado:

```bash
python3 gerar_montagem_todas_as_musicas_3x.py
```

Para validar a ordem e a repetição sem gerar o MP3:

```bash
python3 gerar_montagem_todas_as_musicas_3x.py --dry-run
```

## Limitação de tamanho

Os MP3 de origem somam `143172806` bytes. Como o script usa concatenação contínua por `stream copy`, repetir todas as faixas 3 vezes leva a uma montagem estimada em aproximadamente `429518418` bytes, além de pequeno overhead de encapsulamento, ultrapassando o limite prático de arquivos versionados no GitHub. Por isso, o arquivo `montagem_todas_as_musicas_3x.mp3` não foi incluído no commit.
