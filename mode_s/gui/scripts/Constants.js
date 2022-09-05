const FONT_COLOR                = "#1D3557"
const ACCENT_COLOR1             = "#E63946"
const ACCENT_COLOR2             = "#8E32A8"
const ACCENT_COLOR3             = "#27dbc9"
const BACKGROUND_COLOR1         = "#F1FAEE"
const BACKGROUND_COLOR2         = "#A8DADC"
const FOREGROUND_COLOR          = "#457B9D"
const GLASSY_BACKGROUND         = Qt.rgba(255, 252, 252, 0.3)
const GLASSY_BLACK_BACKGROUND   = Qt.rgba(FONT_COLOR.r, FONT_COLOR.g, FONT_COLOR.b, 0.5)
const BORDER_WIDTH              = 4
const LOCATION                  = "LOC"
const ID_LOCATION               = "ID_LOC"
const DATABASE                  = "ID_DTB"
const ENGINE                    = "ID_EGN"
const MODE_S                    = "ID_MDS"
const TURBULENCE                = "TRB"
const KDE                       = "KDE"
const PROGRESS_BAR              = "[==>]"
const END_PROGRESS_BAR          = "[==|]"

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
const FONT_MEDIUM_NOT_BOLD = Qt.font(
    {
        bold: false,
        pointSize: 16
    }
)
const FONT_SMALL = Qt.font(
    {
        bold: false,
        pointSize: 14
    }
)

const FONT_VERY_SMALL = Qt.font(
    {
        bold: true,
        pointSize: 12
    }
)

const toUrl = (string) => {return new URL(string)}
const transparentBy = (color, grad) => { return Qt.rgba(color.r, color.g, color.b, grad) }
