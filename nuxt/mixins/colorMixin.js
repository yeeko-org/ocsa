import colors from 'vuetify/lib/util/colors';

const SHADE_KEYWORDS = ['lighten', 'darken']

function parseVuetifyColor(raw) {
  const parts = raw.split('-')
  const shadeIdx = parts.findIndex((p) => SHADE_KEYWORDS.includes(p))

  const baseParts = shadeIdx === -1 ? parts : parts.slice(0, shadeIdx)
  const shadeParts = shadeIdx === -1 ? [] : parts.slice(shadeIdx)

  const baseCss = baseParts.join('-')
  const baseJs = baseParts[0] + baseParts.slice(1)
    .map((p) => p[0].toUpperCase() + p.slice(1))
    .join('')

  const shadeCss = shadeParts.join('-')
  const shadeJs = shadeParts.length ? shadeParts.join('') : 'base'

  return { baseCss, baseJs, shadeCss, shadeJs }
}

let colorMixin = {
  methods: {
    getComplementColor(st) {
      if (!st.color) {
        st.color_text = ''
        st.back_text = ''
        return st
      }

      const { baseCss, baseJs, shadeCss, shadeJs } =
        parseVuetifyColor(st.color)

      st.color_text = shadeCss
        ? `${baseCss}--text text--${shadeCss}`
        : `${baseCss}--text`

      try {
        const hex = colors[baseJs][shadeJs]
        if (!hex) {
          st.back_text = 'black--text'
          return st
        }
        const h = hex.replace('#', '')
        const r = parseInt(h.substr(0, 2), 16)
        const g = parseInt(h.substr(2, 2), 16)
        const b = parseInt(h.substr(4, 2), 16)
        const yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000
        st.back_text = yiq >= 128 ? 'black--text' : 'white--text'
      } catch (e) {
        console.log(e, 'baseJs:', baseJs, 'shadeJs:', shadeJs)
        st.back_text = 'black--text'
      }

      return st
    }
  }
}

export default colorMixin;
