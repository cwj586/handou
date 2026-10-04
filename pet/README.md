# 憳豆桌面宠物

桌面上乱逛的憨豆先生（英伦滑稽绅士）。不是网页，是 WPF 桌面程序。

## 启动 / 退出

- 启动：双击桌面「憨豆」快捷方式（或直接运行 `bin\BeanPet.exe`；快捷方式由 `..\tools\make_shortcut.vbs` 生成）
- 退出：右键点击憨豆 → 退出

## 行为

| 触发 | 反应 |
|---|---|
| 左键点击憨豆 | 随机播放一次「被砸后转身」或「做鬼脸」 |
| 按住拖动 | 持续做鬼脸，松手落到鼠标位置（桌面任意位置，之后在该高度左右活动） |
| 双击憨豆 | 跑步或开车到**当前高度屏幕最右缘**驻留：原地待机（站立/原地走/原地跑/原地开车循环），不再左右移动 |
| 驻留中再次双击 | 解除驻留，恢复自由左右闲逛 |
| 右键憨豆 | 菜单：做鬼脸 / 跳舞 / 退出 |
| 闲逛 | 走路 / 跑步 / 开车 三选一，随机方向，各随机循环几轮 |
| 开车 | 上车 → 开车1/开车2 交叉（开车1概率65%）→ 快到屏幕边缘播放「转弯」并调头 → 下车 |
| 随机(18%) | 闲逛间歇自发跳舞：掏出泰迪 → 跳3-5轮 → 收回泰迪 |
| 5分钟没被点击 | 坐下 → 休息30秒-2分钟（呼吸循环）→ 起身 → 重新计时5分钟 |
| 休息中点击 | 起身后播放点击反应，回到闲逛 |

## 调参

改 `BeanPet.cs` 顶部 `Cfg` 类常量后重新编译：

- `WalkSpeed / RunSpeed / CarSpeed` 移动速度（物理像素/秒）
- `InactiveSecs` 无点击多久坐下（默认300）
- `RestMinSecs / RestMaxSecs` 休息时长范围
- `DanceChance` 自发跳舞概率

编译命令（bin 目录下运行）：

```
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /nologo /target:winexe /platform:anycpu /out:bin\BeanPet.exe ^
  /r:C:\Windows\Microsoft.NET\Framework64\v4.0.30319\WPF\PresentationCore.dll ^
  /r:C:\Windows\Microsoft.NET\Framework64\v4.0.30319\WPF\PresentationFramework.dll ^
  /r:C:\Windows\Microsoft.NET\Framework64\v4.0.30319\WPF\WindowsBase.dll ^
  /r:C:\Windows\Microsoft.NET\Framework64\v4.0.30319\System.Xaml.dll ^
  BeanPet.cs BeanFrames.g.cs
```

（在 pet 目录下运行时 out 路径写 `bin\BeanPet.exe`）

`bin\BeanPetTest.exe` 是快速验证版（12秒就坐下、休息6-8秒），用来测久坐循环，日常用 BeanPet.exe。

## 素材说明

- 帧数据在 `assets\frames\`，由 `..\tools\preprocess_bean.py` 从 `assets\sprites\char-d811f16e\frames\`（抽取片段）生成：
  裁剪透明边 → 人物按290px站高/汽车按310px车高归一 → LANCZOS ×1.25 放大 + 锐化。
- 「坐着吃零食」素材带不透明背景，未使用；休息循环用的是「坐下休息」的呼吸段（18-29帧往复）。
- 「起身」用的是「坐下休息」整段倒放（standup），因为 rise 素材与 sitdown 的人物/沙发比例互相矛盾。
- 贴地锚定：逐帧内容底边贴地面；hit、dance2 用常量锚（避免球/跳跃被钉地）。
- 运行日志：`bin\beanpet.log`。
