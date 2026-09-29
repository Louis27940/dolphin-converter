# Maintainer: Louis SIMON <louis.simon@supinfo.com>
pkgname=dolphin-converter
pkgver=1.0.0
pkgrel=1
pkgdesc="Convertisseur de fichiers universel integre pour Dolphin KDE Plasma via KIO Service Menus"
arch=('any')
url="https://github.com/Louis27940/dolphin-converter"
license=('MIT')
depends=('python' 'ffmpeg' 'imagemagick' 'poppler' 'libnotify')
optdepends=(
    'libreoffice-fresh: conversion des documents bureautiques vers PDF'
    'pandoc-cli: conversion des documents Markdown'
)
source=("$pkgname-$pkgver.tar.gz::https://github.com/Louis27940/$pkgname/archive/v$pkgver.tar.gz")
sha256sums=('SKIP')

package() {
    cd "$srcdir/$pkgname-$pkgver" 2>/dev/null || cd "$startdir"
    install -Dm755 bin/dolphin-convert "$pkgdir/usr/bin/dolphin-convert"
    install -d "$pkgdir/usr/share/kio/servicemenus"
    install -m644 servicemenus/*.desktop "$pkgdir/usr/share/kio/servicemenus/"
}
