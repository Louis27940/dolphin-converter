PREFIX ?= /usr
USER_BIN ?= $(HOME)/.local/bin
USER_MENUS ?= $(HOME)/.local/share/kio/servicemenus
SYSTEM_BIN ?= $(DESTDIR)$(PREFIX)/bin
SYSTEM_MENUS ?= $(DESTDIR)$(PREFIX)/share/kio/servicemenus

.PHONY: all test user-install user-uninstall install uninstall

all:
	@echo "Cibles disponibles :"
	@echo "  make test            - Execute la suite de tests unitaires"
	@echo "  make user-install    - Installe dans ~/.local/ (sans sudo)"
	@echo "  make user-uninstall  - Desinstalle de ~/.local/"
	@echo "  make install         - Installe au niveau systeme (requiert sudo)"
	@echo "  make uninstall       - Desinstalle au niveau systeme"

test:
	python3 -m unittest discover tests

user-install:
	mkdir -p $(USER_BIN)
	mkdir -p $(USER_MENUS)
	cp bin/dolphin-convert $(USER_BIN)/dolphin-convert
	chmod +x $(USER_BIN)/dolphin-convert
	cp servicemenus/*.desktop $(USER_MENUS)/
	chmod +x $(USER_MENUS)/*.desktop
	@echo "Installation utilisateur terminee."

user-uninstall:
	rm -f $(USER_BIN)/dolphin-convert
	rm -f $(USER_MENUS)/converter-images.desktop
	rm -f $(USER_MENUS)/converter-audio-video.desktop
	rm -f $(USER_MENUS)/converter-documents.desktop
	@echo "Desinstallation utilisateur terminee."

install:
	mkdir -p $(SYSTEM_BIN)
	mkdir -p $(SYSTEM_MENUS)
	install -m 755 bin/dolphin-convert $(SYSTEM_BIN)/dolphin-convert
	install -m 644 servicemenus/*.desktop $(SYSTEM_MENUS)/

uninstall:
	rm -f $(SYSTEM_BIN)/dolphin-convert
	rm -f $(SYSTEM_MENUS)/converter-images.desktop
	rm -f $(SYSTEM_MENUS)/converter-audio-video.desktop
	rm -f $(SYSTEM_MENUS)/converter-documents.desktop
