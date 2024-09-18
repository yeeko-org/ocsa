import colors from 'vuetify/lib/util/colors';

let colorMixin = {
  methods: {
    kebabToCamel(s) {
      return s.replace(/-([a-z])/g, (g) => g[1].toUpperCase());
    },
    getComplementColor(st){
      if (st.color){
        let color_split = st.color.split(" ")
        if (color_split.length > 1){
          st.color_text = color_split.reduce((str, color)=>
            str + (/\d/.test(color)
              ? `text--${color} `
              : `${color}--text `)
          ,'')
        }
        else{
          st.color_text = `${st.color}--text`
        }
        let base_color = this.kebabToCamel(color_split[0])
        let complement_color = 'base'

        if (color_split.length > 1)
          complement_color = color_split[1].replace('-', '')
        // console.log(colors[base_color])
        try {
          let color = colors[base_color][complement_color]
          if (!color)
            st.back_text = 'black--text'
          let color_hex = color.replace('#', '')
          let r = parseInt(color_hex.substr(0, 2), 16)
          let g = parseInt(color_hex.substr(2, 2), 16)
          let b = parseInt(color_hex.substr(4, 2), 16)
          let yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000
          // return (yiq >= 128) ? 'black--text' : 'white--text'
          st.back_text = (yiq >= 128) ? 'black--text' : 'white--text'

        } catch (e) {
          console.log(e)
          console.log("colors", colors)
          console.log("base_color", base_color)
          st.back_text = 'black--text'
        }
      }
      else {
        st.color_text = ''
        st.back_text = ''
      }
      return st
    }
  }
}

export default colorMixin;
