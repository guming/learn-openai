"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var fs = require("fs");
var markdown_it_1 = require("markdown-it");
// 创建 markdown-it 实例
var md = new markdown_it_1.default();
// 读取 Markdown 文件内容
var markdownContent = fs.readFileSync('./pages/docs/install-redis-on-mac-os', 'utf-8');
// 解析 Markdown 文本为 HTML
var parsedHTML = md.render(markdownContent);
// 使用正则表达式匹配标题（<h1> 到 <h6>）
var sections = parsedHTML.match(/<h[1-6]>(.*?)<\/h[1-6]>/g);
if (sections) {
    // 输出每个 section 的标题
    sections.forEach(function (section, index) {
        var title = section.replace(/<\/?h[1-6]>/g, '');
        console.log("Section ".concat(index + 1, ": ").concat(title));
    });
}
else {
    console.log('No sections found.');
}
