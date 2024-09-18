import axios from "axios";

export default axios.create({
  //baseURL: process.env.apiURL,
  baseURL: process.env.NODE_ENV === 'development'
  	? 'http://localhost:8000/api'
  	//? 'https://ocamis.ngrok.io/api'
    // ? 'https://arropa.yeeko.org/api'
    : 'https://apiocsa.yeeko.org/api',
  headers: {
    "Content-Type": "application/json"
    //"Authorization": "Token 1b38bcac3c4f57a1b57bf48a954111bd54a3f3cf"
  }
});
