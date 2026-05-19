<template>
  <view class="profile-container">
    <!-- 顶部背景装饰 -->
    <view class="header-bg-decor">
      <view class="decor-circle c1"></view>
      <view class="decor-circle c2"></view>
      <view class="decor-circle c3"></view>
    </view>

    <view class="user-header">
      <!-- 顶部右侧小图标 -->
      <view class="header-actions">
        <view class="action-btn" hover-class="action-hover">
          <text class="action-icon">🔔</text>
          <view class="dot-badge"></view>
        </view>
        <view class="action-btn" hover-class="action-hover">
          <text class="action-icon">⚙️</text>
        </view>
      </view>

      <view class="user-info">
        <view class="avatar-wrapper">
          <image class="avatar" src="https://api.dicebear.com/7.x/avataaars/svg?seed=ProUser" mode="aspectFill"></image>
          <view class="avatar-ring"></view>
          <view class="online-dot"></view>
        </view>
        <view class="info-text">
          <text class="username">Alex Developer</text>
          <view class="badge-row">
            <view class="badge">
              <text class="badge-icon">👑</text>
              <text class="badge-text">PRO 会员</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 数据统计卡片 -->
    <view class="stats-card">
      <view class="stat-item">
        <view class="stat-num-wrap">
          <text class="stat-num">12</text>
          <text class="stat-unit">天</text>
        </view>
        <text class="stat-label">累计打卡</text>
      </view>

      <view class="stat-divider-wrap">
        <view class="stat-divider"></view>
      </view>

      <view class="stat-item">
        <view class="stat-num-wrap">
          <text class="stat-num highlight-orange">4.2</text>
          <text class="stat-unit">千</text>
        </view>
        <text class="stat-label">消耗 kCal</text>
      </view>

      <view class="stat-divider-wrap">
        <view class="stat-divider"></view>
      </view>

      <view class="stat-item">
        <view class="stat-num-wrap">
          <text class="stat-num highlight-green">3</text>
          <text class="stat-unit">个</text>
        </view>
        <text class="stat-label">专属计划</text>
      </view>
    </view>

    <!-- 功能菜单 -->
    <view class="section-title">
      <view class="title-bar"></view>
      <text class="title-text">常用功能</text>
    </view>

    <view class="menu-list">
      <view class="menu-item" hover-class="menu-hover" @click="goToPage('/pages/user/body-data')">
        <view class="menu-icon-box" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
          <text class="menu-emoji">📊</text>
        </view>
        <view class="menu-content">
          <text class="menu-text">我的身体数据</text>
          <text class="menu-desc">体重 / 体脂 / 围度</text>
        </view>
        <view class="menu-arrow-wrap">
          <text class="menu-arrow">›</text>
        </view>
      </view>

      <view class="menu-item" hover-class="menu-hover" @click="goToPage('/pages/user/favorites')">
        <view class="menu-icon-box" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
          <text class="menu-emoji">⭐</text>
        </view>
        <view class="menu-content">
          <text class="menu-text">收藏的动作库</text>
          <text class="menu-desc">已收藏 28 个动作</text>
        </view>
        <view class="menu-arrow-wrap">
          <text class="menu-arrow">›</text>
        </view>
      </view>

      <view class="menu-item" hover-class="menu-hover" @click="goToPage('/pages/user/repository')">
        <view class="menu-icon-box" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
          <text class="menu-emoji">📚</text>
        </view>
        <view class="menu-content">
          <text class="menu-text">知识库</text>
          <text class="menu-desc">运动 / 饮食 / 恢复</text>
        </view>
        <view class="menu-arrow-wrap">
          <text class="menu-arrow">›</text>
        </view>
      </view>

      <view class="menu-item" hover-class="menu-hover" @click="goToPage('/pages/user/settings')">
        <view class="menu-icon-box" style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);">
          <text class="menu-emoji">⚙️</text>
        </view>
        <view class="menu-content">
          <text class="menu-text">偏好与设置</text>
          <text class="menu-desc">通知 / 主题 / 隐私</text>
        </view>
        <view class="menu-arrow-wrap">
          <text class="menu-arrow">›</text>
        </view>
      </view>
    </view>

    <!-- 底部留白 -->
    <view style="height: 60rpx;"></view>
  </view>
</template>

<script setup>
const goToPage = (url) => {
  if (!url) return;
  uni.navigateTo({ url });
};
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  background-color: #F4F6FA;
  overflow-x: hidden;
}

/* ========== 顶部背景装饰 ========== */
.header-bg-decor {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 520rpx;
  z-index: 0;
  overflow: hidden;
  pointer-events: none;
}
.decor-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.08;
  background: #fff;
}
.c1 {
  width: 300rpx;
  height: 300rpx;
  top: -80rpx;
  right: -60rpx;
}
.c2 {
  width: 180rpx;
  height: 180rpx;
  top: 180rpx;
  left: -40rpx;
}
.c3 {
  width: 100rpx;
  height: 100rpx;
  top: 60rpx;
  left: 200rpx;
}

/* ========== 用户头部 ========== */
.user-header {
  position: relative;
  z-index: 1;
  height: 520rpx;
  background: linear-gradient(160deg, #0F2027 0%, #203A43 40%, #2C5364 100%);
  padding: 100rpx 48rpx 0;
  box-sizing: border-box;
  border-bottom-left-radius: 56rpx;
  border-bottom-right-radius: 56rpx;
  overflow: hidden;
}

.header-actions {
  display: flex;
  justify-content: flex-end;
  gap: 20rpx;
  margin-bottom: 50rpx;
}
.action-btn {
  position: relative;
  width: 76rpx;
  height: 76rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(10px);
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.2s;
}
.action-hover {
  background: rgba(255, 255, 255, 0.22);
  transform: scale(0.95);
}
.action-icon {
  font-size: 34rpx;
}
.dot-badge {
  position: absolute;
  top: 10rpx;
  right: 12rpx;
  width: 14rpx;
  height: 14rpx;
  background: #FF6B6B;
  border-radius: 50%;
  border: 2rpx solid rgba(15, 32, 39, 0.6);
}

.user-info {
  display: flex;
  align-items: center;
}

/* 头像 */
.avatar-wrapper {
  position: relative;
  flex-shrink: 0;
}
.avatar {
  width: 136rpx;
  height: 136rpx;
  border-radius: 50%;
  position: relative;
  z-index: 1;
}
.avatar-ring {
  position: absolute;
  inset: -6rpx;
  border-radius: 50%;
  border: 4rpx solid rgba(255, 255, 255, 0.25);
  z-index: 2;
}
.online-dot {
  position: absolute;
  bottom: 6rpx;
  right: 6rpx;
  width: 24rpx;
  height: 24rpx;
  background: #2ED573;
  border-radius: 50%;
  border: 4rpx solid #203A43;
  z-index: 3;
}

.info-text {
  margin-left: 32rpx;
  flex: 1;
}
.username {
  font-size: 42rpx;
  font-weight: 800;
  color: #FFFFFF;
  display: block;
  margin-bottom: 16rpx;
  letter-spacing: 1rpx;
}
.badge-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
}
.badge {
  display: inline-flex;
  align-items: center;
  background: linear-gradient(135deg, #FFD700 0%, #FFA502 100%);
  padding: 6rpx 18rpx;
  border-radius: 100rpx;
}
.badge-icon {
  font-size: 20rpx;
  margin-right: 6rpx;
}
.badge-text {
  font-size: 20rpx;
  font-weight: 700;
  color: #3D2E00;
  letter-spacing: 1rpx;
}
.member-expire {
  background: rgba(255, 255, 255, 0.1);
  padding: 6rpx 16rpx;
  border-radius: 100rpx;
}
.expire-text {
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.6);
}

/* ========== 统计卡片 ========== */
.stats-card {
  position: relative;
  z-index: 2;
  margin: -72rpx 36rpx 0;
  background: #FFFFFF;
  border-radius: 28rpx;
  padding: 44rpx 20rpx 40rpx;
  display: flex;
  justify-content: space-around;
  align-items: center;
  box-shadow:
    0 4rpx 24rpx rgba(44, 83, 100, 0.06),
    0 1rpx 3rpx rgba(44, 83, 100, 0.04);
}
.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}
.stat-num-wrap {
  display: flex;
  align-items: baseline;
  justify-content: center;
  margin-bottom: 8rpx;
}
.stat-num {
  font-size: 48rpx;
  font-weight: 900;
  color: #2D3436;
  letter-spacing: -1rpx;
}
.stat-num.highlight-orange {
  color: #FF6348;
}
.stat-num.highlight-green {
  color: #2ED573;
}
.stat-unit {
  font-size: 22rpx;
  font-weight: 600;
  color: #B2BEC3;
  margin-left: 4rpx;
}
.stat-label {
  font-size: 22rpx;
  color: #A4B0BD;
  letter-spacing: 1rpx;
}
.stat-divider-wrap {
  flex-shrink: 0;
  padding: 0 8rpx;
}
.stat-divider {
  width: 2rpx;
  height: 56rpx;
  background: linear-gradient(180deg, transparent 0%, #E8ECF1 50%, transparent 100%);
  border-radius: 2rpx;
}

/* ========== 区块标题 ========== */
.section-title {
  display: flex;
  align-items: center;
  padding: 48rpx 48rpx 24rpx;
}
.title-bar {
  width: 6rpx;
  height: 28rpx;
  border-radius: 6rpx;
  background: linear-gradient(180deg, #2C5364, #4facfe);
  margin-right: 16rpx;
}
.title-text {
  font-size: 28rpx;
  font-weight: 700;
  color: #636E72;
  letter-spacing: 2rpx;
}

/* ========== 功能菜单 ========== */
.menu-list {
  padding: 0 36rpx;
}
.menu-item {
  display: flex;
  align-items: center;
  background: #FFFFFF;
  padding: 28rpx 28rpx;
  border-radius: 24rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 16rpx rgba(44, 83, 100, 0.04);
  transition: all 0.25s ease;
}
.menu-hover {
  background: #F8FAFF;
  transform: scale(0.985);
  box-shadow: 0 4rpx 24rpx rgba(44, 83, 100, 0.08);
}

.menu-icon-box {
  width: 88rpx;
  height: 88rpx;
  border-radius: 22rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 28rpx;
  flex-shrink: 0;
}
.menu-emoji {
  font-size: 38rpx;
}

.menu-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.menu-text {
  font-size: 30rpx;
  font-weight: 700;
  color: #2D3436;
  margin-bottom: 6rpx;
  letter-spacing: 0.5rpx;
}
.menu-desc {
  font-size: 22rpx;
  color: #B2BEC3;
  letter-spacing: 0.5rpx;
}

.menu-arrow-wrap {
  flex-shrink: 0;
  margin-left: 12rpx;
  width: 48rpx;
  height: 48rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 50%;
  background: #F4F6FA;
}
.menu-arrow {
  font-size: 36rpx;
  color: #C8D6E5;
  font-weight: 300;
  line-height: 1;
  margin-top: -4rpx;
}
</style>
