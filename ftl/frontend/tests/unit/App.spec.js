/*
 * Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
 * Licensed under the BSL License. See LICENSE in the project root for license information.
 */

import {createLocalVue, shallowMount} from '@vue/test-utils';
import BootstrapVue from "bootstrap-vue";
import App from "../../src/App";
import VueRouter from 'vue-router';

const localVue = createLocalVue();
localVue.use(BootstrapVue); // to avoid warning on tests execution
localVue.use(VueRouter);
localVue.prototype.$t = (text) => {
  return text;
}; // i18n mock
localVue.prototype.tc = (text) => {
  return text;
}; // i18n mock
localVue.prototype.$moment = () => {
  return {fromNow: jest.fn()}
};
localVue.mixin({methods: {mixinAlert: jest.fn()}}); // mixin alert


const mockedChangeFolder = jest.fn();


describe('App template', () => {
  const wrapper = shallowMount(App, {
    localVue,
    methods: {changeFolder: mockedChangeFolder} // mock changeFolder as it is called by mounted
  });

  it('renders properly app template', () => {
    const appSelector= '#app';
    const elem = wrapper.find(appSelector);

    expect(elem.is(appSelector)).toBe(true);
  });
});
