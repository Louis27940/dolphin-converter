#!/usr/bin/env fish

set -l USER_BIN "$HOME/.local/bin"
set -l USER_MENUS "$HOME/.local/share/kio/servicemenus"
set -l SCRIPT_DIR (status dirname)

function show_help
    echo "Usage: ./install.fish [--uninstall]"
    echo "  --uninstall   Supprime Dolphin Converter de ~/.local/"
    echo "  --help        Affiche cette aide"
end

if test (count $argv) -gt 0
    switch $argv[1]
        case "--uninstall"
            echo "Desinstallation de Dolphin Converter..."
            rm -f "$USER_BIN/dolphin-convert"
            rm -f "$USER_MENUS/converter-images.desktop"
            rm -f "$USER_MENUS/converter-audio-video.desktop"
            rm -f "$USER_MENUS/converter-documents.desktop"
            echo "Desinstallation terminee."
            exit 0
        case "--help" "-h"
            show_help
            exit 0
        case "*"
            echo "Option inconnue : $argv[1]"
            show_help
            exit 1
    end
end

echo "=== Verification des dependances ==="
set -l missing_core 0
for tool in python3 ffmpeg magick pdftoppm notify-send
    if not command -v $tool >/dev/null 2>&1
        if test "$tool" = "magick"
            if not command -v convert >/dev/null 2>&1
                echo "Attention: $tool introuvable (requis pour les images)"
                set missing_core 1
            end
        else
            echo "Attention: $tool introuvable (recommande)"
            set missing_core 1
        end
    else
        echo "Present: $tool"
    end
end

echo ""
echo "=== Verification des outils optionnels ==="
for opt_tool in libreoffice pandoc
    if not command -v $opt_tool >/dev/null 2>&1
        echo "Optionnel absent: $opt_tool (necessaire pour conversion Office/Markdown)"
    else
        echo "Optionnel present: $opt_tool"
    end
end

echo ""
echo "=== Installation en espace utilisateur ==="
mkdir -p "$USER_BIN"
mkdir -p "$USER_MENUS"

cp "$SCRIPT_DIR/bin/dolphin-convert" "$USER_BIN/dolphin-convert"
chmod +x "$USER_BIN/dolphin-convert"

cp "$SCRIPT_DIR/servicemenus/"*.desktop "$USER_MENUS/"

echo "Installation reussie dans :"
echo "  - Binaire      : $USER_BIN/dolphin-convert"
echo "  - Menus KIO    : $USER_MENUS/"
echo ""
echo "Pour recharger Dolphin, relancez l'application ou redemarrez votre session."
