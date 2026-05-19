<template>
  <view class="chat-container">
    <view class="header">
      <view class="header-left">
        <text class="header-title">AI Trainer</text>
        <text class="header-subtitle">Your personal fitness guide</text>
      </view>
    </view>

    <scroll-view
      class="chat-scroll"
      scroll-y="true"
      :scroll-into-view="scrollToId"
      scroll-with-animation
    >
      <view v-if="!loading && messages.length === 0" class="empty-state">
        <view class="empty-logo">✨</view>
        <text class="empty-title">今天想练点什么？</text>
        <text class="empty-desc">当前模式：{{ useRAG ? '基于专属文档提供指导' : '自由拓展解答' }}</text>
      </view>

      <view
        v-for="(msg, idx) in messages"
        :key="idx"
        class="message-row"
        :class="msg.role === 'user' ? 'row-user' : 'row-ai'"
      >
        <template v-if="msg.role === 'assistant'">
          <view class="avatar ai-avatar">
            <image
              class="ai-avatar-img"
              src="https://api.dicebear.com/9.x/bottts/svg?seed=Robert"
              mode="aspectFit"
            />
          </view>
          <view class="message-content ai-content">
            <text class="markdown-text">{{ msg.content || '思考中...' }}</text>
            <view class="status-tag" v-if="msg.content">
              {{ msg.rag ? '📚 RAG 检索' : '⚡️ 自由回复' }}
            </view>
          </view>
        </template>

        <template v-if="msg.role === 'user'">
          <view class="message-content user-bubble">
            <text>{{ msg.content }}</text>
          </view>
        </template>
      </view>

      <view id="msg-bottom" style="height: 1px;"></view>
      <view style="height: 80rpx;"></view>
    </scroll-view>

    <view class="input-area">
      <!-- RAG 切换按钮 & 清除按钮 放在输入框上方 -->
      <view class="toolbar-row">
        <view class="toolbar-left">
          <view
            class="pill-btn"
            :class="{ 'pill-active': useRAG }"
            @click="toggleRAG"
          >
            <text class="pill-icon">{{ useRAG ? '📚' : '⚡️' }}</text>
            <text class="pill-text">{{ useRAG ? '文档库' : '自由对话' }}</text>
          </view>
        </view>
        <view class="toolbar-right">
          <view class="icon-btn" @click="handleClear">
            <text class="icon-text">🗑</text>
          </view>
        </view>
      </view>

      <view class="input-wrapper">
        <input
          class="input-box"
          type="text"
          placeholder="Message AI Trainer..."
          placeholder-class="placeholder-text"
          v-model="inputText"
          :disabled="sending"
          confirm-type="send"
          @confirm="handleSend"
        />
        <view
          class="send-btn"
          :class="{ 'btn-active': inputText.trim() && !sending }"
          @click="handleSend"
        >
          <text class="send-arrow" v-if="!sending">↑</text>
          <view class="loading-dot" v-else></view>
        </view>
      </view>
      <text class="footer-tip">AI 私教可能生成不准确的信息，请结合自身体能情况评估。</text>
    </view>
  </view>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'

// ================== 配置区 ==================
const API_BASE = 'http://46a8871a.r2.cpolar.top'
const USE_STREAM = false

// ================== 状态 ==================
const messages = ref([])
const inputText = ref('')
const sending = ref(false)
const loading = ref(true)
const scrollToId = ref('')
const STORAGE_KEY = 'ai_trainer_chat_history'
const useRAG = ref(true)

// 用于节流 scrollToBottom
let scrollTimer = null

// ================== 工具方法 ==================

function scrollToBottom() {
  nextTick(() => {
    scrollToId.value = ''
    setTimeout(() => {              // ✅ 用 setTimeout 代替
      scrollToId.value = 'msg-bottom'
    }, 50)                          // 50ms 足以触发 scroll-view 重绘
  })
}


function throttledScrollToBottom() {
  if (scrollTimer) return
  scrollToBottom()
  scrollTimer = setTimeout(() => {
    scrollTimer = null
  }, 200)
}

function loadHistory() {
  try {
    const raw = uni.getStorageSync(STORAGE_KEY)
    if (raw) {
      const arr = typeof raw === 'string' ? JSON.parse(raw) : raw
      if (Array.isArray(arr)) {
        if (messages.value.length === 0) {
          messages.value = arr.slice(-300)
        }
        return arr
      }
    }
  } catch (e) {
    console.warn('读取历史失败', e)
  }
  return []
}

function saveHistory(arr) {
  try {
    uni.setStorageSync(STORAGE_KEY, JSON.stringify(arr.slice(-300)))
  } catch (e) {
    console.warn('保存历史失败', e)
  }
}

// ================== RAG 开关 ==================
function toggleRAG() {
  if (sending.value) return
  useRAG.value = !useRAG.value
  uni.showToast({
    title: useRAG.value ? '已切换至文档库模式' : '已切换至自由对话模式',
    icon: 'none',
    duration: 1500
  })
}

// ================== 清除聊天记录 ==================
function handleClear() {
  if (sending.value) return
  uni.showModal({
    title: '清除对话',
    content: '确定要开启一段新的健身对话吗？',
    confirmText: '确定',
    confirmColor: '#0D0D0D',
    success(res) {
      if (res.confirm) {
        try { uni.removeStorageSync(STORAGE_KEY) } catch (e) {}
        messages.value = []
        uni.showToast({ title: '已开启新对话', icon: 'none', duration: 1500 })
      }
    }
  })
}

// ================== 核心：发送消息 ==================
async function handleSend() {
  const text = (inputText.value || '').trim()
  if (!text || sending.value) return

  inputText.value = ''
  sending.value = true

  const userMsg = { role: 'user', content: text }
  messages.value.push(userMsg)
  scrollToBottom()

  const aiMsg = { role: 'assistant', content: '', rag: useRAG.value }
  messages.value.push(aiMsg)
  scrollToBottom()

  const currentHistory = loadHistory()
  const newHistory = [...currentHistory, userMsg]

  try {
    if (USE_STREAM) {
      await fetchStream(text, aiMsg, newHistory)
    } else {
      await fetchNormal(text, aiMsg, newHistory)
    }
  } catch (err) {
    console.error(err)
    if (!aiMsg.content) {
      aiMsg.content = '请求失败，请稍后再试'
    }
  } finally {
    sending.value = false
    scrollToBottom()
  }
}

// ================== 非流式调用 ==================
function fetchNormal(question, aiMsg, newHistory) {
  return new Promise((resolve, reject) => {
    const endpoint = useRAG.value ? '/api/v1/chat' : '/api/v1/chat/plain'

    uni.request({
      url: `${API_BASE}${endpoint}`,
      method: 'POST',
      header: { 'Content-Type': 'application/json' },
      data: { question },
      success: (res) => {
        try {
          const obj = typeof res.data === 'string' ? JSON.parse(res.data) : (res.data || {})
          const answer = obj?.data?.answer || obj?.answer || JSON.stringify(obj)
          aiMsg.content = answer
          newHistory.push({ role: 'assistant', content: answer })
          saveHistory(newHistory)
          resolve()
        } catch (e) {
          aiMsg.content = '解析返回结果失败'
          reject(e)
        }
      },
      fail: (err) => {
        aiMsg.content = '网络异常，请检查网络或接口地址'
        reject(err)
      }
    })
  })
}

// ================== 流式调用 ==================
function decodeChunk(buffer) {
  if (!buffer) return ''
  try {
    const uint8 = new Uint8Array(buffer)
    let str = ''
    for (let i = 0; i < uint8.length; i++) {
      str += String.fromCharCode(uint8[i])
    }
    return str
  } catch (e) {
    return ''
  }
}

function parseSSELines(text, aiMsg) {
  const lines = text.split('\n')
  let temp = ''

  const processTemp = () => {
    if (temp.startsWith('data:')) {
      const jsonStr = temp.replace(/^data:\s*/, '')
      if (jsonStr.trim() === '[DONE]') return
      try {
        const obj = JSON.parse(jsonStr)
        const answer = obj?.answer || ''
        if (answer) {
          aiMsg.content += answer
        }
      } catch (e) {
        if (jsonStr) {
          aiMsg.content += jsonStr
        }
      }
    }
    temp = ''
  }

  lines.forEach(line => {
    if (!line.trim()) {
      processTemp()
      return
    }
    temp += (temp ? '\n' : '') + line
  })
  processTemp()
}

function fetchStream(question, aiMsg, newHistory) {
  return new Promise((resolve, reject) => {
    const endpoint = useRAG.value
      ? '/api/v1/chat/stream'
      : '/api/v1/chat/plain/stream'

    const requestTask = uni.request({
      url: `${API_BASE}${endpoint}`,
      method: 'POST',
      header: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream'
      },
      data: { question },
      enableChunked: true,
      responseType: 'arraybuffer',
      success: () => {},
      fail: (err) => {
        aiMsg.content = aiMsg.content || '网络异常，请检查网络'
        reject(err)
      }
    })

    requestTask.onChunkReceived((res) => {
      try {
        const text = decodeChunk(res.data) || ''
        parseSSELines(text, aiMsg)
        throttledScrollToBottom()
      } catch (e) {
        console.warn('解析流式数据异常', e)
      }
    })

    const originSuccess = requestTask.success
    requestTask.success = (res) => {
      try { originSuccess?.(res) } catch (_) {}
      newHistory.push({ role: 'assistant', content: aiMsg.content })
      saveHistory(newHistory)
      resolve()
    }

    setTimeout(() => {
      try { requestTask.abort() } catch (_) {}
      if (!aiMsg.content) {
        aiMsg.content = '响应超时，请重试'
        reject(new Error('timeout'))
      }
    }, 60000)
  })
}

// ================== 生命周期 ==================
onMounted(() => {
  loadHistory()
  loading.value = false
  setTimeout(() => {
    scrollToBottom()
  }, 300)
})
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #FFFFFF;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* 顶部导航 — 只保留标题 */
.header {
  padding: 100rpx 40rpx 30rpx;
  background-color: #FFFFFF;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 10;
}
.header-left {
  display: flex;
  flex-direction: column;
}
.header-title {
  font-size: 36rpx;
  font-weight: 700;
  color: #0D0D0D;
  letter-spacing: -0.5rpx;
}
.header-subtitle {
  font-size: 24rpx;
  color: #8E8E93;
  margin-top: 4rpx;
}

/* 聊天内容区域 */
.chat-scroll {
  flex: 1;
  padding: 0 40rpx;
  box-sizing: border-box;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60%;
  opacity: 0.8;
}
.empty-logo {
  font-size: 80rpx;
  margin-bottom: 30rpx;
}
.empty-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #0D0D0D;
  margin-bottom: 12rpx;
}
.empty-desc {
  font-size: 28rpx;
  color: #8E8E93;
}

/* 消息行布局 */
.message-row {
  display: flex;
  margin-bottom: 48rpx;
  width: 100%;
}
.row-user {
  justify-content: flex-end;
}
.row-ai {
  justify-content: flex-start;
  align-items: flex-start;
}

/* AI 头像 */
.avatar {
  width: 60rpx;
  height: 60rpx;
  border-radius: 50%;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 24rpx;
}
.ai-avatar {
  background-color: #10A37F;
  color: #FFFFFF;
  font-size: 22rpx;
  font-weight: 700;
}

/* 消息内容区 */
.message-content {
  max-width: 80%;
  position: relative;
}

/* 用户气泡 */
.user-bubble {
  background-color: #F4F4F5;
  color: #0D0D0D;
  padding: 24rpx 32rpx;
  border-radius: 40rpx;
  border-bottom-right-radius: 8rpx;
  font-size: 30rpx;
  line-height: 1.5;
  word-break: break-word;
}

/* AI 内容 */
.ai-content {
  color: #0D0D0D;
  padding-top: 8rpx;
}
.markdown-text {
  font-size: 30rpx;
  line-height: 1.7;
  word-break: break-word;
}

/* 底部状态标签 */
.status-tag {
  display: inline-block;
  margin-top: 16rpx;
  font-size: 20rpx;
  color: #8E8E93;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  border: 1px solid #E5E5EA;
}

/* ================== 底部输入区 ================== */
.input-area {
  padding: 20rpx 40rpx 60rpx;
  background-color: #FFFFFF;
}

/* 工具栏行：RAG 切换 + 清除 */
.toolbar-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}
.toolbar-left {
  display: flex;
  align-items: center;
}
.toolbar-right {
  display: flex;
  align-items: center;
}

/* 极简按钮组件 */
.pill-btn {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 10rpx 20rpx;
  border-radius: 100rpx;
  border: 1px solid #E5E5EA;
  background-color: #FFFFFF;
  transition: all 0.2s;
}
.pill-active {
  background-color: #F9F9F9;
  border-color: #D1D1D6;
}
.pill-icon { font-size: 24rpx; }
.pill-text {
  font-size: 24rpx;
  color: #1C1C1E;
  font-weight: 500;
}

.icon-btn {
  padding: 10rpx 16rpx;
  border-radius: 100rpx;
  transition: all 0.2s;
}
.icon-btn:active {
  background-color: #F2F2F7;
}
.icon-text {
  font-size: 32rpx;
  color: #8E8E93;
}

/* 输入框行 */
.input-wrapper {
  display: flex;
  align-items: center;
  background-color: #FFFFFF;
  border: 1px solid #D1D1D6;
  border-radius: 48rpx;
  padding: 12rpx 16rpx 12rpx 36rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.03);
}
.input-box {
  flex: 1;
  height: 64rpx;
  font-size: 30rpx;
  color: #0D0D0D;
}
.placeholder-text {
  color: #AEAEB2;
}

/* 发送按钮 */
.send-btn {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background-color: #E5E5EA;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.2s;
  flex-shrink: 0;
  margin-left: 16rpx;
}
.btn-active {
  background-color: #0D0D0D;
}
.btn-active:active {
  transform: scale(0.95);
}
.send-arrow {
  color: #FFFFFF;
  font-size: 32rpx;
  font-weight: 600;
}

/* 发送中加载动画点 */
.loading-dot {
  width: 12rpx;
  height: 12rpx;
  background-color: #FFFFFF;
  border-radius: 50%;
  animation: pulse 1s infinite alternate;
}
@keyframes pulse {
  0% { transform: scale(0.8); opacity: 0.5; }
  100% { transform: scale(1.2); opacity: 1; }
}

/* 底部免责提示语 */
.footer-tip {
  display: block;
  text-align: center;
  font-size: 20rpx;
  color: #AEAEB2;
  margin-top: 20rpx;
}
/* AI 头像图片 */
.ai-avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

</style>
