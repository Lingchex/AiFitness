"use strict";
const common_vendor = require("../../common/vendor.js");
const _sfc_main = {
  __name: "repository",
  setup(__props) {
    const activeTab = common_vendor.ref(0);
    const searchQuery = common_vendor.ref("");
    const books = common_vendor.ref([
      {
        title: "肌肉增长解剖学",
        size: "12.5 MB",
        pages: 186,
        type: "official",
        fileType: "PDF",
        emoji: "💪",
        gradient: "linear-gradient(145deg, #667eea 0%, #764ba2 100%)"
      },
      {
        title: "营养膳食进阶指南",
        size: "8.2 MB",
        pages: 124,
        type: "official",
        fileType: "PDF",
        emoji: "🥗",
        gradient: "linear-gradient(145deg, #f093fb 0%, #f5576c 100%)"
      },
      {
        title: "心率与有氧训练",
        size: "15.1 MB",
        pages: 210,
        type: "official",
        fileType: "PDF",
        emoji: "❤️‍🔥",
        gradient: "linear-gradient(145deg, #4facfe 0%, #00f2fe 100%)"
      },
      {
        title: "2024深蹲力量训练记录",
        size: "2.4 MB",
        pages: 32,
        type: "user",
        fileType: "PDF",
        emoji: "🏋️",
        gradient: "linear-gradient(145deg, #a8edea 0%, #fed6e3 100%)"
      },
      {
        title: "拉伸恢复完全手册",
        size: "6.7 MB",
        pages: 98,
        type: "official",
        fileType: "EPUB",
        emoji: "🧘",
        gradient: "linear-gradient(145deg, #ffecd2 0%, #fcb69f 100%)"
      },
      {
        title: "训练日志模板V2.0",
        size: "1.1 MB",
        pages: 16,
        type: "user",
        fileType: "DOCX",
        emoji: "📝",
        gradient: "linear-gradient(145deg, #89f7fe 0%, #66a6ff 100%)"
      }
    ]);
    const tabs = common_vendor.computed(() => [
      { label: "全部", count: books.value.length },
      { label: "公共库", count: books.value.filter((b) => b.type === "official").length },
      { label: "私有库", count: books.value.filter((b) => b.type === "user").length }
    ]);
    const displayBooks = common_vendor.computed(() => {
      let list = books.value;
      if (activeTab.value === 1)
        list = list.filter((b) => b.type === "official");
      if (activeTab.value === 2)
        list = list.filter((b) => b.type === "user");
      if (searchQuery.value) {
        list = list.filter((b) => b.title.includes(searchQuery.value));
      }
      return list;
    });
    const handleUpload = () => {
      common_vendor.wx$1.chooseMessageFile({
        count: 1,
        type: "file",
        extension: ["pdf"],
        // 过滤仅 PDF
        success: (res) => {
          const file = res.tempFiles[0];
          if (file.size > 20 * 1024 * 1024) {
            common_vendor.index.showToast({ title: "文件不能超过 20MB", icon: "none" });
            return;
          }
          common_vendor.index.showLoading({ title: "AI 解析入库中...", mask: true });
          common_vendor.index.uploadFile({
            url: "https://你的服务器域名.com/api/v1/documents/upload",
            // 必须是 https
            filePath: file.path,
            name: "file",
            // 必须对应后端接口中的 file: UploadFile 参数名
            header: {
              // 如果有登录态，在这里传 Token
              // 'Authorization': 'Bearer ' + storage.getToken()
            },
            success: (uploadRes) => {
              const data = JSON.parse(uploadRes.data);
              if (data.code === 200) {
                common_vendor.index.showToast({ title: "入库成功", icon: "success" });
                const newDoc = {
                  title: file.name,
                  size: (file.size / 1024 / 1024).toFixed(1) + " MB",
                  pages: data.data.pages || "?",
                  // 后端若返回页数
                  type: "user",
                  fileType: "PDF",
                  emoji: "📄",
                  gradient: "linear-gradient(145deg, #a18cd1 0%, #fbc2eb 100%)"
                };
                books.value.unshift(newDoc);
              } else {
                common_vendor.index.showModal({
                  title: "处理失败",
                  content: data.detail || "解析失败，请重试",
                  showCancel: false
                });
              }
            },
            fail: (err) => {
              common_vendor.index.__f__("error", "at pages/user/repository.vue:217", "上传失败:", err);
              common_vendor.index.showToast({ title: "网络请求失败", icon: "none" });
            },
            complete: () => {
              common_vendor.index.hideLoading();
            }
          });
        },
        fail: (err) => {
          common_vendor.index.__f__("log", "at pages/user/repository.vue:227", "取消选择文件");
        }
      });
    };
    const openBook = (item) => {
      common_vendor.index.showToast({ title: "解析中: " + item.title, icon: "none" });
    };
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: common_vendor.t(books.value.length),
        b: common_vendor.o(handleUpload, "3b"),
        c: searchQuery.value,
        d: common_vendor.o(($event) => searchQuery.value = $event.detail.value, "a3"),
        e: common_vendor.f(tabs.value, (tab, index, i0) => {
          return {
            a: common_vendor.t(tab.label),
            b: common_vendor.t(tab.count),
            c: activeTab.value === index ? 1 : "",
            d: index,
            e: common_vendor.n(activeTab.value === index ? "active" : ""),
            f: common_vendor.o(($event) => activeTab.value = index, index)
          };
        }),
        f: `translateX(${activeTab.value * 100}%)`,
        g: common_vendor.f(displayBooks.value, (item, index, i0) => {
          return {
            a: common_vendor.f(5, (n, k1, i1) => {
              return {
                a: n
              };
            }),
            b: common_vendor.t(item.emoji),
            c: common_vendor.t(item.fileType),
            d: item.gradient,
            e: common_vendor.t(item.title),
            f: common_vendor.t(item.size),
            g: common_vendor.t(item.pages),
            h: common_vendor.t(item.type === "official" ? "系统" : "私有"),
            i: common_vendor.n("source-" + item.type),
            j: index,
            k: common_vendor.o(($event) => openBook(item), index)
          };
        }),
        h: displayBooks.value.length === 0
      }, displayBooks.value.length === 0 ? {} : {});
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-2353aac3"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/pages/user/repository.js.map
