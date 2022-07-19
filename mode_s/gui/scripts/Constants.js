const FONT_COLOR        = "#1D3557"
const ACCENT_COLOR1     = "#E63946"
const ACCENT_COLOR2     = "#8E32A8"
const BACKGROUND_COLOR1 = "#F1FAEE"
const BACKGROUND_COLOR2 = "#A8DADC"
const FOREGROUND_COLOR  = "#457B9D"
const GLASSY_BACKGROUND = Qt.rgba(255, 252, 252, 0.3)

const FONT_VERY_BIG = Qt.font(
    {
        bold: true,
        pointSize: 32
    }
)
const FONT_BIG = Qt.font(
    {
        bold: true,
        pointSize: 20
    }
)
const FONT_MEDIUM = Qt.font(
    {
        bold: true,
        pointSize: 16
    }
)
const FONT_SMALL = Qt.font(
    {
        bold: false,
        pointSize: 15
    }
)

const toUrl = (string) => {return new URL(string)}
