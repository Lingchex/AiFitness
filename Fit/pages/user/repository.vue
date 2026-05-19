<template>
  <view class="kb-container">
    <view class="header-bg-decor">
      <view class="decor-circle c1"></view>
      <view class="decor-circle c2"></view>
      <view class="decor-circle c3"></view>
    </view>

    <view class="kb-header">
      <view class="header-top">
        <view class="page-title-wrap">
          <text class="page-title">知识库</text>
          <text class="page-subtitle">共 {{ books.length }} 份参考资料</text>
        </view>
        <view class="header-actions">
          <view class="action-btn upload-btn" hover-class="upload-hover" @tap="handleUpload">
            <text class="action-icon">➕</text>
            <text class="upload-text">上传解析</text>
          </view>
        </view>
      </view>

      <view class="search-bar">
        <text class="search-icon">🔍</text>
        <input type="text" v-model="searchQuery" placeholder="搜索知识库内容..." placeholder-style="color: rgba(255,255,255,0.45); font-size: 26rpx;" />
      </view>
    </view>

    <view class="tabs-card">
      <view v-for="(tab, index) in tabs" :key="index"
        :class="['tab-item', activeTab === index ? 'active' : '']"
        @tap="activeTab = index">
        <text class="tab-text">{{ tab.label }}</text>
        <view class="tab-count" :class="{ 'active-count': activeTab === index }">{{ tab.count }}</view>
      </view>
      <view class="tab-indicator-bar">
        <view class="tab-indicator" :style="{ transform: `translateX(${activeTab * 100}%)` }"></view>
      </view>
    </view>

    <scroll-view scroll-y class="book-scroll" :show-scrollbar="false">
      <view class="book-list">
        <view class="book-card" v-for="(item, index) in displayBooks" :key="index"
          hover-class="card-hover" @tap="openBook(item)">
          <view class="book-cover-box" :style="{ background: item.gradient }">
            <view class="cover-pattern">
              <view class="pattern-line" v-for="n in 5" :key="n"></view>
            </view>
            <text class="cover-emoji">{{ item.emoji }}</text>
            <view class="file-type-tag">
              <text class="file-type-text">{{ item.fileType }}</text>
            </view>
            </view>
          
          <view class="book-info">
            <text class="book-title">{{ item.title }}</text>
            <view class="book-meta">
              <view class="meta-left">
                <text class="meta-size">{{ item.size }}</text>
                <view class="meta-dot"></view>
                <text class="meta-pages">{{ item.pages }}页</text>
              </view>
              <view class="meta-source" :class="'source-' + item.type">
                <text class="meta-source-text">{{ item.type === 'official' ? '系统' : '私有' }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <view class="empty-hint" v-if="displayBooks.length === 0">
        <text class="empty-emoji">📂</text>
        <text class="empty-text">暂无相关文档，请尝试切换分类</text>
      </view>

      <view style="height: 80rpx;"></view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue';

const activeTab = ref(0);
const searchQuery = ref('');

const books = ref([
  {
    title: '肌肉增长解剖学',
    size: '12.5 MB',
    pages: 186,
    type: 'official',
    fileType: 'PDF',
    emoji: '💪',
    gradient: 'linear-gradient(145deg, #667eea 0%, #764ba2 100%)'
  },
  {
    title: '营养膳食进阶指南',
    size: '8.2 MB',
    pages: 124,
    type: 'official',
    fileType: 'PDF',
    emoji: '🥗',
    gradient: 'linear-gradient(145deg, #f093fb 0%, #f5576c 100%)'
  },
  {
    title: '心率与有氧训练',
    size: '15.1 MB',
    pages: 210,
    type: 'official',
    fileType: 'PDF',
    emoji: '❤️‍🔥',
    gradient: 'linear-gradient(145deg, #4facfe 0%, #00f2fe 100%)'
  },
  {
    title: '2024深蹲力量训练记录',
    size: '2.4 MB',
    pages: 32,
    type: 'user',
    fileType: 'PDF',
    emoji: '🏋️',
    gradient: 'linear-gradient(145deg, #a8edea 0%, #fed6e3 100%)'
  },
  {
    title: '拉伸恢复完全手册',
    size: '6.7 MB',
    pages: 98,
    type: 'official',
    fileType: 'EPUB',
    emoji: '🧘',
    gradient: 'linear-gradient(145deg, #ffecd2 0%, #fcb69f 100%)'
  },
  {
    title: '训练日志模板V2.0',
    size: '1.1 MB',
    pages: 16,
    type: 'user',
    fileType: 'DOCX',
    emoji: '📝',
    gradient: 'linear-gradient(145deg, #89f7fe 0%, #66a6ff 100%)'
  }
]);

const tabs = computed(() => [
  { label: '全部', count: books.value.length },
  { label: '公共库', count: books.value.filter(b => b.type === 'official').length },
  { label: '私有库', count: books.value.filter(b => b.type === 'user').length }
]);

const displayBooks = computed(() => {
  let list = books.value;
  // 过滤分类
  if (activeTab.value === 1) list = list.filter(b => b.type === 'official');
  if (activeTab.value === 2) list = list.filter(b => b.type === 'user');
  
  // 过滤搜索
  if (searchQuery.value) {
    list = list.filter(b => b.title.includes(searchQuery.value));
  }
  return list;
});

// handleUpload 函数替换为你 script setup 中的原函数
const handleUpload = () => {
  // 1. 微信小程序环境下，选择聊天记录中的文件（PDF通常存在这里）
  wx.chooseMessageFile({
    count: 1,
    type: 'file',
    extension: ['pdf'], // 过滤仅 PDF
    success: (res) => {
      const file = res.tempFiles[0];
      
      // 校验文件大小 (例如限制 20MB)
      if (file.size > 20 * 1024 * 1024) {
        uni.showToast({ title: '文件不能超过 20MB', icon: 'none' });
        return;
      }

      uni.showLoading({ title: 'AI 解析入库中...', mask: true });

      // 2. 调用 FastAPI 上传接口
      uni.uploadFile({
        url: 'https://你的服务器域名.com/api/v1/documents/upload', // 必须是 https
        filePath: file.path,
        name: 'file', // 必须对应后端接口中的 file: UploadFile 参数名
        header: {
          // 如果有登录态，在这里传 Token
          // 'Authorization': 'Bearer ' + storage.getToken()
        },
        success: (uploadRes) => {
          // 注意：uploadFile 返回的是 String，需要 JSON.parse
          const data = JSON.parse(uploadRes.data);
          
          if (data.code === 200) {
            uni.showToast({ title: '入库成功', icon: 'success' });
            
            // 3. 将新上传的文档动态添加到前端列表（实时反馈）
            const newDoc = {
              title: file.name,
              size: (file.size / 1024 / 1024).toFixed(1) + ' MB',
              pages: data.data.pages || '?', // 后端若返回页数
              type: 'user',
              fileType: 'PDF',
              emoji: '📄',
              gradient: 'linear-gradient(145deg, #a18cd1 0%, #fbc2eb 100%)'
            };
            books.value.unshift(newDoc); // 插到列表最前面
          } else {
            uni.showModal({
              title: '处理失败',
              content: data.detail || '解析失败，请重试',
              showCancel: false
            });
          }
        },
        fail: (err) => {
          console.error('上传失败:', err);
          uni.showToast({ title: '网络请求失败', icon: 'none' });
        },
        complete: () => {
          uni.hideLoading();
        }
      });
    },
    fail: (err) => {
      // 用户取消选择
      console.log('取消选择文件');
    }
  });
};
const openBook = (item) => {
  uni.showToast({ title: '解析中: ' + item.title, icon: 'none' });
};
</script>

<style scoped>
.kb-container {
  min-height: 100vh;
  background-color: #F8FAFC;
  overflow-x: hidden;
}

/* ========== 背景装饰 ========== */
.header-bg-decor {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 480rpx;
  z-index: 0;
  overflow: hidden;
  pointer-events: none;
}
.decor-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.07;
  background: #fff;
}
.c1 { width: 300rpx; height: 300rpx; top: -100rpx; right: -50rpx; }
.c2 { width: 180rpx; height: 180rpx; top: 220rpx; left: -40rpx; }
.c3 { width: 100rpx; height: 100rpx; top: 60rpx; left: 200rpx; }

/* ========== 头部 ========== */
.kb-header {
  position: relative;
  z-index: 1;
  background: linear-gradient(160deg, #1e293b 0%, #334155 100%);
  padding: 100rpx 40rpx 60rpx;
  border-bottom-left-radius: 56rpx;
  border-bottom-right-radius: 56rpx;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40rpx;
}
.page-title-wrap {
  display: flex;
  flex-direction: column;
}
.page-title {
  font-size: 48rpx;
  font-weight: 800;
  color: #FFFFFF;
  letter-spacing: 1rpx;
}
.page-subtitle {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 4rpx;
}

.upload-btn {
  background: #3b82f6 !important;
  width: auto !important;
  height: 72rpx !important;
  padding: 0 28rpx;
  border-radius: 36rpx !important;
  display: flex;
  align-items: center;
  gap: 8rpx;
}
.upload-text {
  color: #fff;
  font-size: 24rpx;
  font-weight: 600;
}
.action-icon {
  font-size: 28rpx;
}

.search-bar {
  background: rgba(255, 255, 255, 0.12);
  height: 84rpx;
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  padding: 0 32rpx;
  border: 1rpx solid rgba(255, 255, 255, 0.1);
}
.search-icon {
  font-size: 30rpx;
  margin-right: 20rpx;
  opacity: 0.7;
}
.search-bar input {
  color: #FFF;
  font-size: 28rpx;
  flex: 1;
}

/* ========== Tab 切换 (优化版) ========== */
.tabs-card {
  position: relative;
  z-index: 2;
  margin: -32rpx 40rpx 0;
  background: #FFFFFF;
  border-radius: 28rpx;
  padding: 10rpx;
  display: flex;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.05);
}
.tab-item {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10rpx;
  padding: 22rpx 0;
  position: relative;
  z-index: 2;
}
.tab-text {
  font-size: 28rpx;
  color: #64748b;
  font-weight: 500;
  transition: all 0.3s;
}
.tab-count {
  font-size: 20rpx;
  color: #94a3b8;
  background: #f1f5f9;
  padding: 2rpx 14rpx;
  border-radius: 100rpx;
  font-weight: 600;
}
.tab-item.active .tab-text {
  color: #1e293b;
  font-weight: 700;
}
.active-count {
  color: #3b82f6 !important;
  background: rgba(59, 130, 246, 0.1) !important;
}

/* 滑动条容器 */
.tab-indicator-bar {
  position: absolute;
  bottom: 12rpx;
  left: 10rpx;
  right: 10rpx;
  height: 6rpx;
  pointer-events: none;
}
/* 具体的滑动指示器线段 */
.tab-indicator {
  width: 33.33%;
  height: 100%;
  display: flex;
  justify-content: center;
  transition: transform 0.3s cubic-bezier(0.65, 0, 0.35, 1);
}
.tab-indicator::after {
  content: '';
  width: 40rpx; /* 线段宽度 */
  height: 100%;
  background: #3b82f6;
  border-radius: 10rpx;
}

/* ========== 文档列表 ========== */
.book-scroll {
  height: calc(100vh - 420rpx);
}
.book-list {
  display: flex;
  flex-wrap: wrap;
  padding: 32rpx 32rpx 0;
  justify-content: space-between;
}

.book-card {
  width: 47.5%;
  background: #FFFFFF;
  border-radius: 32rpx;
  margin-bottom: 32rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.03);
  border: 1rpx solid rgba(0, 0, 0, 0.02);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.card-hover {
  transform: translateY(-8rpx);
  box-shadow: 0 20rpx 40rpx rgba(0, 0, 0, 0.08);
}

.book-cover-box {
  height: 200rpx;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}
.cover-pattern {
  position: absolute;
  inset: 0;
  opacity: 0.12;
  display: flex;
  flex-direction: column;
  justify-content: space-evenly;
  padding: 24rpx;
}
.pattern-line {
  height: 6rpx;
  border-radius: 6rpx;
  background: #fff;
}
.pattern-line:nth-child(1) { width: 40%; }
.pattern-line:nth-child(2) { width: 70%; }
.pattern-line:nth-child(3) { width: 50%; }

.cover-emoji {
  font-size: 80rpx;
  z-index: 1;
}

.file-type-tag {
  position: absolute;
  top: 16rpx;
  left: 16rpx;
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(4px);
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
}
.file-type-text {
  font-size: 18rpx;
  color: #fff;
  font-weight: 700;
}

.book-info {
  padding: 24rpx;
}
.book-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #1e293b;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
  height: 78rpx; /* 保持高度一致 */
  margin-bottom: 16rpx;
}
.book-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.meta-left {
  display: flex;
  align-items: center;
  gap: 6rpx;
}
.meta-size, .meta-pages {
  font-size: 20rpx;
  color: #94a3b8;
}
.meta-dot {
  width: 4rpx;
  height: 4rpx;
  border-radius: 50%;
  background: #cbd5e1;
}
.meta-source {
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  font-size: 18rpx;
  font-weight: 600;
}
.source-official { background: #f1f5f9; color: #475569; }
.source-user { background: #eff6ff; color: #3b82f6; }

/* ========== 空状态 ========== */
.empty-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 160rpx 0;
}
.empty-emoji {
  font-size: 100rpx;
  margin-bottom: 24rpx;
  filter: grayscale(1);
  opacity: 0.5;
}
.empty-text {
  font-size: 28rpx;
  color: #94a3b8;
}
</style>