const appendVerticalLine = (x, y, target) => {
    target.append(x, 0)
    target.append(x, y)
    target.append(x, 0)
}

const toUrl = (string) => { return new URL(string) }

const transparentBy = (color, grad) => { return Qt.rgba(color.r, color.g, color.b, grad) }

const nextMultipleOf5 = (num, next=true) => { 
    let niceNum = (Math.ceil(num / 5) * 5)
    let offset = 0
    if ((next && num / niceNum > 0.95) || (!next && niceNum / num > 0.95)) {
        offset = (Math.ceil(niceNum / 50) * 5)
    }
    return niceNum + (next ? 1 : -1) * offset 
}
