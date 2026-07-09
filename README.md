# Patent to Zemax Skill

[中文说明](#中文说明) | [English](#english)

## 中文说明

这是一个 Codex Skill，用于把公开光学设计专利转换为可审计的 Zemax OpticStudio 顺序模式模型。它保留“专利原文 → 标准化处方 JSON → ZMX → ZOS-API 回读验证”的证据链，重点支持旋转对称、纯透射式光刻物镜。

### 当前版本新增内容

- Clear Semi-Diameter 默认保持 Automatic，不再把专利自由口径静默写成 fixed 半口径。
- 光刻物镜按物方 NA 设置 Zemax 孔径。对于掩膜到晶圆的缩小投影物镜，通常按 `物方 NA = 像方 NA / |缩小倍率|` 从专利像方 NA 推导。
- 通过 ZOS-API 打开并验证 Real Ray Aiming，适配高 NA 有限共轭光刻系统。
- 专利中的每个数值实施例、example 或 table 都必须被建模；如果不能可靠复现，必须明确标记原因。
- 输出中文 / 英文双语复现报告。
- 每个输出包包含原专利 PDF，方便把 ZMX、报告、验证日志和来源文件一起审阅。
- 报告中增加 RMS 点列斑直径作为参考指标；当前推送版本不包含优化，也不判断是否应该优化。
- 改进 ZOS-API 验证：覆盖物方介质、浸没介质声明、玻璃缺失、非有限 automatic 半口径和 layout 导出问题。
- 新增实施例清单校验器，用于发现“专利里还有数值表但没有建模”的遗漏。

### 功能

- 接受 CN、US、JP、EP、WO/PCT 专利号、PDF 或扫描图片。
- 输出处方 JSON、`.zmx`、验证日志、可信度报告和 ZOS-API layout。
- 使用物高定义掩膜视场，并从专利像方 NA 和倍率推导 Zemax `ObjectSpaceNA`。
- 强制使用 Real Ray Aiming，并在 ZOS-API 验证报告中记录设置。
- 区分原文抄录、确定性派生和推断值，禁止静默修正 OCR、玻璃映射或符号解释。
- 可准备包含原专利、最终报告和 ZMX 的 Outlook 邮件草稿；实际发送需要再次确认。

### 安装与使用

直接把本仓库链接交给 Codex，或将 `patent-to-zemax` 目录复制到个人 Codex skills 目录：

```powershell
Copy-Item -Recurse patent-to-zemax "$HOME\.codex\skills\patent-to-zemax"
```

需要 Windows、现代 Ansys Zemax OpticStudio、可用 ZOS-API 许可和 Python.NET。

```text
使用 $patent-to-zemax 把专利 EP0770895A2 的所有实施例转换成 Zemax。
```

```powershell
python patent-to-zemax/scripts/build_lithography_zmx.py prescription.json --output output
python patent-to-zemax/scripts/export_zosapi_layout.py output/model.zmx --output output/layout.png
```

### 输出文件

每个可复现实施例会输出：

- `.zmx` Zemax 顺序模式文件
- `.prescription.json` 标准化处方与证据文件
- 中文 / 英文双语复现报告
- ZOS-API 验证 JSON / 日志
- ZOS-API 导出的镜头 layout 图
- 原专利 PDF 副本

### 公开基准

| 专利 | 权利人 | 波长 | 模型 | ZOS-API 验证 |
|---|---|---:|---|---|
| [EP0770895A2](https://patents.google.com/patent/EP0770895A2/en) | Nikon | 248.4 nm | 纯折射、干式、0.25×、54 个处方面 | 通过：像方 NA 0.6、ObjectSpaceNA、Real Ray Aiming |
| [US20030048547A1](https://patents.google.com/patent/US20030048547A1/en) | Carl Zeiss SMT | 193.304 nm | 纯折射、Table 3、63 个处方面 | 通过：像方 NA 0.75、ObjectSpaceNA、Real Ray Aiming |

额外批量复现验证包含用户给出的 5 个专利：`US5990926A`、`US6008884A`、`US6259508B1`、`US6788387B2` 和 `US7023627B2`。这批复现共生成 25 个数值实施例 / table，对应 ZMX、验证 JSON、layout 图、双语报告、原 PDF 副本，并通过实施例清单检查。

### 限制与许可

第一版重点覆盖旋转对称顺序系统：定焦或有限共轭光刻物镜、球面、偶次非球面、光阑、像面、波长、孔径、视场 / 物高、多配置数据和常见玻璃 / 材料映射。

自由曲面、衍射面、偏心 / 倾斜、折返式和非顺序系统目前会标记为超出范围，除非后续版本增加专门支持。

本 skill 不绕过验证码、付费墙或访问限制；如果联网获取失败，需要用户直接提供 PDF 或图片。允许自动推断，但必须记录原始值、修正依据、置信度和来源证据，禁止静默修正。生成的 ZMX 是复现工件，不声明与原始专利或商业设计完全等价。

转换代码采用 [MIT License](LICENSE)。第三方专利文件及其图表不因本仓库许可而重新授权。

## English

This Codex skill converts published optical-design patents into auditable Zemax OpticStudio sequential models. It preserves the evidence chain from patent source to normalized prescription JSON, ZMX model, and ZOS-API round-trip validation, with dedicated support for rotationally symmetric all-transmissive lithography objectives.

### What's new in the current version

- Keeps Zemax Clear Semi-Diameter automatic by default, instead of writing patent free-diameter values as fixed semi-diameters.
- Sets lithography aperture by object-space NA. For mask-to-wafer reduction objectives, the skill derives object-space NA from the patent image-side NA and magnification, typically `object NA = image NA / |reduction ratio|`.
- Enables and verifies Real Ray Aiming through ZOS-API for high-NA finite-conjugate lithography systems.
- Requires every numerical embodiment, example, or table in a patent to be modeled, or explicitly marked as unreconstructable with a reason.
- Produces bilingual Chinese/English reconstruction reports.
- Copies the original patent PDF into each output package so the ZMX, report, validation log, and source document stay together.
- Adds RMS spot diameter as a reference metric in reports. This value is reported for credibility review only; the pushed version does not perform optimization or optimization-eligibility gating.
- Improves ZOS-API validation for object-space materials, immersion declarations, missing glasses, non-finite automatic semi-diameters, and layout export.
- Adds an embodiment-inventory validator to catch patents where extra prescription tables were parsed but not modeled.

### Features

- Accepts CN, US, JP, EP, and WO/PCT patent numbers, PDFs, and scanned images.
- Produces prescription JSON, `.zmx`, validation logs, confidence reports, and ZOS-API layouts.
- Represents the mask field as object height and derives Zemax `ObjectSpaceNA` from the patent image-side NA and reduction ratio.
- Enforces Real Ray Aiming and records the setting in ZOS-API validation reports.
- Separates copied, deterministically derived, and inferred values; OCR corrections, sign interpretation, and glass mappings are never silent.
- Can prepare an Outlook draft containing the original patent, final report, and ZMX. Sending remains a separately confirmed action.

### Installation and usage

Give this repository link to Codex, or copy the `patent-to-zemax` directory into your personal Codex skills directory:

```powershell
Copy-Item -Recurse patent-to-zemax "$HOME\.codex\skills\patent-to-zemax"
```

Requirements: Windows, a modern Ansys Zemax OpticStudio installation, a valid ZOS-API license, and Python.NET.

```text
Use $patent-to-zemax to convert every embodiment in patent EP0770895A2 to Zemax.
```

```powershell
python patent-to-zemax/scripts/build_lithography_zmx.py prescription.json --output output
python patent-to-zemax/scripts/export_zosapi_layout.py output/model.zmx --output output/layout.png
```

### Outputs

For each reconstructable embodiment, the skill writes:

- `.zmx` sequential Zemax file
- `.prescription.json` normalized prescription and evidence file
- bilingual Chinese/English reconstruction report
- ZOS-API validation JSON/log
- ZOS-API exported layout image
- copied source patent PDF

### Public benchmarks

| Patent | Assignee | Wavelength | Model | ZOS-API validation |
|---|---|---:|---|---|
| [EP0770895A2](https://patents.google.com/patent/EP0770895A2/en) | Nikon | 248.4 nm | All-refractive, dry, 0.25×, 54 prescription surfaces | Passed: image-side NA 0.6, ObjectSpaceNA, Real Ray Aiming |
| [US20030048547A1](https://patents.google.com/patent/US20030048547A1/en) | Carl Zeiss SMT | 193.304 nm | All-refractive, Table 3, 63 prescription surfaces | Passed: image-side NA 0.75, ObjectSpaceNA, Real Ray Aiming |

Additional user-directed rebuild validation covered five patents: `US5990926A`, `US6008884A`, `US6259508B1`, `US6788387B2`, and `US7023627B2`. That rebuild produced 25 modeled numerical embodiments/tables with matching ZMX files, validation JSON files, exported layout images, bilingual reports, copied source PDFs, and embodiment-inventory checks.

### Limitations and license

First-version coverage focuses on rotationally symmetric sequential systems: fixed-focus or finite-conjugate lithography objectives, spherical surfaces, even aspheres, stops, image planes, wavelengths, aperture settings, field/object height, multi-configuration data, and common glass/material mappings.

Freeform, diffractive, tilted/decentered, catadioptric, and non-sequential systems are marked as out of scope unless a future version adds dedicated support.

The skill does not bypass CAPTCHA, paywalls, or access controls. If patent retrieval fails, provide the PDF or images directly. Automatic inference is allowed only when the original value, correction basis, confidence, and source evidence are recorded. Generated ZMX files are reconstruction artifacts, not a claim of exact equivalence to the original proprietary design.

The conversion code is released under the [MIT License](LICENSE). Third-party patent documents and figures are not relicensed by this repository.
