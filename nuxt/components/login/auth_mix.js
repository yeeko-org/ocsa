
let authMixin = {
  rules: {
    user_name: (v) =>  !!v || 'Es necesario agregar tu nombre',
    full_name: (v) =>  !!v || 'Es necesario agregar un correo',
    password: (v) => !!v || 'Es necesario agregar tu contraseña',
    required: (value) => !!value || 'Valor Requerido.',
    min: (value) => (!!value ? value.length >= 8 : false) || 'Mínimo 8 caracteres',
    min_year: (value) =>{
      console.log("value", value)
      return (!!value ? (Number(value) >= 1900) : false) || 'El año debe ser mayor a 1900'
    },
    max_year: (value) =>
      (!!value ? (Number(value) <= new Date().getFullYear()) : false)
      || 'Año inválido',
    email: (value) => {
      const pattern = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}.\[0-9]{1,3}.\[0-9]{1,3}.\[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
      return pattern.test(value) || 'Escribe un correo válido'
    }
  }
}




export default authMixin
