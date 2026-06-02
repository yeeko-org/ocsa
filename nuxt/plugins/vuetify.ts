// import '@mdi/font/css/materialdesignicons.css'
// import 'material-design-icons-iconfont/dist/material-design-icons.css'
import '@fontsource/roboto/300.css'
import '@fontsource/roboto/400.css'
import '@fontsource/roboto/500.css'
import '@fontsource/roboto/700.css'
import { h } from 'vue'
// import { aliases, md } from 'vuetify/iconsets/md'

import { aliases as mdAliases } from 'vuetify/iconsets/md'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import { VDateInput } from "vuetify/components/VDateInput"

const materialSymbols = {
  component: (props: { tag: string; icon: string }) =>
    h(props.tag, { class: 'material-symbols-outlined' }, props.icon),
}


export default defineNuxtPlugin((app) => {
  const vuetify = createVuetify({
    components: {
      VDateInput
    },
    theme: {
      defaultTheme: 'light',
      themes: {
        light: {
          dark: false,
          colors: {
            // primary: colors.indigo.darken1,
            // secondary: '#424242',
            // accent: colors.teal.accent4,
            primary: "#ff002f",
            secondary: "#d7a997",
            accent: "#1e1e1e",
          }
        }
      }
    },
    icons: {
      defaultSet: 'ms',
      aliases: mdAliases,   // Los nombres internos de Vuetify son iguales
      sets: {
        ms: materialSymbols,
      }
    },
    // icons: {
    //   defaultSet: 'md',
    //   aliases,
    //   sets: {
    //     md,
    //   }
    // },
    date: {
      locale: {
        'es-MX': {
          firstDayOfWeek: 0,
          masks: {
              input: 'DD/MM/YYYY',
              date: 'DD/MM/YYYY',
              time: 'HH:mm',
              datetime: 'DD/MM/YYYY HH:mm',
          },
        },
      },
    }
  })
  app.vueApp.use(vuetify)
})