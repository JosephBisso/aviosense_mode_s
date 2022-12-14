const appendVerticalLine = (x, y, target) => {
    target.append(x, 0)
    target.append(x, y)
    target.append(x, 0)
}

const toUrl = (string) => { return new URL(string) }

const transparentBy = (color, grad) => { return Qt.rgba(color.r, color.g, color.b, grad) }

const nextMultipleOf5 = (num, next=true) => { 
    let niceNum = num
    let func = next ? Math.ceil : Math.round
    niceNum = func(num / 5) * 5
    return niceNum 
}
