import vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'

export default defineNuxtConfig({
  runtimeConfig: {
    mapboxToken: process.env.NUXT_MAPBOX_TOKEN,
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
  app: {
    head: {
      link: [
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0'
        }
      ]
    }
  },
  devServer: {
    https: {
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