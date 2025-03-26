// 不依赖 sharp 库的简单实现
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const publicImagesDir = path.join(__dirname, '../public/assets/images');
const srcImagesDir = path.join(__dirname, '../src/assets/images');

// 确保输出目录存在
if (!fs.existsSync(publicImagesDir)) {
  fs.mkdirSync(publicImagesDir, { recursive: true });
}

if (!fs.existsSync(srcImagesDir)) {
  fs.mkdirSync(srcImagesDir, { recursive: true });
}

console.log('创建示例 JPG 文件以替代 SVG 转换...');

// 为了简化，我们创建一个简单的样例 JPG 文件
const sampleJpgContent = Buffer.from('/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAABAAEDAREAAhEBAxEB/8QAFAABAAAAAAAAAAAAAAAAAAAACP/EABQQAQAAAAAAAAAAAAAAAAAAAAD/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8AT+gAA//Z', 'base64');

// 创建 table-bg.jpg 在两个目录
fs.writeFileSync(path.join(publicImagesDir, 'table-bg.jpg'), sampleJpgContent);
fs.writeFileSync(path.join(srcImagesDir, 'table-bg.jpg'), sampleJpgContent);
console.log('已创建 table-bg.jpg');

// 创建 default-avatar.jpg 在两个目录
fs.writeFileSync(path.join(publicImagesDir, 'default-avatar.jpg'), sampleJpgContent);
fs.writeFileSync(path.join(srcImagesDir, 'default-avatar.jpg'), sampleJpgContent);
console.log('已创建 default-avatar.jpg');

console.log('图片处理完成！'); 