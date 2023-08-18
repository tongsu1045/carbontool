import Vue from 'vue'
import Router from 'vue-router'
import HelloWorld from '@/components/HelloWorld'
import tool from '@/components/tool'
import userguide from '@/components/userguide'
import resource from '@/components/resource'


Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'tool',
      component: tool
    },
    {
      path: '/userguide',
      name: 'userguide',
      component: userguide
    },
    {
      path: '/resource',
      name: 'resource',
      component: resource
    }
  ]
})
