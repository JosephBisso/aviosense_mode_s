pyinstaller --windowed --noconfirm --onedir `
            --name "mode_s" `
            --add-data "README.md;." `
            --icon "./src/gui/img/mode_s.ico" `
            --splash "./src/gui/img/splash.png" `
            --paths "src/gui/" --paths "./src/gui/scripts/" `
            --paths "./src/app" --paths "./src/mode_s/" `
            --add-binary "./lib/qt*.dll;./geoservices" `
            ./src/app/main.py
