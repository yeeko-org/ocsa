import dayjs from 'dayjs'

export function useDates() {
  const months_of_year = [
    { name: 'Enero', short_name: 'Ene' },
    { name: 'Febrero', short_name: 'Feb' },
    { name: 'Marzo', short_name: 'Mar' },
    { name: 'Abril', short_name: 'Abr' },
    { name: 'Mayo', short_name: 'May' },
    { name: 'Junio', short_name: 'Jun' },
    { name: 'Julio', short_name: 'Jul' },
    { name: 'Agosto', short_name: 'Ago' },
    { name: 'Septiembre', short_name: 'Sep' },
    { name: 'Octubre', short_name: 'Oct' },
    { name: 'Noviembre', short_name: 'Nov' },
    { name: 'Diciembre', short_name: 'Dic' },
  ]

  return {
    months_of_year,
  }
}