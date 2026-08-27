import {defineConfig} from 'vitest/config'
import {createRequire} from 'node:module'
import {dirname, resolve} from 'node:path'
import {fileURLToPath} from 'node:url'

const root = dirname(fileURLToPath(import.meta.url))

// pnpm no expone pinia en la raíz de node_modules: llega como dependencia de
// @pinia/nuxt, y fuera de Nuxt hay que resolverla desde ahí.
const pinia_entry = createRequire(
    resolve(root, 'node_modules/@pinia/nuxt') + '/').resolve('pinia')

export default defineConfig({
  resolve: {
    alias: {
      '~': resolve(root),
      pinia: pinia_entry,
    },
  },
  test: {
    environment: 'node',
    include: ['**/__tests__/**/*.test.js'],
  },
})
