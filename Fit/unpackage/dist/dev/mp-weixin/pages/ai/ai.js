"use strict";
const common_vendor = require("../../common/vendor.js");
const API_BASE = "http://46a8871a.r2.cpolar.top";
const USE_STREAM = false;
const STORAGE_KEY = "ai_trainer_chat_history";
const _sfc_main = {
  __name: "ai",
  setup(__props) {
    const messages = common_vendor.ref([]);
    const inputText = common_vendor.ref("");
    const sending = common_vendor.ref(false);
    const loading = common_vendor.ref(true);
    const scrollToId = common_vendor.ref("");
    const useRAG = common_vendor.ref(true);
    let scrollTimer = null;
    function scrollToBottom() {
      common_vendor.nextTick$1(() => {
        scrollToId.value = "";
        setTimeout(() => {
          scrollToId.value = "msg-bottom";
        }, 50);
      });
    }
    function throttledScrollToBottom() {
      if (scrollTimer)
        return;
      scrollToBottom();
      scrollTimer = setTimeout(() => {
        scrollTimer = null;
      }, 200);
    }
    function loadHistory() {
      try {
        const raw = common_vendor.index.getStorageSync(STORAGE_KEY);
        if (raw) {
          const arr = typeof raw === "string" ? JSON.parse(raw) : raw;
          if (Array.isArray(arr)) {
            if (messages.value.length === 0) {
              messages.value = arr.slice(-300);
            }
            return arr;
          }
        }
      } catch (e) {
        common_vendor.index.__f__("warn", "at pages/ai/ai.vue:152", "读取历史失败", e);
      }
      return [];
    }
    function saveHistory(arr) {
      try {
        common_vendor.index.setStorageSync(STORAGE_KEY, JSON.stringify(arr.slice(-300)));
      } catch (e) {
        common_vendor.index.__f__("warn", "at pages/ai/ai.vue:161", "保存历史失败", e);
      }
    }
    function toggleRAG() {
      if (sending.value)
        return;
      useRAG.value = !useRAG.value;
      common_vendor.index.showToast({
        title: useRAG.value ? "已切换至文档库模式" : "已切换至自由对话模式",
        icon: "none",
        duration: 1500
      });
    }
    function handleClear() {
      if (sending.value)
        return;
      common_vendor.index.showModal({
        title: "清除对话",
        content: "确定要开启一段新的健身对话吗？",
        confirmText: "确定",
        confirmColor: "#0D0D0D",
        success(res) {
          if (res.confirm) {
            try {
              common_vendor.index.removeStorageSync(STORAGE_KEY);
            } catch (e) {
            }
            messages.value = [];
            common_vendor.index.showToast({ title: "已开启新对话", icon: "none", duration: 1500 });
          }
        }
      });
    }
    async function handleSend() {
      const text = (inputText.value || "").trim();
      if (!text || sending.value)
        return;
      inputText.value = "";
      sending.value = true;
      const userMsg = { role: "user", content: text };
      messages.value.push(userMsg);
      scrollToBottom();
      const aiMsg = { role: "assistant", content: "", rag: useRAG.value };
      messages.value.push(aiMsg);
      scrollToBottom();
      const currentHistory = loadHistory();
      const newHistory = [...currentHistory, userMsg];
      try {
        if (USE_STREAM)
          ;
        else {
          await fetchNormal(text, aiMsg, newHistory);
        }
      } catch (err) {
        common_vendor.index.__f__("error", "at pages/ai/ai.vue:220", err);
        if (!aiMsg.content) {
          aiMsg.content = "请求失败，请稍后再试";
        }
      } finally {
        sending.value = false;
        scrollToBottom();
      }
    }
    function fetchNormal(question, aiMsg, newHistory) {
      return new Promise((resolve, reject) => {
        const endpoint = useRAG.value ? "/api/v1/chat" : "/api/v1/chat/plain";
        common_vendor.index.request({
          url: `${API_BASE}${endpoint}`,
          method: "POST",
          header: { "Content-Type": "application/json" },
          data: { question },
          success: (res) => {
            var _a;
            try {
              const obj = typeof res.data === "string" ? JSON.parse(res.data) : res.data || {};
              const answer = ((_a = obj == null ? void 0 : obj.data) == null ? void 0 : _a.answer) || (obj == null ? void 0 : obj.answer) || JSON.stringify(obj);
              aiMsg.content = answer;
              newHistory.push({ role: "assistant", content: answer });
              saveHistory(newHistory);
              resolve();
            } catch (e) {
              aiMsg.content = "解析返回结果失败";
              reject(e);
            }
          },
          fail: (err) => {
            aiMsg.content = "网络异常，请检查网络或接口地址";
            reject(err);
          }
        });
      });
    }
    function decodeChunk(buffer) {
      if (!buffer)
        return "";
      try {
        const uint8 = new Uint8Array(buffer);
        let str = "";
        for (let i = 0; i < uint8.length; i++) {
          str += String.fromCharCode(uint8[i]);
        }
        return str;
      } catch (e) {
        return "";
      }
    }
    function parseSSELines(text, aiMsg) {
      const lines = text.split("\n");
      let temp = "";
      const processTemp = () => {
        if (temp.startsWith("data:")) {
          const jsonStr = temp.replace(/^data:\s*/, "");
          if (jsonStr.trim() === "[DONE]")
            return;
          try {
            const obj = JSON.parse(jsonStr);
            const answer = (obj == null ? void 0 : obj.answer) || "";
            if (answer) {
              aiMsg.content += answer;
            }
          } catch (e) {
            if (jsonStr) {
              aiMsg.content += jsonStr;
            }
          }
        }
        temp = "";
      };
      lines.forEach((line) => {
        if (!line.trim()) {
          processTemp();
          return;
        }
        temp += (temp ? "\n" : "") + line;
      });
      processTemp();
    }
    function fetchStream(question, aiMsg, newHistory) {
      return new Promise((resolve, reject) => {
        const endpoint = useRAG.value ? "/api/v1/chat/stream" : "/api/v1/chat/plain/stream";
        const requestTask = common_vendor.index.request({
          url: `${API_BASE}${endpoint}`,
          method: "POST",
          header: {
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
          },
          data: { question },
          enableChunked: true,
          responseType: "arraybuffer",
          success: () => {
          },
          fail: (err) => {
            aiMsg.content = aiMsg.content || "网络异常，请检查网络";
            reject(err);
          }
        });
        requestTask.onChunkReceived((res) => {
          try {
            const text = decodeChunk(res.data) || "";
            parseSSELines(text, aiMsg);
            throttledScrollToBottom();
          } catch (e) {
            common_vendor.index.__f__("warn", "at pages/ai/ai.vue:338", "解析流式数据异常", e);
          }
        });
        const originSuccess = requestTask.success;
        requestTask.success = (res) => {
          try {
            originSuccess == null ? void 0 : originSuccess(res);
          } catch (_) {
          }
          newHistory.push({ role: "assistant", content: aiMsg.content });
          saveHistory(newHistory);
          resolve();
        };
        setTimeout(() => {
          try {
            requestTask.abort();
          } catch (_) {
          }
          if (!aiMsg.content) {
            aiMsg.content = "响应超时，请重试";
            reject(new Error("timeout"));
          }
        }, 6e4);
      });
    }
    common_vendor.onMounted(() => {
      loadHistory();
      loading.value = false;
      setTimeout(() => {
        scrollToBottom();
      }, 300);
    });
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: !loading.value && messages.value.length === 0
      }, !loading.value && messages.value.length === 0 ? {
        b: common_vendor.t(useRAG.value ? "基于专属文档提供指导" : "自由拓展解答")
      } : {}, {
        c: common_vendor.f(messages.value, (msg, idx, i0) => {
          return common_vendor.e({
            a: msg.role === "assistant"
          }, msg.role === "assistant" ? common_vendor.e({
            b: common_vendor.t(msg.content || "思考中..."),
            c: msg.content
          }, msg.content ? {
            d: common_vendor.t(msg.rag ? "📚 RAG 检索" : "⚡️ 自由回复")
          } : {}) : {}, {
            e: msg.role === "user"
          }, msg.role === "user" ? {
            f: common_vendor.t(msg.content)
          } : {}, {
            g: idx,
            h: common_vendor.n(msg.role === "user" ? "row-user" : "row-ai")
          });
        }),
        d: scrollToId.value,
        e: common_vendor.t(useRAG.value ? "📚" : "⚡️"),
        f: common_vendor.t(useRAG.value ? "文档库" : "自由对话"),
        g: useRAG.value ? 1 : "",
        h: common_vendor.o(toggleRAG, "59"),
        i: common_vendor.o(handleClear, "58"),
        j: sending.value,
        k: common_vendor.o(handleSend, "6a"),
        l: inputText.value,
        m: common_vendor.o(($event) => inputText.value = $event.detail.value, "9e"),
        n: !sending.value
      }, !sending.value ? {} : {}, {
        o: inputText.value.trim() && !sending.value ? 1 : "",
        p: common_vendor.o(handleSend, "a5")
      });
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-fdb58938"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/pages/ai/ai.js.map
