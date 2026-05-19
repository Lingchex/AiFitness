"use strict";
const common_vendor = require("../../common/vendor.js");
const _sfc_main = {
  __name: "user",
  setup(__props) {
    const goToPage = (url) => {
      if (!url)
        return;
      common_vendor.index.navigateTo({ url });
    };
    return (_ctx, _cache) => {
      return {
        a: common_vendor.o(($event) => goToPage("/pages/user/body-data"), "32"),
        b: common_vendor.o(($event) => goToPage("/pages/user/favorites"), "9e"),
        c: common_vendor.o(($event) => goToPage("/pages/user/repository"), "0b"),
        d: common_vendor.o(($event) => goToPage("/pages/user/settings"), "4a")
      };
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-0f7520f0"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/pages/user/user.js.map
