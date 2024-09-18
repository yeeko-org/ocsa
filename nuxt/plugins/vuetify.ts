// import '@mdi/font/css/materialdesignicons.css'
import 'material-design-icons-iconfont/dist/material-design-icons.css'
import { aliases, md } from 'vuetify/iconsets/md'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import { VDateInput } from "vuetify/labs/VDateInput"

export default defineNuxtPlugin((app) => {
  const vuetify = createVuetify({
    components: {
      VDateInput
    },
    icons: {
      defaultSet: 'md',
      aliases,
      sets: {
        md,
      }
    },
  })
  app.vueApp.use(vuetify)
})