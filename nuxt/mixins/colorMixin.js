import colors from 'vuetify/lib/util/colors';

const SHADE_KEYWORDS = ['lighten', 'darken']

export function parseVuetifyColor(raw) {
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

// Resuelve cualquier color a hex (#rrggbb). Deja pasar los que ya son hex y
// traduce los nombres Vuetify ('deep-purple', 'brown', 'blue-lighten-3'…) con
// el mismo parser/lookup que usa getComplementColor. Devuelve null si no
// reconoce el color.
export function colorToHex(color) {
  if (!color) return null
  if (color.startsWith('#')) return color
  const { baseJs, shadeJs } = parseVuetifyColor(color)
  try {
    return colors[baseJs][shadeJs] || null
  } catch (e) {
    return null
  }
}

let colorMixin = {
  methods: {
    getComplementColor(st) {
      if (!st.color) {
        st.color_text = ''
        st.back_text = ''
        return st
      }

      const { baseJs, shadeJs } = parseVuetifyColor(st.color)

      // color_text: nombre de color (no clase) para la prop :color del icono.
      // back_text: clase de texto Vuetify 4 para el contenido del chip/tooltip.
      // Ambos derivan del contraste YIQ contra el color de fondo del status.
      try {
        const hex = colors[baseJs][shadeJs]
        if (!hex) {
          st.color_text = 'black'
          st.back_text = 'text-black'
          return st
        }
        const h = hex.replace('#', '')
        const r = parseInt(h.substr(0, 2), 16)
        const g = parseInt(h.substr(2, 2), 16)
        const b = parseInt(h.substr(4, 2), 16)
        const yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000
        const is_light = yiq >= 128
        st.color_text = is_light ? 'black' : 'white'
        st.back_text = is_light ? 'text-black' : 'text-white'
      } catch (e) {
        console.log(e, 'baseJs:', baseJs, 'shadeJs:', shadeJs)
        st.color_text = 'black'
        st.back_text = 'text-black'
      }

      return st
    }
  }
}

export default colorMixin;
