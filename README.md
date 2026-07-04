# Patent to Zemax Skill

[中文](#中文说明) | [English](#english)

## 中文说明

这是由 Codex 自主开发的 Skill，可将公开的光学设计专利转换为可审计的 Zemax OpticStudio 顺序模式模型。目前已测试较复杂的光学系统，包括纯透射光刻物镜，并保留“专利原文 → 标准化处方 → ZMX → ZOS-API 回读”的完整证据链。

### 功能

- 接受 CN、US、JP、EP、WO/PCT 专利号、PDF 或扫描图片。
- 输出处方 JSON、`.zmx`、验证日志、可信度报告和 ZOS-API layout。
- 使用物高定义掩膜视场，以专利像方 NA 为目标求解 Zemax `ObjectSpaceNA`。
- 强制 Real Ray Aiming、Robust Ray Aiming 和 Advanced Convergence。
- 区分原文抄录、确定性派生和推断值，禁止静默修正 OCR 或玻璃映射。
- 可准备包含原专利、最终报告和 ZMX 的 Outlook 邮件草稿；实际发送需要再次确认。

### 安装与使用

将 `patent-to-zemax` 目录复制到个人 Codex skills 目录：

```powershell
Copy-Item -Recurse patent-to-zemax "$HOME\.codex\skills\patent-to-zemax"
```

需要 Windows、现代 Ansys Zemax OpticStudio、可用的 ZOS-API 许可证和 Python.NET。

```text
使用 $patent-to-zemax 把专利 EP0770895A2 的所有实施例转换成 Zemax。
```

```powershell
python patent-to-zemax/scripts/build_lithography_zmx.py prescription.json --output output
python patent-to-zemax/scripts/export_zosapi_layout.py output/model.zmx --output output/layout.png
```

### 公开基准

| 专利 | 权利人 | 波长 | 模型 | ZOS-API 验证 |
|---|---|---:|---|---|
| [EP0770895A2](https://patents.google.com/patent/EP0770895A2/en) | Nikon | 248.4 nm | 纯折射、干式、0.25×、54 个处方面 | 通过：像方 NA 0.6、ObjectSpaceNA、Robust Real Ray Aiming |
| [US20030048547A1](https://patents.google.com/patent/US20030048547A1/en) | Carl Zeiss SMT | 193.304 nm | 纯折射、Table 3、63 个处方面 | 通过：像方 NA 0.75、ObjectSpaceNA、Robust Real Ray Aiming |

两个目录均包含原专利 PDF、标准化处方、ZMX、ZOS-API 回读日志、专利图、API layout 和对比图。目前 193 nm 样例的结构复现结果更完整，处方、倍率、NA、材料和总长均通过验证；专利级像差等价仍标记为未验证。

### 限制与许可

第一版不可靠恢复自由曲面、衍射面、偏心倾斜、非顺序系统或处方信息不完整的实施例。转换代码采用 [MIT License](LICENSE)；第三方专利文件及其中图表不因本许可证而重新授权。

## English

This Codex-developed skill converts published optical-design patents into auditable Zemax OpticStudio sequential models. It has been tested on complex optical systems, including all-transmissive lithography objectives, while preserving a traceable chain from the patent source to a normalized prescription, ZMX model, and ZOS-API round-trip validation.

### Features

- Accepts CN, US, JP, EP, and WO/PCT patent numbers, PDFs, and scanned images.
- Produces prescription JSON, `.zmx`, validation logs, confidence reports, and ZOS-API layouts.
- Represents the mask field as object height and solves Zemax `ObjectSpaceNA` against the patent image-side NA.
- Enforces Real Ray Aiming, Robust Ray Aiming, and Advanced Convergence.
- Separates copied, deterministically derived, and inferred values; OCR corrections and glass mappings are never silent.
- Can prepare an Outlook draft containing the original patent, final report, and ZMX. Sending remains a separately confirmed action.

### Installation and usage

Copy the `patent-to-zemax` directory into your personal Codex skills directory:

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

### Public benchmarks

| Patent | Assignee | Wavelength | Model | ZOS-API validation |
|---|---|---:|---|---|
| [EP0770895A2](https://patents.google.com/patent/EP0770895A2/en) | Nikon | 248.4 nm | All-refractive, dry, 0.25×, 54 prescription surfaces | Passed: image-side NA 0.6, ObjectSpaceNA, Robust Real Ray Aiming |
| [US20030048547A1](https://patents.google.com/patent/US20030048547A1/en) | Carl Zeiss SMT | 193.304 nm | All-refractive, Table 3, 63 prescription surfaces | Passed: image-side NA 0.75, ObjectSpaceNA, Robust Real Ray Aiming |

Both benchmark directories include the source patent PDF, normalized prescription, ZMX, ZOS-API round-trip log, patent figure, API layout, and side-by-side comparison. The 193 nm case currently has the more complete structural reconstruction: prescription, magnification, NA, materials, and total track all pass validation. Patent-level aberration equivalence remains explicitly unverified.

### Limitations and license

The first release does not reliably reconstruct freeform, diffractive, decentered/tilted, non-sequential, or incomplete prescriptions. The conversion code is released under the [MIT License](LICENSE). Third-party patent documents and figures are not relicensed by this repository.
