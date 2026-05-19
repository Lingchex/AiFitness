"use strict";
const common_vendor = require("../../common/vendor.js");
if (!Math) {
  AnalysisOverlay();
}
const AnalysisOverlay = () => "../../components/planing/AnalysisOverlay.js";
const _sfc_main = {
  __name: "plan",
  setup(__props) {
    const planList = common_vendor.ref([
      {
        name: "高抬腿热身",
        sets: 3,
        reps: "30",
        rest: 15,
        type: "warmup",
        typeLabel: "热身",
        completed: false,
        muscles: [
          { name: "股四头肌", activation: 85 },
          { name: "髂腰肌", activation: 78 },
          { name: "小腿三头肌", activation: 65 }
        ],
        tips: [
          "挺胸收腹，保持躯干稳定，不要前后晃动",
          "大腿抬至与地面平行，小腿自然下垂",
          "前脚掌着地，落地时膝关节微屈缓冲"
        ],
        mistakes: [
          { wrong: "身体后仰，靠惯性甩腿", right: "核心收紧，躯干保持直立，主动抬腿" },
          { wrong: "全脚掌或脚跟着地", right: "前脚掌着地，利用跟腱弹性缓冲" }
        ],
        advice: "作为热身动作，建议前2组以60%速度进行，最后一组提速至85%最大速度，逐步激活神经系统，为后续高强度训练做好准备。"
      },
      {
        name: "俄罗斯挺身",
        sets: 4,
        reps: "20",
        rest: 30,
        type: "core",
        typeLabel: "核心",
        completed: false,
        muscles: [
          { name: "腹直肌", activation: 72 },
          { name: "腹内外斜肌", activation: 90 },
          { name: "竖脊肌", activation: 55 }
        ],
        tips: [
          "双脚离地或脚跟轻触地面，保持V字坐姿",
          "转体时肩部带动，不要仅转头或用手臂代偿",
          "呼气转体，吸气回正，保持呼吸节奏"
        ],
        mistakes: [
          { wrong: "背部拱起，驼背做动作", right: "挺胸，脊柱保持中立位，想象头顶向上延伸" },
          { wrong: "双手持重甩动借力", right: "控制离心过程，转体匀速，2秒转向2秒回正" }
        ],
        advice: "你当前的核心基础较好，建议尝试在转体末端增加0.5秒的顶峰收缩，能显著提升腹斜肌的刺激深度。若想进阶，可手持2-4kg药球。"
      },
      {
        name: "波比跳",
        sets: 4,
        reps: "15",
        rest: 45,
        type: "hiit",
        typeLabel: "HIIT",
        completed: true,
        muscles: [
          { name: "胸大肌", activation: 68 },
          { name: "股四头肌", activation: 82 },
          { name: "三角肌前束", activation: 60 },
          { name: "臀大肌", activation: 75 }
        ],
        tips: [
          "下蹲时臀部向后，不要膝关节过度前移",
          "俯卧撑阶段身体成一直线，不要塌腰",
          "起跳时充分伸展踝、膝、髋三关节"
        ],
        mistakes: [
          { wrong: "跳过俯卧撑直接起跳", right: "每个波比跳必须包含完整的俯卧撑动作" },
          { wrong: "落地时膝关节内扣", right: "落地时膝盖对准脚尖方向，臀部向后坐缓冲" }
        ],
        advice: "波比跳是本计划中强度最高的动作。建议第1-2组保持标准动作质量，第3-4组若体能下降可适当降低跳起高度，但不要省略俯卧撑环节，保证训练容量。"
      },
      {
        name: "平板支撑",
        sets: 3,
        reps: "60",
        rest: 30,
        type: "core",
        typeLabel: "核心",
        completed: false,
        muscles: [
          { name: "腹横肌", activation: 95 },
          { name: "腹直肌", activation: 70 },
          { name: "竖脊肌", activation: 62 }
        ],
        tips: [
          "肘关节位于肩膀正下方，前臂平贴地面",
          "收紧臀部，不要塌腰也不要撅臀",
          "目光看向双手之间，颈椎保持中立"
        ],
        mistakes: [
          { wrong: "腰部下沉塌腰", right: "想象肚脐向脊柱方向靠近，骨盆后倾" },
          { wrong: "憋气坚持", right: "保持均匀的腹式呼吸，每次吸气3秒呼气3秒" }
        ],
        advice: "60秒的平板支撑对核心耐力要求较高。若中段感到腰部酸痛，说明腹横肌力量不足，建议先拆分为3×30秒，逐步延长单次时间。"
      },
      {
        name: "腹部拉伸",
        sets: 1,
        reps: "1",
        rest: 0,
        type: "stretch",
        typeLabel: "拉伸",
        completed: false,
        muscles: [
          { name: "腹直肌", activation: 40 },
          { name: "髂腰肌", activation: 85 },
          { name: "股四头肌", activation: 60 }
        ],
        tips: [
          "上半身缓慢后仰，感受腹部前侧的拉伸感",
          "髋部充分前推，不要只弯腰",
          "保持20-30秒，采用深呼吸放松"
        ],
        mistakes: [
          { wrong: "过度后仰导致腰椎挤压", right: "后仰幅度以舒适拉伸感为限，不要产生疼痛" },
          { wrong: "快速弹振式拉伸", right: "静态保持，配合缓慢的深呼吸逐步加深幅度" }
        ],
        advice: "训练后的拉伸非常关键，能有效降低延迟性肌肉酸痛（DOMS）。建议每个拉伸姿势保持至少30秒，可在呼气时微微加深幅度。"
      }
    ]);
    const showAnalysis = common_vendor.ref(false);
    const currentIndex = common_vendor.ref(0);
    const currentItem = common_vendor.computed(() => planList.value[currentIndex.value]);
    const openAnalysis = (index) => {
      currentIndex.value = index;
      showAnalysis.value = true;
    };
    const closeAnalysis = () => {
      showAnalysis.value = false;
    };
    const toggleTask = (index) => {
      planList.value[index].completed = !planList.value[index].completed;
    };
    const completedCount = common_vendor.computed(() => planList.value.filter((item) => item.completed).length);
    const progress = common_vendor.computed(() => completedCount.value / planList.value.length * 100);
    return (_ctx, _cache) => {
      return {
        a: progress.value + "%",
        b: common_vendor.t(completedCount.value),
        c: common_vendor.t(planList.value.length),
        d: common_vendor.f(planList.value, (item, index, i0) => {
          return common_vendor.e({
            a: item.completed
          }, item.completed ? {} : {}, {
            b: common_vendor.t(item.name),
            c: common_vendor.t(item.sets),
            d: common_vendor.t(item.reps),
            e: common_vendor.t(item.rest),
            f: common_vendor.o(($event) => toggleTask(index), index),
            g: common_vendor.t(item.typeLabel),
            h: common_vendor.n(item.type),
            i: common_vendor.o(($event) => openAnalysis(index), index),
            j: index,
            k: item.completed ? 1 : ""
          });
        }),
        e: common_vendor.o(closeAnalysis, "64"),
        f: common_vendor.p({
          visible: showAnalysis.value,
          item: currentItem.value
        })
      };
    };
  }
};
const MiniProgramPage = /* @__PURE__ */ common_vendor._export_sfc(_sfc_main, [["__scopeId", "data-v-bee4c29d"]]);
wx.createPage(MiniProgramPage);
//# sourceMappingURL=../../../.sourcemap/mp-weixin/pages/plan/plan.js.map
