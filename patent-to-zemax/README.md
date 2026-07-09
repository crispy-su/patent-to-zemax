# Patent to Zemax Skill / 光学专利转 Zemax Skill

`patent-to-zemax` converts optical-design patents into audited Zemax OpticStudio sequential models. It is built for CN, US, JP, EP, and WO/PCT patent numbers, PDFs, scans, and extracted prescription tables, with dedicated handling for rotationally symmetric transmissive lithography objectives.

`patent-to-zemax` 用于把光学设计专利转换为可审计的 Zemax OpticStudio 顺序模式模型。它支持 CN、US、JP、EP、WO/PCT 专利号、PDF、扫描图片和已提取的处方表，重点覆盖旋转对称、纯透射式光刻物镜。

## What's new in the current version / 当前版本新增内容

- Keeps Zemax Clear Semi-Diameter automatic by default, instead of writing patent free-diameter values as fixed semi-diameters.
- 对 Zemax 的 Clear Semi-Diameter 默认保持 Automatic，不再把专利自由口径静默写成 fixed 半口径。

- Sets lithography aperture by object-space NA. For mask-to-wafer reduction objectives, the skill derives object-space NA from the patent image-side NA and magnification, typically `object NA = image NA / |reduction ratio|`.
- 光刻物镜按物方 NA 设置孔径。对于掩膜到晶圆的缩小投影物镜，通常按 `物方 NA = 像方 NA / |缩小倍率|` 从专利像方 NA 推导。

- Enables and verifies Real Ray Aiming through ZOS-API for high-NA finite-conjugate lithography systems.
- 通过 ZOS-API 打开并验证 Real Ray Aiming，适配高 NA 有限共轭光刻系统。

- Requires every numerical embodiment, example, or table in a patent to be modeled, or explicitly marked as unreconstructable with a reason.
- 要求专利中的每个数值实施例、example 或 table 都被建模；如果不能可靠复现，必须明确标记原因。

- Produces bilingual Chinese/English reconstruction reports.
- 输出中文/英文双语复现报告。

- Copies the original patent PDF into each output package so the ZMX, report, validation log, and source document stay together.
- 每个输出包都包含原专利 PDF，方便把 ZMX、报告、验证日志和来源文件一起审阅。

- Adds RMS spot diameter as a reference metric in reports. This value is reported for credibility review only; the pushed version does not perform optimization or optimization-eligibility gating.
- 在报告中增加 RMS 点列斑直径作为参考指标。该指标仅用于可信性审阅；当前推送版本不包含优化，也不判断是否应该优化。

- Improves ZOS-API validation for object-space materials, immersion declarations, missing glasses, non-finite automatic semi-diameters, and layout export.
- 改进 ZOS-API 验证：覆盖物方介质、浸没介质声明、玻璃缺失、非有限 automatic 半口径和 layout 导出问题。

- Adds an embodiment-inventory validator to catch patents where extra prescription tables were parsed but not modeled.
- 新增实施例清单校验器，用于发现“专利里还有数值表但没有建模”的遗漏。

## Outputs / 输出文件

For each reconstructable embodiment, the skill writes:

每个可复现实施例会输出：

- `.zmx` sequential Zemax file / Zemax 顺序模式文件
- `.prescription.json` normalized prescription and evidence file / 标准化处方与证据文件
- bilingual reconstruction report / 双语复现报告
- ZOS-API validation JSON/log / ZOS-API 验证日志
- ZOS-API exported layout image / ZOS-API 导出的镜头 layout 图
- copied source patent PDF / 原专利 PDF 副本

## Validation benchmarks / 验证基准

The current development validation includes representative public lithography-objective patents:

当前开发验证包含以下公开光刻物镜专利样例：

- `EP0770895A2` dry lithography objective benchmark.
- `US20030048547A1` lithography objective benchmark with ZOS-API validation artifacts.
- Additional user-directed rebuild set: `US5990926A`, `US6008884A`, `US6259508B1`, `US6788387B2`, and `US7023627B2`.

The five-patent rebuild produced 25 modeled numerical embodiments/tables with matching ZMX files, validation JSON files, exported layout images, bilingual reports, copied source PDFs, and embodiment-inventory checks.

五个专利的批量复现共生成 25 个数值实施例 / table，对应 ZMX、验证 JSON、layout 图、双语报告、原 PDF 副本，并通过实施例清单检查。

## Scope and limitations / 范围与限制

First-version coverage focuses on rotationally symmetric sequential transmissive systems: fixed-focus or finite-conjugate lithography objectives, spherical surfaces, even aspheres, stops, image planes, wavelengths, aperture settings, field/object height, multi-configuration data, and common glass/material mappings.

第一版重点覆盖旋转对称顺序系统：定焦或有限共轭光刻物镜、球面、偶次非球面、光阑、像面、波长、孔径、视场 / 物高、多配置数据和常见玻璃 / 材料映射。

Freeform, diffractive, tilted/decentered, catadioptric, and non-sequential systems are marked as out of scope unless a future version adds dedicated support.

自由曲面、衍射面、偏心 / 倾斜、折返式和非顺序系统目前会标记为超出范围，除非后续版本增加专门支持。

## Notes / 说明

- The skill does not bypass CAPTCHA, paywalls, or access controls. If patent retrieval fails, provide the PDF or images directly.
- 本 skill 不绕过验证码、付费墙或访问限制；如果联网获取失败，需要用户直接提供 PDF 或图片。

- Automatic inference is allowed only when the original value, correction basis, confidence, and source evidence are recorded.
- 允许自动推断，但必须记录原始值、修正依据、置信度和来源证据，禁止静默修正。

- Generated ZMX files are reconstruction artifacts, not a claim of exact equivalence to the original proprietary design.
- 生成的 ZMX 是复现工件，不声明与原始专利或商业设计完全等价。
