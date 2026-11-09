// Plegado único de las búsquedas locales (selects del dashboard y buscador
// del mapa): sin acentos, sin apóstrofos y en minúsculas, así «wixarika»
// encuentra «Wixárika», «nuu savi» encuentra «Ñuu Savi» y «mephaa» o
// «me'phaa» encuentran «Me´phaa». NFD separa la tilde en un diacrítico
// combinante (U+0300–U+036F); los apóstrofos tipográficos no se
// descomponen y se quitan aparte.
const APOSTROPHES = /['’‘´`ʾʼ¨]/g

export const foldText = (text) =>
  (text || '').normalize('NFD').replace(/[̀-ͯ]/g, '')
    .replace(APOSTROPHES, '').toLowerCase()
