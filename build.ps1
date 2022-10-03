pyinstaller --windowed --noconfirm --onedir `
            --name "Mode_S" `
            --add-data "README.md;." `
            --icon "./mode_s/gui/img/mode_s.ico" `
            --splash "./mode_s/gui/img/splash.png" `
            --paths "./mode_s/" --paths "mode_s/gui/" --paths "./mode_s/gui/scripts/" `
            --add-binary "./lib/qsql*.dll;./lib" --add-binary "./lib/qt*.dll;./geoservices" `
            ./mode_s/mode_s.py
