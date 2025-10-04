const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('Starting build process...');

// 清理并创建目录结构
if (fs.existsSync('dist')) {
    fs.rmSync('dist', { recursive: true, force: true });
}

fs.mkdirSync('dist', { recursive: true });
fs.mkdirSync('dist/nodes', { recursive: true });
fs.mkdirSync('dist/nodes/picEdit', { recursive: true });

// 手动编译每个文件
console.log('Compiling TypeScript files...');

try {
    // 编译 index.ts
    execSync('npx tsc index.ts --outDir dist --declaration --target es2019 --module commonjs --esModuleInterop --skipLibCheck --moduleResolution node', { stdio: 'pipe' });
    console.log('✓ index.ts compiled');
} catch (error) {
    console.log('⚠ index.ts compilation failed, creating manually...');
    
    // 手动创建 index.js
    const indexContent = `"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.PicEdit = void 0;
var PicEdit_node_1 = require("./nodes/picEdit/PicEdit.node");
Object.defineProperty(exports, "PicEdit", { enumerable: true, get: function () { return PicEdit_node_1.PicEdit; } });
`;
    fs.writeFileSync('dist/index.js', indexContent);
    
    const indexDts = `export { PicEdit } from './nodes/picEdit/PicEdit.node';
`;
    fs.writeFileSync('dist/index.d.ts', indexDts);
    console.log('✓ index files created manually');
}

try {
    // 编译 PicEdit.node.ts
    execSync('npx tsc nodes/picEdit/PicEdit.node.ts --outDir dist --declaration --target es2019 --module commonjs --esModuleInterop --skipLibCheck --moduleResolution node', { stdio: 'pipe' });
    console.log('✓ PicEdit.node.ts compiled');
} catch (error) {
    console.log('⚠ PicEdit.node.ts compilation failed');
    console.log(error.toString());
}

try {
    // 编译 SharpImageProcessor.ts
    execSync('npx tsc nodes/picEdit/SharpImageProcessor.ts --outDir dist --declaration --target es2019 --module commonjs --esModuleInterop --skipLibCheck --moduleResolution node', { stdio: 'pipe' });
    console.log('✓ SharpImageProcessor.ts compiled');
} catch (error) {
    console.log('⚠ SharpImageProcessor.ts compilation failed');
    console.log(error.toString());
}

// 复制 SVG 文件
try {
    if (fs.existsSync('nodes/picEdit/picEdit.svg')) {
        fs.copyFileSync('nodes/picEdit/picEdit.svg', 'dist/nodes/picEdit/picEdit.svg');
        console.log('✓ SVG file copied');
    }
} catch (error) {
    console.log('⚠ Failed to copy SVG:', error.message);
}

console.log('Build process completed!');

// 列出生成的文件
console.log('\nGenerated files:');
function listFiles(dir, prefix = '') {
    if (!fs.existsSync(dir)) return;
    const files = fs.readdirSync(dir);
    files.forEach(file => {
        const filePath = path.join(dir, file);
        const stats = fs.statSync(filePath);
        if (stats.isDirectory()) {
            console.log(prefix + file + '/');
            listFiles(filePath, prefix + '  ');
        } else {
            console.log(prefix + file);
        }
    });
}
listFiles('dist');