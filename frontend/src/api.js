import axios from 'axios';

const API = axios.create({
    baseURL: window.location.hostname === 'localhost'
        ? 'http://127.0.0.1:8000'
        : 'https://bierdeckel.onrender.com'
});

export default API;