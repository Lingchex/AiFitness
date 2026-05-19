<!-- 主页面 index.vue（或原文件名） -->
<template>
	<view class="plan-container">
		<view class="plan-header">
			<text class="date">Today, 14 Oct</text>
			<text class="title">AI智训计划</text>
			<view class="progress-bar">
				<view class="progress-fill" :style="{ width: progress + '%' }"></view>
			</view>
			<text class="progress-text">已完成 {{ completedCount }}/{{ planList.length }}</text>
		</view>

		<scroll-view class="task-list" scroll-y="true">
			<view
				class="task-card"
				v-for="(item, index) in planList"
				:key="index"
				:class="{ 'is-completed': item.completed }"
			>
				<view class="task-left" @click="toggleTask(index)">
					<view class="checkbox">
						<view class="check-inner" v-if="item.completed"></view>
					</view>
					<view class="task-info">
						<text class="task-name">{{ item.name }}</text>
						<text class="task-desc">{{ item.sets }}组 × {{ item.reps }}次 · 休息 {{ item.rest }}s</text>
					</view>
				</view>
				<view class="task-tag" :class="item.type">{{ item.typeLabel }}</view>
				<view class="ai-btn" @click.stop="openAnalysis(index)">
					<view class="ai-icon-wrap">
						<text class="ai-icon">✦</text>
					</view>
					<text class="ai-label">AI分析</text>
				</view>
			</view>
			<view style="height: 60rpx;"></view>
		</scroll-view>

		<!-- 引入提取后的 AI 分析组件 -->
		<AnalysisOverlay
			:visible="showAnalysis"
			:item="currentItem"
			@close="closeAnalysis"
		/>
	</view>
</template>

<script setup>
import { ref, computed } from 'vue'
import AnalysisOverlay from '@/components/planing/AnalysisOverlay.vue';

const planList = ref([
	{
		name: '高抬腿热身', sets: 3, reps: '30', rest: 15,
		type: 'warmup', typeLabel: '热身', completed: false,
		muscles: [
			{ name: '股四头肌', activation: 85 },
			{ name: '髂腰肌', activation: 78 },
			{ name: '小腿三头肌', activation: 65 },
		],
		tips: [
			'挺胸收腹，保持躯干稳定，不要前后晃动',
			'大腿抬至与地面平行，小腿自然下垂',
			'前脚掌着地，落地时膝关节微屈缓冲',
		],
		mistakes: [
			{ wrong: '身体后仰，靠惯性甩腿', right: '核心收紧，躯干保持直立，主动抬腿' },
			{ wrong: '全脚掌或脚跟着地', right: '前脚掌着地，利用跟腱弹性缓冲' },
		],
		advice: '作为热身动作，建议前2组以60%速度进行，最后一组提速至85%最大速度，逐步激活神经系统，为后续高强度训练做好准备。'
	},
	{
		name: '俄罗斯挺身', sets: 4, reps: '20', rest: 30,
		type: 'core', typeLabel: '核心', completed: false,
		muscles: [
			{ name: '腹直肌', activation: 72 },
			{ name: '腹内外斜肌', activation: 90 },
			{ name: '竖脊肌', activation: 55 },
		],
		tips: [
			'双脚离地或脚跟轻触地面，保持V字坐姿',
			'转体时肩部带动，不要仅转头或用手臂代偿',
			'呼气转体，吸气回正，保持呼吸节奏',
		],
		mistakes: [
			{ wrong: '背部拱起，驼背做动作', right: '挺胸，脊柱保持中立位，想象头顶向上延伸' },
			{ wrong: '双手持重甩动借力', right: '控制离心过程，转体匀速，2秒转向2秒回正' },
		],
		advice: '你当前的核心基础较好，建议尝试在转体末端增加0.5秒的顶峰收缩，能显著提升腹斜肌的刺激深度。若想进阶，可手持2-4kg药球。'
	},
	{
		name: '波比跳', sets: 4, reps: '15', rest: 45,
		type: 'hiit', typeLabel: 'HIIT', completed: true,
		muscles: [
			{ name: '胸大肌', activation: 68 },
			{ name: '股四头肌', activation: 82 },
			{ name: '三角肌前束', activation: 60 },
			{ name: '臀大肌', activation: 75 },
		],
		tips: [
			'下蹲时臀部向后，不要膝关节过度前移',
			'俯卧撑阶段身体成一直线，不要塌腰',
			'起跳时充分伸展踝、膝、髋三关节',
		],
		mistakes: [
			{ wrong: '跳过俯卧撑直接起跳', right: '每个波比跳必须包含完整的俯卧撑动作' },
			{ wrong: '落地时膝关节内扣', right: '落地时膝盖对准脚尖方向，臀部向后坐缓冲' },
		],
		advice: '波比跳是本计划中强度最高的动作。建议第1-2组保持标准动作质量，第3-4组若体能下降可适当降低跳起高度，但不要省略俯卧撑环节，保证训练容量。'
	},
	{
		name: '平板支撑', sets: 3, reps: '60', rest: 30,
		type: 'core', typeLabel: '核心', completed: false,
		muscles: [
			{ name: '腹横肌', activation: 95 },
			{ name: '腹直肌', activation: 70 },
			{ name: '竖脊肌', activation: 62 },
		],
		tips: [
			'肘关节位于肩膀正下方，前臂平贴地面',
			'收紧臀部，不要塌腰也不要撅臀',
			'目光看向双手之间，颈椎保持中立',
		],
		mistakes: [
			{ wrong: '腰部下沉塌腰', right: '想象肚脐向脊柱方向靠近，骨盆后倾' },
			{ wrong: '憋气坚持', right: '保持均匀的腹式呼吸，每次吸气3秒呼气3秒' },
		],
		advice: '60秒的平板支撑对核心耐力要求较高。若中段感到腰部酸痛，说明腹横肌力量不足，建议先拆分为3×30秒，逐步延长单次时间。'
	},
	{
		name: '腹部拉伸', sets: 1, reps: '1', rest: 0,
		type: 'stretch', typeLabel: '拉伸', completed: false,
		muscles: [
			{ name: '腹直肌', activation: 40 },
			{ name: '髂腰肌', activation: 85 },
			{ name: '股四头肌', activation: 60 },
		],
		tips: [
			'上半身缓慢后仰，感受腹部前侧的拉伸感',
			'髋部充分前推，不要只弯腰',
			'保持20-30秒，采用深呼吸放松',
		],
		mistakes: [
			{ wrong: '过度后仰导致腰椎挤压', right: '后仰幅度以舒适拉伸感为限，不要产生疼痛' },
			{ wrong: '快速弹振式拉伸', right: '静态保持，配合缓慢的深呼吸逐步加深幅度' },
		],
		advice: '训练后的拉伸非常关键，能有效降低延迟性肌肉酸痛（DOMS）。建议每个拉伸姿势保持至少30秒，可在呼气时微微加深幅度。'
	},
])

const showAnalysis = ref(false)
const currentIndex = ref(0)

const currentItem = computed(() => planList.value[currentIndex.value])

const openAnalysis = (index) => {
	currentIndex.value = index
	showAnalysis.value = true
}

const closeAnalysis = () => {
	showAnalysis.value = false
}

const toggleTask = (index) => {
	planList.value[index].completed = !planList.value[index].completed
}

const completedCount = computed(() => planList.value.filter(item => item.completed).length)
const progress = computed(() => (completedCount.value / planList.value.length) * 100)
</script>

<style scoped>
.plan-container {
	min-height: 100vh;
	background-color: #FAFAFA;
	padding: 40rpx;
	box-sizing: border-box;
}
.plan-header {
	margin-top: 60rpx;
	margin-bottom: 50rpx;
}
.date {
	font-size: 28rpx;
	color: #00D2D3;
	font-weight: bold;
	text-transform: uppercase;
	letter-spacing: 2rpx;
}
.title {
	font-size: 54rpx;
	font-weight: 900;
	color: #2D3436;
	display: block;
	margin-top: 10rpx;
	margin-bottom: 30rpx;
}
.progress-bar {
	height: 16rpx;
	background-color: #EEEEEE;
	border-radius: 20rpx;
	overflow: hidden;
	margin-bottom: 12rpx;
}
.progress-fill {
	height: 100%;
	background: linear-gradient(90deg, #00D2D3, #0984E3);
	border-radius: 20rpx;
	transition: width 0.3s ease;
}
.progress-text {
	font-size: 24rpx;
	color: #636E72;
}
.task-list {
	max-height: calc(100vh - 340rpx);
}
.task-card {
	background-color: #FFFFFF;
	border-radius: 32rpx;
	padding: 36rpx;
	display: flex;
	align-items: center;
	margin-bottom: 30rpx;
	box-shadow: 0 10rpx 40rpx rgba(0,0,0,0.04);
	transition: all 0.3s ease;
	gap: 20rpx;
}
.task-card:active {
	transform: scale(0.98);
}
.is-completed {
	opacity: 0.6;
	background-color: #F8F9FA;
	box-shadow: none;
}
.is-completed .task-name {
	text-decoration: line-through;
	color: #B2BEC3;
}
.task-left {
	flex: 1;
	display: flex;
	align-items: center;
	min-width: 0;
}
.checkbox {
	width: 48rpx;
	height: 48rpx;
	border: 4rpx solid #DFE6E9;
	border-radius: 16rpx;
	margin-right: 24rpx;
	display: flex;
	justify-content: center;
	align-items: center;
	transition: all 0.2s;
	flex-shrink: 0;
}
.is-completed .checkbox {
	border-color: #00D2D3;
	background-color: #00D2D3;
}
.check-inner {
	width: 20rpx;
	height: 20rpx;
	background-color: #FFFFFF;
	border-radius: 6rpx;
}
.task-info {
	flex: 1;
	min-width: 0;
}
.task-name {
	font-size: 34rpx;
	font-weight: 700;
	color: #2D3436;
	display: block;
	margin-bottom: 8rpx;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}
.task-desc {
	font-size: 26rpx;
	color: #636E72;
}
.task-tag {
	padding: 8rpx 20rpx;
	border-radius: 100rpx;
	font-size: 22rpx;
	font-weight: bold;
	flex-shrink: 0;
}
.warmup { background-color: #FFEAA7; color: #D35400; }
.core { background-color: #81ECEC; color: #008080; }
.hiit { background-color: #FF7675; color: #FFFFFF; }
.stretch { background-color: #A29BFE; color: #FFFFFF; }

/* AI 分析按钮 */
.ai-btn {
	display: flex;
	flex-direction: column;
	align-items: center;
	flex-shrink: 0;
	gap: 6rpx;
}
.ai-icon-wrap {
	width: 64rpx;
	height: 64rpx;
	border-radius: 50%;
	background: linear-gradient(135deg, #00D2D3, #0984E3);
	display: flex;
	justify-content: center;
	align-items: center;
	box-shadow: 0 6rpx 20rpx rgba(9, 132, 227, 0.35);
}
.ai-icon {
	font-size: 28rpx;
	color: #FFFFFF;
	line-height: 1;
}
.ai-label {
	font-size: 20rpx;
	color: #0984E3;
	font-weight: 600;
	white-space: nowrap;
}
</style>
