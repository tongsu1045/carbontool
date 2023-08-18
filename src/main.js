// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue';
import VueRouter from 'vue-router';
import App from './App';
//import TestApp from './TestApp';
import router from './router';
import axios from 'axios';
//import '@/config/api';
//import Axios from '@/config/axios.js';
import ViewUI from 'view-design';
import 'view-design/dist/styles/iview.css';
import echarts from 'echarts';

axios.defaults.baseURL = 'http://localhost:5000';
Vue.prototype.$axios = axios; //以后在使用的时候，可以直接使用 $axios 关键字直接发起get或者post请求

Vue.config.productionTip = false
Vue.prototype.$echarts = echarts //$echarts就可以，少了$就不行

Vue.use(ViewUI);

new Vue({
    el: '#app',
    router,
    render: h => h(App)
});

/*
new Vue({
    el: '#app',
    router,
    render: h => h(TestApp)
});
*/
