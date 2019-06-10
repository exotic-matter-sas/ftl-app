import Vue from 'vue';
import BootstrapVue from 'bootstrap-vue';
import App from './App.vue';

import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue/dist/bootstrap-vue.css';
import {mixinAlert} from "./vueMixins";
import router from './router'

Vue.config.productionTip = false;

Vue.use(BootstrapVue);

Vue.prototype.$_ = function (text, vars = null) {
  var translated_text;

  if (vars === null) {
    if (typeof gettext === 'function') {
      translated_text = gettext(text);
    }
  } else {
    if (typeof interpolate === 'function') {
      if (Array.isArray(vars)) {
        translated_text = interpolate(text, vars);
      } else {
        translated_text = interpolate(text, vars, true);
      }
    }
  }

  return translated_text || text;
};

// Defined mixins
Vue.mixin({
  methods: {
    mixinAlert
  }
});

new Vue({
  router,
  render: h => h(App)
}).$mount('#app');
