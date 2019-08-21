import {createLocalVue, shallowMount, mount} from '@vue/test-utils';

import axios from 'axios';
import BootstrapVue from "bootstrap-vue";
import flushPromises from "flush-promises"; // needed for async tests

import * as tv from './../tools/testValues.js'
import {axiosConfig} from "../../src/constants";

import ManageFolders from "../../src/views/ManageFolders";
import FTLDeleteFolder from "../../src/components/FTLDeleteFolder";
import FTLRenameFolder from "../../src/components/FTLRenameFolder";
import FTLSelectableFolder from "../../src/components/FTLSelectableFolder";
import FTLNewFolder from "../../src/components/FTLNewFolder";
import FTLMoveFolder from "../../src/components/FTLMoveFolder";

const localVue = createLocalVue();

localVue.use(BootstrapVue); // avoid bootstrap vue warnings
localVue.component('font-awesome-icon', jest.fn()); // avoid font awesome warnings

localVue.prototype.$_ = (text, args='') => {return text + args};// i18n mock
localVue.prototype.$moment = () => {return {fromNow: jest.fn()}}; // moment mock
const mockedRouterPush = jest.fn();
localVue.prototype.$router = {push: mockedRouterPush}; // router mock
const mockedMixinAlert = jest.fn();
localVue.mixin({methods: {mixinAlert: mockedMixinAlert}}); // mixinAlert mock

// mock calls to api requests
jest.mock('axios', () => ({
  get: jest.fn(),
}));

// TODO store mocked response for tested api request here
const mockedGetFoldersListResponse = {
  data: [tv.FOLDER_PROPS, tv.FOLDER_PROPS_VARIANT],
  status: 200,
  config: axiosConfig
};
const mockedGetFolderDetailsResponse = {
  data: {paths: 'fakePath'},
  status: 200,
  config: axiosConfig
};

const mockedRefreshFolder = jest.fn();
const mockedGetFolderDetail = jest.fn();
const mockedUnselectFolder = jest.fn();
const mockedNavigateToFolder = jest.fn();
const mockedUpdateFolders = jest.fn();
const mockedUpdateFoldersFromUrl = jest.fn();
const mockedBreadcrumb = jest.fn();
const mockedGetCurrentFolder = jest.fn();


const mountedMocks = {
  updateFolders: mockedUpdateFolders,
  updateFoldersFromUrl: mockedUpdateFoldersFromUrl,
};

const folder = tv.FOLDER_PROPS;

describe('ManageFolders template', () => {
  let wrapper;
  // defined const specific to this describe here
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(ManageFolders, {
      localVue,
      methods: mountedMocks,
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('renders properly component template', () => {
    const elementSelector= '#folders-mngt';
    const elem = wrapper.find(elementSelector);

    expect(elem.is(elementSelector)).toBe(true);

    expect(wrapper.text()).toContain('No folder selected');
  });
});

describe('ManageFolders mounted call proper methods', () => {
  let wrapper;

  it('mounted without props call proper methods', () => {
    jest.clearAllMocks();
    //when mounted with folder props
    wrapper = shallowMount(ManageFolders, {
      localVue,
      methods: {
        updateFolders : mockedUpdateFolders
      }
    });

    //then
    expect(mockedUpdateFolders).toHaveBeenCalledTimes(1);
  });

  it('mounted with folder props call proper methods', () => {
    jest.clearAllMocks();
    //when mounted with folder props
    wrapper = shallowMount(ManageFolders, {
      localVue,
      propsData: { folder },
      methods: {
        updateFoldersFromUrl : mockedUpdateFoldersFromUrl
      }
    });

    //then
    expect(mockedUpdateFoldersFromUrl).toHaveBeenCalledTimes(1);
    expect(mockedUpdateFoldersFromUrl).toHaveBeenCalledWith(folder);
  });
});

describe('ManageFolders computed', () => {
  let wrapper;
  // defined const specific to this describe here
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(ManageFolders, {
      localVue,
      methods: mountedMocks,
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('getCurrentFolder return proper format', () => {
    // when previousLevels empty
    const testedReturn = wrapper.vm.getCurrentFolder;

    //then
    expect(testedReturn).toBe(null);
  });
  it('getCurrentFolder return proper format whe previousLevels set', () => {
    // when previousLevels set
    wrapper.setData({previousLevels: [tv.FOLDER_PROPS, tv.FOLDER_PROPS_VARIANT]});
    const testedReturn = wrapper.vm.getCurrentFolder;

    //then
    expect(testedReturn).toBe(tv.FOLDER_PROPS_VARIANT);
  });
  it('breadcrumb return proper format', () => {
    // when previousLevels set
    wrapper.setData({previousLevels: [tv.FOLDER_PROPS, tv.FOLDER_PROPS_VARIANT]});
    const testedReturn = wrapper.vm.breadcrumb;

    //then
    expect(testedReturn).toEqual([
      {text: 'Root', to: {name: 'folders'}},
      {text: tv.FOLDER_PROPS.name, to: {name: 'folders', params: {folder: tv.FOLDER_PROPS.id}}},
      {text: tv.FOLDER_PROPS_VARIANT.name, to: {name: 'folders', params: {folder: tv.FOLDER_PROPS_VARIANT.id}}},
    ]);
  });
});

describe('ManageFolders watcher call proper methods', () => {
  let wrapper;
  // defined const specific to this describe here
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(ManageFolders, {
      localVue,
      methods: mountedMocks,
      propsData: {}
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('folder watcher call proper methods', () => {
    const newFolder = tv.FOLDER_PROPS_VARIANT;
    //when a new folder is set
    wrapper.setData({folder: newFolder});

    //then
    expect(mockedUpdateFoldersFromUrl).toHaveBeenCalledTimes(1);
    expect(mockedUpdateFoldersFromUrl).toHaveBeenCalledWith(newFolder);

    //when the same folder is set
    wrapper.setData({folder: newFolder, previousLevels: [tv.FOLDER_PROPS_VARIANT]});

    //then nothing new happens
    expect(mockedUpdateFoldersFromUrl).toHaveBeenCalledTimes(1);

    //when the folder is undefined
    wrapper.setData({folder: undefined});

    //then
    expect(wrapper.vm.previousLevels).toEqual([]);
    expect(mockedUpdateFolders).toHaveBeenCalledTimes(1);
  });
});

describe('ManageFolders methods', () => {
  let wrapper;
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(ManageFolders, {
      localVue,
      methods: Object.assign(
        {
          unselectFolder: mockedUnselectFolder,
          refreshFolder: mockedRefreshFolder,
          navigateToFolder: mockedNavigateToFolder,
        },
        mountedMocks
      ),
      propsData: { folder },
      computed: {
        breadcrumb: mockedBreadcrumb,
        getCurrentFolder: mockedGetCurrentFolder
      }
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('refreshFolder call proper methods', () => {
    // restore original method to test it
    wrapper.setMethods({refreshFolder: ManageFolders.methods.refreshFolder});

    //when called with folder props
    wrapper.vm.refreshFolder();

    //then
    expect(mockedUnselectFolder).toHaveBeenCalledTimes(1);
    expect(mockedUpdateFolders).not.toHaveBeenCalled();
    expect(mockedUpdateFoldersFromUrl).toHaveBeenCalledWith(folder);

    //when called without folder props
    jest.clearAllMocks();
    wrapper.setData({folder: undefined});
    wrapper.vm.refreshFolder();

    //then
    expect(mockedUnselectFolder).toHaveBeenCalledTimes(1);
    expect(mockedUpdateFolders).toHaveBeenCalledTimes(1 + 1); //+1 for the call inside watch folder which isn't mockable
    expect(mockedUpdateFoldersFromUrl).not.toHaveBeenCalled();
  });
  it('unselectFolder update data', () => {
    // restore original method to test it
    wrapper.setMethods({unselectFolder: ManageFolders.methods.unselectFolder});

    //when
    wrapper.setData({folderDetail: tv.FOLDER_PROPS});
    wrapper.vm.unselectFolder();

    //then
    expect(wrapper.vm.folderDetail).toBe(null);
  });
  it('navigateToFolder push data to router', () => {
    wrapper.setData({ previousLevels: [tv.FOLDER_PROPS] });
    // restore original method to test it
    wrapper.setMethods({navigateToFolder: ManageFolders.methods.navigateToFolder});

    //when
    wrapper.vm.navigateToFolder(tv.FOLDER_PROPS_VARIANT);

    //then
    expect(wrapper.vm.previousLevels).toEqual([tv.FOLDER_PROPS, tv.FOLDER_PROPS_VARIANT]);
    expect(mockedRouterPush).toHaveBeenCalledTimes(1);
    expect(mockedRouterPush).toHaveBeenCalledWith({name: 'folders', params: {folder: tv.FOLDER_PROPS_VARIANT.id}});
  });
  it('updateFoldersFromUrl call propers methods', async () => {
    // restore original method to test it
    wrapper.setMethods({updateFoldersFromUrl: ManageFolders.methods.updateFoldersFromUrl});
    axios.get.mockResolvedValueOnce(mockedGetFolderDetailsResponse);
    //when
    wrapper.vm.updateFoldersFromUrl(tv.FOLDER_PROPS.id);
    await flushPromises();

    //then
    expect(wrapper.vm.previousLevels).toBe(mockedGetFolderDetailsResponse.data.paths);
    expect(mockedUpdateFolders).toHaveBeenCalledTimes(1);
    expect(mockedUpdateFolders).toHaveBeenCalledWith(mockedGetFolderDetailsResponse.data);
  });
});

describe('ManageFolders methods call api', () => {
  let wrapper;
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(ManageFolders, {
      localVue,
      methods: Object.assign(
        {
          unselectFolder: mockedUnselectFolder,
          refreshFolder: mockedRefreshFolder,
          navigateToFolder: mockedNavigateToFolder,
        },
        mountedMocks
      ),
      propsData: { folder },
      computed: {
        breadcrumb: mockedBreadcrumb,
        getCurrentFolder: mockedGetCurrentFolder
      },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('getFolderDetail call api', async () => {
    axios.get.mockResolvedValue(mockedGetFolderDetailsResponse);

    // when
    wrapper.vm.getFolderDetail(folder);
    await flushPromises();

    // then
    expect(axios.get).toHaveBeenCalledWith("/app/api/v1/folders/" + folder.id);
    expect(axios.get).toHaveBeenCalledTimes(1);
  });
  it('updateFolders call api', async () => {
    // restore original method to test it
    wrapper.setMethods({updateFolders: ManageFolders.methods.updateFolders});
    axios.get.mockResolvedValue(mockedGetFoldersListResponse);

    // when
    wrapper.vm.updateFolders();
    await flushPromises();

    // then
    expect(axios.get).toHaveBeenCalledWith('/app/api/v1/folders');
    expect(axios.get).toHaveBeenCalledTimes(1);

    // when called with folder arg
    jest.clearAllMocks();
    wrapper.vm.updateFolders(folder);
    await flushPromises();

    // then
    expect(axios.get).toHaveBeenCalledWith('/app/api/v1/folders?level=' + folder.id);
    expect(axios.get).toHaveBeenCalledTimes(1);
  });
  it('updateFoldersFromUrl call api', async () => {
    axios.get.mockResolvedValue(mockedGetFolderDetailsResponse);
    wrapper.setMethods({updateFoldersFromUrl: ManageFolders.methods.updateFoldersFromUrl});

    // when folder in url is already the one selected
    wrapper.setData({ folderDetail: folder });
    wrapper.vm.updateFoldersFromUrl(folder.id);
    await flushPromises();

    // then no API call is made
    expect(axios.get).not.toHaveBeenCalled();

    // when folder in url is already the one selected
    wrapper.vm.updateFoldersFromUrl(tv.FOLDER_PROPS_VARIANT.id);
    await flushPromises();

    // then no API call is made
    expect(axios.get).toHaveBeenCalledTimes(1);
    expect(axios.get).toHaveBeenCalledWith('/app/api/v1/folders/' + tv.FOLDER_PROPS_VARIANT.id);
  });
});

describe('ManageFolders methods error handling', () => {
  let wrapper;
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(ManageFolders, {
      localVue,
      methods: Object.assign(
        {
          unselectFolder: mockedUnselectFolder,
          refreshFolder: mockedRefreshFolder,
          navigateToFolder: mockedNavigateToFolder,
        },
        mountedMocks
      ),
      propsData: { folder },
      computed: {
        breadcrumb: mockedBreadcrumb,
        getCurrentFolder: mockedGetCurrentFolder
      },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('getFolderDetail call mixinAlert in case of error', async () => {
    // force an error
    axios.get.mockRejectedValue('fakeError');

    // when
    wrapper.vm.getFolderDetail(folder);
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(mockedMixinAlert).toHaveBeenCalledTimes(1);
    expect(mockedMixinAlert.mock.calls[0][0]).toContain('folder details');
  });
  it('updateFolders call mixinAlert in case of error', async () => {
    // restore original method to test it
    wrapper.setMethods({updateFolders: ManageFolders.methods.updateFolders});
    // force an error
    axios.get.mockRejectedValue('fakeError');

    // when
    wrapper.vm.updateFolders();
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(mockedMixinAlert).toHaveBeenCalledTimes(1);
    expect(mockedMixinAlert.mock.calls[0][0]).toContain('refresh folders');
  });
  it('updateFoldersFromUrl call mixinAlert in case of error', async () => {
    // restore original method to test it
    wrapper.setMethods({updateFoldersFromUrl: ManageFolders.methods.updateFoldersFromUrl});
    // force an error
    axios.get.mockRejectedValue('fakeError');

    // when
    wrapper.vm.updateFoldersFromUrl();
    await flushPromises();

    // then mixinAlert is called with proper message
    expect(mockedMixinAlert).toHaveBeenCalledTimes(1);
    expect(mockedMixinAlert.mock.calls[0][0]).toContain('open this folder');
  });
});

describe('Event received and handled by component', () => {
  let wrapper;
  beforeEach(() => {
    // set mocked component methods return value before shallowMount
    wrapper = shallowMount(ManageFolders, {
      localVue,
      methods: Object.assign(
        {
          unselectFolder: mockedUnselectFolder,
          refreshFolder: mockedRefreshFolder,
          navigateToFolder: mockedNavigateToFolder,
          getFolderDetail: mockedGetFolderDetail,
        },
        mountedMocks
      ),
      propsData: { folder },
      computed: {
        breadcrumb: mockedBreadcrumb,
        getCurrentFolder: mockedGetCurrentFolder
      },
    });
    jest.clearAllMocks(); // Reset mock call count done by mounted
  });

  it('event-navigate-folder call navigateToFolder', async () => {
    // Need to defined some folders for FTLSelectableFolder to appears
    wrapper.setData({ folders: mockedGetFoldersListResponse.data });

    // when
    wrapper.find(FTLSelectableFolder).vm.$emit('event-navigate-folder', folder);
    await flushPromises();

    // then
    expect(mockedNavigateToFolder).toHaveBeenCalledTimes(1);
    expect(mockedNavigateToFolder).toHaveBeenCalledWith(folder);
  });
  it('event-select-folder call getFolderDetail', async () => {
    // Need to defined some folders for FTLSelectableFolder to appears
    wrapper.setData({ folders: mockedGetFoldersListResponse.data });

    // when
    wrapper.find(FTLSelectableFolder).vm.$emit('event-select-folder', folder);
    await flushPromises();

    // then
    expect(mockedGetFolderDetail).toHaveBeenCalledTimes(1);
    expect(mockedGetFolderDetail).toHaveBeenCalledWith(folder);
  });
  it('event-unselect-folder call unselectFolder', async () => {
    // Need to defined some folders for FTLSelectableFolder to appears
    wrapper.setData({ folders: mockedGetFoldersListResponse.data });

    // when
    wrapper.find(FTLSelectableFolder).vm.$emit('event-unselect-folder', folder);
    await flushPromises();

    // then
    expect(mockedUnselectFolder).toHaveBeenCalledTimes(1);
  });
  it('event-folder-renamed call refreshFolder', async () => {
    // Need to defined folderDetail for FTLRenameFolder to appears
    wrapper.setData({ folderDetail: folder });

    // when
    wrapper.find(FTLRenameFolder).vm.$emit('event-folder-renamed', folder);
    await flushPromises();

    // then
    expect(mockedRefreshFolder).toHaveBeenCalledTimes(1);
    expect(mockedRefreshFolder).toHaveBeenCalledWith(folder);
  });
  it('event-folder-created call refreshFolder', async () => {
    // when
    wrapper.find(FTLNewFolder).vm.$emit('event-folder-created', folder);
    await flushPromises();

    // then
    expect(mockedRefreshFolder).toHaveBeenCalledTimes(1);
    expect(mockedRefreshFolder).toHaveBeenCalledWith(folder);
  });
  it('event-folder-deleted call refreshFolder', async () => {
    // Need to defined folderDetail for FTLRenameFolder to appears
    wrapper.setData({ folderDetail: folder });

    // when
    wrapper.find(FTLDeleteFolder).vm.$emit('event-folder-deleted', folder);

    // then
    expect(mockedRefreshFolder).toHaveBeenCalledTimes(1);
    expect(mockedRefreshFolder).toHaveBeenCalledWith(folder);
  });
  it('event-folder-moved call refreshFolder', async () => {
    // Need to defined folderDetail for FTLRenameFolder to appears
    wrapper.setData({ folderDetail: folder });

    // when
    wrapper.find(FTLMoveFolder).vm.$emit('event-folder-moved', folder);

    // then
    expect(mockedRefreshFolder).toHaveBeenCalledTimes(1);
    expect(mockedRefreshFolder).toHaveBeenCalledWith(folder);
  });
});