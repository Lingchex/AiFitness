"use strict";
const common_vendor = require("../../common/vendor.js");
const API_BASE_URL = "https://1bce4b79.r2.cpolar.top";
const _sfc_main = {
  __name: "AnalysisOverlay",
  props: {
    visible: Boolean,
    item: Object
  },
  emits: ["close"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const enter = common_vendor.ref(false);
    const videoPath = common_vendor.ref("");
    const isAnalyzing = common_vendor.ref(false);
    const analysisResult = common_vendor.ref(null);
    const loadingText = common_vendor.ref("AI深度分析中...");
    common_vendor.watch(() => props.visible, (v) => {
      enter.value = v;
      if (v)
        analysisResult.value = null;
    });
    const chooseVideo = (type) => {
      common_vendor.index.chooseVideo({
        sourceType: [type],
        compressed: false,
        maxDuration: 60,
        success: (res) => {
          videoPath.value = res.tempFilePath;
          analysisResult.value = null;
        }
      });
    };
    const removeVideo = () => {
      videoPath.value = "";
      analysisResult.value = null;
    };
    const formattedReport = common_vendor.computed(() => {
      if (!analysisResult.value || !analysisResult.value.report)
        return "";
      let md = analysisResult.value.report;
      let html = md.replace(/\n/g, "<br>").replace(/\*\*(.*?)\*\*/g, "<b>$1</b>");
      return html;
    });
    const submitAnalysis = async () => {
      if (!videoPath.value || isAnalyzing.value)
        return;
      isAnalyzing.value = true;
      analysisResult.value = null;
      loadingText.value = "正在上传视频...";
      common_vendor.index.showLoading({ title: loadingText.value, mask: true });
      const tips = [
        "AI 正在提取关键帧...",
        "正在分析动作轨迹...",
        "正在评估发力路径...",
        "正在生成评估报告...",
        "分析需要一点时间，请耐心等待..."
      ];
      let tipIndex = 0;
      const tipTimer = setInterval(() => {
        if (isAnalyzing.value) {
          loadingText.value = tips[tipIndex % tips.length];
          common_vendor.index.showLoading({ title: loadingText.value, mask: true });
          tipIndex++;
        } else {
          clearInterval(tipTimer);
        }
      }, 4e3);
      try {
        const uploadRes = await new Promise((resolve, reject) => {
          common_vendor.index.uploadFile({
            url: `${API_BASE_URL}/api/analyze`,
            filePath: videoPath.value,
            name: "file",
            // 对应后端 request.files['file']
            formData: {
              "exercise_type": props.item.name || "自动识别",
              // 把当前动作名传给后端
              "max_frames": "8",
              "frame_strategy": "adaptive"
            },
            // ⭐ 核心：将超时时间延长到 120 秒 (120000ms)，防止大模型分析超时中断
            timeout: 24e4,
            success: (res) => {
              if (res.statusCode === 200) {
                try {
                  resolve(JSON.parse(res.data));
                } catch (e) {
                  reject(new Error("返回数据解析失败"));
                }
              } else {
                try {
                  const errData = JSON.parse(res.data);
                  reject(new Error(errData.msg || "请求失败"));
                } catch (e) {
                  reject(new Error(`服务器错误: ${res.statusCode}`));
                }
              }
            },
            fail: (err) => {
              if (err.errMsg && err.errMsg.includes("timeout")) {
                reject(new Error("请求超时，AI分析时间过长，请稍后重试"));
              } else {
                reject(new Error("网络请求失败，请检查IP和后端服务"));
              }
            }
          });
        });
        if (uploadRes.code === 200) {
          analysisResult.value = uploadRes.data;
          common_vendor.index.showToast({ title: "分析完成", icon: "success" });
        } else {
          throw new Error(uploadRes.msg || "分析失败");
        }
      } catch (error) {
        common_vendor.index.__f__("error", "at components/planing/AnalysisOverlay.vue:245", "分析出错:", error);
        common_vendor.index.showModal({
          title: "分析失败",
          content: error.message || "未知错误",
          showCancel: false
        });
      } finally {
        clearInterval(tipTimer);
        isAnalyzing.value = false;
        common_vendor.index.hideLoading();
      }
    };
    return (_ctx, _cache) => {
      return common_vendor.e({
        a: common_vendor.o(($event) => _ctx.$emit("close"), "3c"),
        b: common_vendor.t(__props.item.typeLabel),
        c: common_vendor.n(__props.item.type),
        d: common_vendor.t(__props.item.name),
        e: common_vendor.t(__props.item.sets),
        f: common_vendor.t(__props.item.reps),
        g: common_vendor.t(__props.item.rest),
        h: !videoPath.value
      }, !videoPath.value ? {} : {
        i: videoPath.value,
        j: common_vendor.o(removeVideo, "ba")
      }, {
        k: common_vendor.o(($event) => chooseVideo("camera"), "66"),
        l: common_vendor.o(($event) => chooseVideo("album"), "9a"),
        m: isAnalyzing.value
      }, isAnalyzing.value ? {
        n: common_vendor.t(loadingText.value)
      } : {}, {
        o: videoPath.value && !isAnalyzing.value ? 1 : "",
        p: isAnalyzing.value ? 1 : "",
        q: isAnalyzing.value,
        r: common_vendor.o(submitAnalysis, "92"),
        s: analysisResult.value
      }, analysisResult.value ? {
        t: common_vendor.t(analysisResult.value.video_info.exercise_type_detected_or_given),
        v: common_vendor.t(analysisResult.value.video_info.duration_sec),
        w: common_vendor.t(analysisResult.value.video_info.extracted_frames),
        x: formattedReport.value
      } : {}, {
        y: enter.value ? 1 : "",
        z: common_vendor.o(() => {
        }, "73"),
        A: __props.visible ? 1 : "",
        B: common_vendor.o(($event) => _ctx.$emit("close"), "5e")
      });
    };
  }
};
const Component = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-53b1e711"]]);
wx.createComponent(Component);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/components/planing/AnalysisOverlay.js.map
