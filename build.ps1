pyinstaller --windowed --noconfirm --onedir `
            --name "mode_s" `
            --add-data "README.md;." `
            --icon "./src/gui/img/mode_s.ico" `
            --splash "./src/gui/img/splash.png" `
            --paths "src/gui/" --paths "./mode_s/gui/scripts/" `
            --paths "./src/app" --paths "./src/gui/" --paths "./src/mode_s/" `
            --add-binary "./lib/qsql*.dll;./lib" --add-binary "./lib/qt*.dll;./geoservices" `
            ./mode_s/mode_s.py
