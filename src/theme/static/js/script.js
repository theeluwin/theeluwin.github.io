const wow = () => {
  const interval = 15
  const dom = document.getElementById('wow')
  if (!dom) return
  const hex = ['00', '14', '28', '3C', '50', '64', '78', '8C', 'A0', 'B4', 'C8', 'DC', 'F0']
  let r = 1
  let g = 1
  let b = 1
  let seq = 1
  const change = () => {
    if(seq === 6) {
      b = b - 1
      if(b === 0) {
        seq = 1
      }
    }
    if(seq === 5) {
      r = r + 1
      if(r === 12) {
        seq = 6
      }
    }
    if(seq === 4) {
      g = g - 1
      if(g === 0) {
        seq = 5
      }
    }
    if(seq === 3) {
      b = b + 1
      if(b === 12) {
        seq = 4
      }
    }
    if(seq === 2) {
      r = r - 1
      if(r === 0) {
        seq = 3
      }
    }
    if(seq === 1) {
      g = g + 1
      if(g === 12) {
        seq = 2
      }
    }
    rainbow = "#" + hex[r] + hex[g] + hex[b]
    dom.style.color = rainbow
  }
  setInterval(() => change(), interval)
}

wow()
