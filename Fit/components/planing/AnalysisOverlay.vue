<template>
	<view class="analysis-overlay" :class="{ show: visible }" @click="$emit('close')">
		<view class="panel" :class="{ enter }" @click.stop>

			<!-- ===== 顶部沉浸式 Header ===== -->
			<view class="header">
				<view class="nav">
					<view class="back" @click="$emit('close')"></view>
					<text class="title">AI 动作分析</text>
				</view>

				<!-- 运动信息 -->
				<view class="exercise-card">
					<view class="badge" :class="item.type">{{ item.typeLabel }}</view>
					<text class="name">{{ item.name }}</text>
					<text class="meta">
						{{ item.sets }}组 × {{ item.reps }}次 · 休息 {{ item.rest }}s
					</text>
				</view>
			</view>

			<!-- ===== 内容区 ===== -->
			<scroll-view scroll-y class="content">

				<!-- AI 提示 -->
				<view class="ai-tip">
					<view class="ai-dot"></view>
					<text>AI将分析动作轨迹、稳定性与发力路径</text>
				</view>

				<!-- ===== 上传区域 ===== -->
				<view class="upload-card">

					<!-- 空状态 -->
					<view v-if="!videoPath" class="empty">
						<view class="icon-wrap">
							<view class="icon-video"></view>
						</view>

						<text class="empty-title">上传动作视频</text>
						<text class="empty-desc">
							侧面全身 · 10~30秒 · 保持完整动作周期
						</text>
					</view>

					<!-- 预览 -->
					<view v-else class="preview">
						<video
							:src="videoPath"
							class="video"
							controls
						></video>

						<view class="preview-bar">
							<text class="ready">已就绪 ✓</text>
							<text class="reset" @click="removeVideo">重新拍摄</text>
						</view>
					</view>

				</view>

				<!-- ===== 按钮区 ===== -->
				<view class="actions">
					<button class="btn primary" @click="chooseVideo('camera')">
						📹 拍摄
					</button>
					<button class="btn ghost" @click="chooseVideo('album')">
						相册
					</button>
				</view>

				<!-- ===== AI分析按钮 ===== -->
				<button
					class="submit"
					:class="{ active: videoPath && !isAnalyzing, analyzing: isAnalyzing }"
					:disabled="isAnalyzing"
					@click="submitAnalysis"
				>
					<!-- 分析中的专属动画 -->
					<view v-if="isAnalyzing" class="analyzing-wrap">
						<view class="pulse-ring"></view>
						<view class="pulse-ring delay"></view>
						<text class="analyzing-text">{{ loadingText }}</text>
					</view>
					<text v-else>开始 AI 分析</text>
				</button>

				<!-- ===== 分析结果展示区 ===== -->
				<view v-if="analysisResult" class="result-card">
					<view class="result-header">
						<view class="ai-dot"></view>
						<text class="result-title">AI 评估报告</text>
					</view>
					
					<!-- 视频信息摘要 -->
					<view class="result-meta">
						<text>动作类型：{{ analysisResult.video_info.exercise_type_detected_or_given }}</text>
						<text>视频时长：{{ analysisResult.video_info.duration_sec }}s</text>
						<text>提取帧数：{{ analysisResult.video_info.extracted_frames }}</text>
					</view>

					<!-- 大模型 Markdown 报告渲染 -->
					<view class="report-content">
						<rich-text :nodes="formattedReport"></rich-text>
					</view>
				</view>

				<view style="height: 80rpx"></view>
			</scroll-view>
		</view>
	</view>
</template>

<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
	visible: Boolean,
	item: Object
})

const emit = defineEmits(['close'])

const enter = ref(false)
const videoPath = ref('')
const isAnalyzing = ref(false)
const analysisResult = ref(null) // 存储后端返回的 data 对象
const loadingText = ref('AI深度分析中...') // 动态加载文字

watch(() => props.visible, (v) => {
	enter.value = v
	// 每次打开面板时，清空之前的结果
	if(v) analysisResult.value = null
})

const chooseVideo = (type) => {
	uni.chooseVideo({
		sourceType: [type],
		compressed: false,
		maxDuration: 60,
		success: (res) => {
			videoPath.value = res.tempFilePath
			analysisResult.value = null // 重新选择视频时清空报告
		}
	})
}

const removeVideo = () => {
	videoPath.value = ''
	analysisResult.value = null
}

// 简易的 Markdown 转换，让换行和基础格式在 rich-text 中好看一点
// 强烈建议后续 npm install markdown-it 引入真正的 md 解析器
const formattedReport = computed(() => {
	if (!analysisResult.value || !analysisResult.value.report) return ''
	let md = analysisResult.value.report
	// 极简转换：换行符转 <br>，粗体转 <b>
	let html = md.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
	return html
})

// 后端 API 地址，请确保真机/模拟机能访问到此 IP
const API_BASE_URL = 'https://1bce4b79.r2.cpolar.top' 
const submitAnalysis = async () => {
	if (!videoPath.value || isAnalyzing.value) return

	isAnalyzing.value = true
	analysisResult.value = null
	loadingText.value = '正在上传视频...'
	
	// 开启动态 loading 提示
	uni.showLoading({ title: loadingText.value, mask: true })

	// 模拟等待时的文字变幻，缓解用户焦虑
	const tips = [
		'AI 正在提取关键帧...',
		'正在分析动作轨迹...',
		'正在评估发力路径...',
		'正在生成评估报告...',
		'分析需要一点时间，请耐心等待...'
	]
	let tipIndex = 0
	const tipTimer = setInterval(() => {
		if (isAnalyzing.value) {
			loadingText.value = tips[tipIndex % tips.length]
			uni.showLoading({ title: loadingText.value, mask: true })
			tipIndex++
		} else {
			clearInterval(tipTimer)
		}
	}, 4000) // 每4秒换一个提示

	try {
		// 使用 uni.uploadFile 发送文件和表单数据
		const uploadRes = await new Promise((resolve, reject) => {
			uni.uploadFile({
				url: `${API_BASE_URL}/api/analyze`,
				filePath: videoPath.value,
				name: 'file', // 对应后端 request.files['file']
				formData: {
					'exercise_type': props.item.name || '自动识别', // 把当前动作名传给后端
					'max_frames': '8',
					'frame_strategy': 'adaptive'
				},
				// ⭐ 核心：将超时时间延长到 120 秒 (120000ms)，防止大模型分析超时中断
				timeout: 240000, 
				success: (res) => {
					// ⚠️ 注意：uni.uploadFile 返回的 data 是字符串，需要手动解析
					if (res.statusCode === 200) {
						try {
							resolve(JSON.parse(res.data))
						} catch(e) {
							reject(new Error('返回数据解析失败'))
						}
					} else {
						try {
							const errData = JSON.parse(res.data)
							reject(new Error(errData.msg || '请求失败'))
						} catch(e) {
							reject(new Error(`服务器错误: ${res.statusCode}`))
						}
					}
				},
				fail: (err) => {
					// 如果是超时错误，给出明确提示
					if (err.errMsg && err.errMsg.includes('timeout')) {
						reject(new Error('请求超时，AI分析时间过长，请稍后重试'))
					} else {
						reject(new Error('网络请求失败，请检查IP和后端服务'))
					}
				}
			})
		})

		// 请求成功，保存结果
		if (uploadRes.code === 200) {
			analysisResult.value = uploadRes.data
			uni.showToast({ title: '分析完成', icon: 'success' })
		} else {
			throw new Error(uploadRes.msg || '分析失败')
		}

	} catch (error) {
		console.error('分析出错:', error)
		uni.showModal({
			title: '分析失败',
			content: error.message || '未知错误',
			showCancel: false
		})
	} finally {
		clearInterval(tipTimer) // 清除文字轮播定时器
		isAnalyzing.value = false
		uni.hideLoading()
	}
}
</script>

<style scoped>
/* ===== 遮罩 ===== */
.analysis-overlay {
	position: fixed;
	inset: 0;
	background: rgba(0,0,0,0);
	transition: 0.3s;
	pointer-events: none;
	z-index: 999;
}
.analysis-overlay.show {
	background: rgba(0,0,0,0.5);
	pointer-events: auto;
}

/* ===== 面板 ===== */
.panel {
	position: absolute;
	right: 0;
	top: 0;
	bottom: 0;
	width: 100%;
	background: #F5F6FA;
	transform: translateX(100%);
	transition: 0.4s cubic-bezier(.2,.8,.2,1);
	display: flex;
	flex-direction: column;
	overflow: hidden;
}

/* ===== 内容 ===== */
.content {
	max-width: 800rpx;
	margin-left: auto;
	margin-right: auto;
	padding: 30rpx;
	box-sizing: border-box;
	flex: 1;
	height: 0;
}

.panel.enter {
	transform: translateX(0);
}

/* ===== Header ===== */
.header {
	padding: 60rpx 30rpx 30rpx;
	background: linear-gradient(135deg,#0984E3,#00D2D3);
	color: #fff;
}

/* 导航 */
.nav {
	display: flex;
	align-items: center;
}
.back {
	width: 30rpx;
	height: 30rpx;
	border-left: 4rpx solid #fff;
	border-bottom: 4rpx solid #fff;
	transform: rotate(45deg);
}
.title {
	margin-left: 20rpx;
	font-weight: bold;
}

/* 卡片 */
.exercise-card {
	margin-top: 30rpx;
	background: rgba(255,255,255,0.15);
	backdrop-filter: blur(20rpx);
	padding: 30rpx;
	border-radius: 24rpx;
}

.badge {
	padding: 6rpx 18rpx;
	border-radius: 20rpx;
	font-size: 22rpx;
	display: inline-block;
	background: rgba(255,255,255,0.2);
}
.name {
	font-size: 40rpx;
	font-weight: bold;
	display: block;
	margin-top: 10rpx;
}
.meta {
	font-size: 24rpx;
	opacity: 0.9;
}

/* ===== 内容 ===== */
.content {
	max-width: 800rpx;
	margin-left: auto;
	margin-right: auto;
	padding: 30rpx;
	box-sizing: border-box
}

/* AI提示 */
.ai-tip {
	display: flex;
	align-items: center;
	font-size: 24rpx;
	color: #636e72;
	margin-bottom: 20rpx;
}
.ai-dot {
	width: 12rpx;
	height: 12rpx;
	background: #00cec9;
	border-radius: 50%;
	margin-right: 10rpx;
}

/* 上传卡 */
.upload-card {
	background: #fff;
	border-radius: 24rpx;
	padding: 40rpx;
	box-shadow: 0 10rpx 30rpx rgba(0,0,0,0.05);
}

/* 空状态 */
.empty {
	text-align: center;
}
.icon-wrap {
	width: 120rpx;
	height: 120rpx;
	margin: 0 auto 20rpx;
	border-radius: 50%;
	background: #eef7ff;
	display: flex;
	align-items: center;
	justify-content: center;
}
.icon-video {
	width: 50rpx;
	height: 36rpx;
	border: 4rpx solid #0984E3;
	border-radius: 6rpx;
}

.empty-title {
	font-weight: bold;
	display: block;
}
.empty-desc {
	font-size: 24rpx;
	color: #888;
}

/* 预览 */
.video {
	width: 100%;
	height: 360rpx;
	border-radius: 16rpx;
	background: #000;
}
.preview-bar {
	display: flex;
	justify-content: space-between;
	margin-top: 10rpx;
}
.ready {
	color: #00b894;
}
.reset {
	color: #636e72;
}

/* 按钮 */
.actions {
	display: flex;
	margin-top: 30rpx;
}
.btn {
	flex: 1;
	height: 90rpx;
	border-radius: 20rpx;
	margin-right: 20rpx;
	line-height: 90rpx;
	font-size: 28rpx;
}
.primary {
	background: linear-gradient(135deg,#0984E3,#00D2D3);
	color: #fff;
}
.ghost {
	background: #fff;
	color: #333;
	border: 1rpx solid #eee;
}

/* 提交 */
.submit {
	margin-top: 30rpx;
	height: 100rpx;
	border-radius: 24rpx;
	background: #ccc;
	color: #fff;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 32rpx;
	border: none;
	overflow: hidden;
	position: relative;
}
.submit.active {
	background: linear-gradient(135deg,#0984E3,#00D2D3);
	box-shadow: 0 10rpx 30rpx rgba(0,0,0,0.2);
}
.submit.analyzing {
	background: linear-gradient(135deg,#0984E3,#00D2D3);
	box-shadow: 0 10rpx 30rpx rgba(0,0,0,0.2);
	cursor: not-allowed;
}

/* ===== 新增：分析中脉冲动画 ===== */
.analyzing-wrap {
	position: relative;
	display: flex;
	align-items: center;
	justify-content: center;
	width: 100%;
	height: 100%;
	z-index: 1;
}
.pulse-ring {
	position: absolute;
	width: 60rpx;
	height: 60rpx;
	border: 4rpx solid rgba(255,255,255,0.6);
	border-radius: 50%;
	animation: pulse-expand 2s ease-out infinite;
}
.pulse-ring.delay {
	animation-delay: 0.5s;
}
.analyzing-text {
	position: relative;
	z-index: 2;
	font-size: 28rpx;
	letter-spacing: 2rpx;
}

@keyframes pulse-expand {
	0% { transform: scale(0.5); opacity: 1; }
	100% { transform: scale(2.5); opacity: 0; }
}

/* ===== 结果展示区 ===== */
.result-card {
	margin-top: 40rpx;
	background: #fff;
	border-radius: 24rpx;
	padding: 30rpx;
	box-shadow: 0 10rpx 30rpx rgba(0,0,0,0.05);
	animation: fadeInUp 0.6s cubic-bezier(.2,.8,.2,1) forwards;
}

@keyframes fadeInUp {
	from { opacity: 0; transform: translateY(30rpx); }
	to { opacity: 1; transform: translateY(0); }
}

.result-header {
	display: flex;
	align-items: center;
	margin-bottom: 20rpx;
	padding-bottom: 20rpx;
	border-bottom: 1rpx solid #f0f0f0;
}
.result-title {
	font-size: 32rpx;
	font-weight: bold;
	margin-left: 10rpx;
	color: #2d3436;
}

.result-meta {
	background: #f8f9fa;
	padding: 20rpx;
	border-radius: 12rpx;
	margin-bottom: 20rpx;
	display: flex;
	flex-direction: column;
	gap: 8rpx;
	font-size: 24rpx;
	color: #636e72;
}

.report-content {
	font-size: 26rpx;
	line-height: 1.8;
	color: #2d3436;
	word-break: break-all;
}
</style>
