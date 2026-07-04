# Patent to Zemax Skill

将公开的光学设计专利转换为可审计的 Zemax OpticStudio 顺序模式模型。项目特别支持旋转对称、纯透射、干式光刻物镜，并保留“专利原文 → 标准化处方 → ZMX → ZOS-API 回读”的完整证据链。

## 功能

- 接受 CN、US、JP、EP、WO/PCT 专利号、PDF 或扫描图片。
- 输出处方 JSON、`.zmx`、验证日志、可信度报告和 ZOS-API layout。
- 使用物高定义掩膜视场，以专利像方 NA 为目标求解 Zemax `ObjectSpaceNA`。
- 强制 Real Ray Aiming、Robust Ray Aiming 和 Advanced Convergence。
- 区分原文抄录、确定性派生和推断值，禁止静默修正 OCR 或玻璃映射。
- 可准备包含原专利、最终报告和 ZMX 的 Outlook 邮件草稿；实际发送需要再次确认。

## 安装

将 `patent-to-zemax` 目录复制到个人 Codex skills 目录：

```powershell
Copy-Item -Recurse patent-to-zemax "$HOME\.codex\skills\patent-to-zemax"
```

需要 Windows、现代 Ansys Zemax OpticStudio、可用的 ZOS-API 许可证和 Python.NET。

## 使用

```text
使用 $patent-to-zemax 把专利 EP0770895A2 的所有实施例转换成 Zemax。
```

核心命令：

```powershell
python patent-to-zemax/scripts/build_lithography_zmx.py prescription.json --output output
python patent-to-zemax/scripts/export_zosapi_layout.py output/model.zmx --output output/layout.png
```

## 公开基准

`patent-to-zemax/validation/EP0770895A2` 保存 Nikon 公开专利第一实施例的端到端基准。该系统为 248.4 nm、纯折射、干式、掩膜到晶圆模型。最新 ZOS-API 回读通过以下检查：

- 54 个专利处方面和光阑位置；
- Object Height 视场与 0.25× 投影倍率；
- `ObjectSpaceNA`，实际像方 NA 0.6；
- Real + Robust Ray Aiming 与 Advanced Convergence；
- F_SILICA 材料、1000 mm 总长及 ZMX 保存后重开。

专利来源：[EP0770895A2](https://patents.google.com/patent/EP0770895A2/en)。专利原文及其中图表的权利归相应权利人；仓库中的转换代码采用 MIT 许可证。

## 限制

第一版不可靠恢复自由曲面、衍射面、偏心倾斜、非顺序系统或处方信息不完整的实施例。ZMX 成功打开只证明结构回读通过，不等同于专利级像差性能已经复现。

## License

MIT，见 [LICENSE](LICENSE)。第三方专利文件不因本许可证而重新授权。
