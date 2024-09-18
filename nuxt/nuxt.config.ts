import vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'
// import fs from 'fs'
// import path from 'path'
export default defineNuxtConfig({
  //...
  build: {
    transpile: ['vuetify'],
  },
  // devtools: { enabled: true }
  modules: [
    '@pinia/nuxt',
    (_options, nuxt) => {
      nuxt.hooks.hook('vite:extendConfig', (config) => {
        // @ts-expect-error
        config.plugins.push(vuetify({ autoImport: true }))
      })
    },
  ],
  // set .pem and .key files to be served by vite and build https
  devServer: {
    https: {
      // key: fs.readFileSync(path.resolve(__dirname, 'localhost-key.pem')),
      // cert: fs.readFileSync(path.resolve(__dirname, 'localhost.pem')),
      key: 'localhost-key.pem',
      cert: 'localhost.pem',
    },
  },
  vite: {
    vue: {
      template: {
        transformAssetUrls,
      },
    },
  }
})
