# Dolphin Converter

Convertisseur de fichiers universel, 100 % local et natif pour KDE Plasma (Dolphin) utilisant l'API KIO Service Menus.

## Fonctionnalites

- Selection multiple de fichiers (%F) avec parallelisme borne.
- Menus contextuels adaptes par famille de fichiers (Images, Audio/Video, Documents).
- Remplacement propre de l'extension d'origine et gestion des doublons (`nom_1.ext`).
- Notifications natives KDE Plasma au demarrage et a l'achevement.
- Moteur d'orchestration Python 3 sans aucune dependance pip.

## Prerequis

- `python` (>= 3.10)
- `ffmpeg`
- `imagemagick`
- `poppler` (`pdftoppm`)
- `libnotify` (`notify-send`)

Optionnel :
- `libreoffice-fresh` ou `openoffice-bin` (pour documents Word/LibreOffice/OpenOffice vers PDF)
- `pandoc-cli` (pour conversion Markdown vers DOCX/HTML et DOCX vers Markdown)

## Installation rapide (Espace utilisateur)

```bash
./install.fish
```
ou
```bash
make user-install
```

## Utilisation CLI directe

```bash
dolphin-convert --format webp photo1.jpg photo2.png
dolphin-convert --format mp3 video.mp4
dolphin-convert --format png document.pdf
```

## Tests

```bash
make test
```

## Workflow de Contribution

Le projet suit un flux Git structure :

1. Creer une branche de fonctionnalite (`feat/...`) ou de correction (`fix/...`) depuis `develop`.
2. Ouvrir une Pull Request vers la branche `develop`.
3. Apres revue, tests et validation sur `develop`, ouvrir une Pull Request de `develop` vers `main`.
4. La branche `main` est protegee : tout changement passe obligatoirement par une PR validee.

## Licence

Ce projet est distribue sous licence MIT. Consultez le fichier [LICENSE](LICENSE) pour plus de details.
