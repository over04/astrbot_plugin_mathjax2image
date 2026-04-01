# MathJax2Image
> 喜欢的话可以给个 Star 喵，有问题欢迎提 Issue/PR
> 
将 LLM 输出中的 Markdown / MathJax / TikZ / Mermaid 内容自动渲染为精美图片的 AstrBot 插件。

## 安装

### 1. 安装依赖
```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. CDN 资源
插件使用阿里云 OSS CDN 加载 MathJax、TikZJax 和字体资源，无需额外下载。

## 特性

- **LaTeX 公式渲染** - 支持行内公式 `$...$` 和独立公式 `$$...$$`
- **TikZ 图形渲染** - 支持 `tikzpicture`、`tikzcd` 等环境，自动检测所需库
- **Markdown 智能预处理** - 自动修复格式问题，确保正确渲染
- **代码块行号** - 代码块自动显示行号，长代码自动换行
- **可配置背景色** - 支持自定义模板背景颜色
- **CDN 渲染** - 使用阿里云 OSS CDN，插件体积小（约 400KB）

## 效果展示

### TikZ 自然变换图

![TikZ 示例](examples/tikz_example.png)

**TikZ 示例代码：**
```latex
\begin{tikzpicture}[scale=1.8]
  \draw[gray, rounded corners] (-0.8,-1.2) rectangle (0.8,1.2);
  \node at (0,1.5) {$\mathcal{C}$};
  \node (X) at (0,0.5) {$X$};
  \node (Y) at (0,-0.5) {$Y$};
  \draw[->] (X) -- (Y) node[midway,left] {$f$};

  \draw[gray, rounded corners] (3,-1.5) rectangle (6,1.5);
  \node at (4.5,1.8) {$\mathcal{D}$};

  \node (FX) at (3.5,0.7) {$F(X)$};
  \node (FY) at (3.5,-0.7) {$F(Y)$};

  \node (GX) at (5.5,0.7) {$G(X)$};
  \node (GY) at (5.5,-0.7) {$G(Y)$};

  \draw[->] (FX) -- (FY) node[midway,left] {$F(f)$};
  \draw[->] (GX) -- (GY) node[midway,right] {$G(f)$};
  \draw[->, blue, dashed] (FX) -- (GX) node[midway,above] {$\alpha_X$};
  \draw[->, blue, dashed] (FY) -- (GY) node[midway,below] {$\alpha_Y$};

  \draw[->, red, bend left=20] (0.9,0.3) to node[above] {$F$} (3.4,0.5);
  \draw[->, orange, bend right=20] (0.9,-0.3) to node[below] {$G$} (3.4,-0.5);
\end{tikzpicture}
```

## 工作方式

插件会自动拦截 LLM 最终文本回复。

- 命中“自动渲染正则配置”任意一条规则：直接渲染为图片，只返回图片
- 未命中：保持原始文本输出
- 渲染失败：回退原始文本输出

## 配置

在 AstrBot 插件配置中可设置：

- `background_color` - 模板背景颜色（默认 `#FDFBF0`）
- `custom_match_patterns` - 自动渲染正则配置，每行一条正则

默认配置已覆盖：

- Markdown：标题、列表、引用、代码块、表格
- LaTeX / MathJax：`$...$`、`$$...$$`、`\(...\)`、`\[...\]`、常见公式环境
- TikZ / TikZ-CD / circuitikz / chemfig
- Mermaid 代码块

## 支持

[AstrBot 帮助文档](https://astrbot.app)

## 致谢

- [obsidian-tikzjax](https://github.com/artisticat1/obsidian-tikzjax) - 提供支持 AMS 字体的 TikZJax 实现
- [MathJax](https://www.mathjax.org/) - 数学公式渲染引擎
- [BaKoMa Fonts](http://www.ctan.org/pkg/bakoma-fonts) - TeX 字体
