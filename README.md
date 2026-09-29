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
- `libreoffice-fresh` (pour documents Word/LibreOffice vers PDF)
- `pandoc-cli` (pour Markdown vers DOCX/PDF)

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
