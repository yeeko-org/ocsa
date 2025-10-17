import vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'
// import dotenv from 'dotenv'
// import fs from 'fs'
// import path from 'path'
// dotenv.config()
export default defineNuxtConfig({
  runtimeConfig: {
    // Las claves aquí solo están disponibles en el lado del servidor
    // Ejemplo: apiSecret: '123'
    mapboxToken: process.env.NUXT_MAPBOX_TOKEN,

    // Las claves dentro de `public` están disponibles también en el lado del cliente
    public: {
      apiUrl: process.env.NUXT_API_URL,
      adminUrl: process.env.NUXT_ADMIN_URL,
      // mapboxToken: process.env.NUXT_MAPBOX_TOKEN
    }
  },
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
  nitro: {
    devServer: {
      timeout: 300000
    }
  },
  vite: {
    vue: {
      template: {
        transformAssetUrls,
      },
    },
  },

  compatibilityDate: '2025-08-06'
})