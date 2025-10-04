const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 创建目录结构
if (!fs.existsSync('dist')) fs.mkdirSync('dist');
if (!fs.existsSync('dist/nodes')) fs.mkdirSync('dist/nodes');
if (!fs.existsSync('dist/nodes/picEdit')) fs.mkdirSync('dist/nodes/picEdit');

// 编译 TypeScript 文件
try {
    console.log('Compiling TypeScript files...');
    execSync('npx tsc --project .', { stdio: 'inherit' });
    console.log('TypeScript compilation completed.');
} catch (error) {
    console.error('TypeScript compilation failed:', error.message);
}

// 复制 SVG 文件
try {
    if (fs.existsSync('nodes/picEdit/picEdit.svg')) {
        fs.copyFileSync('nodes/picEdit/picEdit.svg', 'dist/nodes/picEdit/picEdit.svg');
        console.log('SVG file copied.');
    }
} catch (error) {
    console.error('Failed to copy SVG:', error.message);
}

console.log('Build completed.');