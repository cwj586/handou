// 憨豆桌面宠物 - WPF (C#5 / .NET Framework 4.x)
// 编译: csc /target:winexe /out:bin\BeanPet.exe /r:PresentationCore.dll /r:PresentationFramework.dll /r:WindowsBase.dll /r:System.Xaml.dll BeanPet.cs BeanFrames.g.cs
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Threading;

namespace BeanPet
{
    // ---- 可调参数 ----
    public static class Cfg
    {
        public const double WalkSpeed = 150;   // 物理像素/秒
        public const double RunSpeed = 380;
#if QUICK
        public const double CarSpeed = 540;
        public const int InactiveSecs = 12;    // 测试: 12秒无点击即坐下
        public const int RestMinSecs = 6;
        public const int RestMaxSecs = 8;
        public const double DanceChance = 0.0;
        public const int TurnCooldownUnits = 1;
#else
        public const double CarSpeed = 480;
        public const int InactiveSecs = 300;   // 5分钟无点击 -> 坐下
        public const int RestMinSecs = 30;
        public const int RestMaxSecs = 120;
        public const double DanceChance = 0.18; // 每次闲逛结束后随机跳舞概率
        public const int TurnCooldownUnits = 1; // 转弯后至少再开几个循环才允许再转
#endif
        public const double EdgeMarginPx = 46;  // 距屏幕边缘(物理px)触发转弯
        public const int DanceLoopsMin = 3, DanceLoopsMax = 5;
        public const int WalkLoopsMin = 2, WalkLoopsMax = 4;
        public const int RunLoopsMin = 2, RunLoopsMax = 4;
        public const int DriveUnitsMin = 3, DriveUnitsMax = 6;
    }

    public class BeanAction
    {
        string _name; string[] _files; int[] _w; int[] _h; float[] _cx; float[] _gy;
        List<BitmapSource> _frames; bool _loaded;

        public BeanAction(string name, string[] files, int[] w, int[] h, float[] cx, float[] gy)
        {
            _name = name; _files = files; _w = w; _h = h; _cx = cx; _gy = gy;
        }

        public string Name { get { return _name; } }
        public int Count { get { return _files.Length; } }

        public void EnsureLoaded(string baseDir)
        {
            if (_loaded) return;
            _frames = new List<BitmapSource>(_files.Length);
            foreach (string f in _files)
            {
                BitmapImage bi = new BitmapImage();
                bi.BeginInit();
                bi.CacheOption = BitmapCacheOption.OnLoad;
                bi.UriSource = new Uri(baseDir + f, UriKind.Relative);
                bi.EndInit();
                bi.Freeze();
                _frames.Add(bi);
            }
            _loaded = true;
        }

        public void Unload()
        {
            _frames = null; _loaded = false;
        }

        public BitmapSource Get(int i) { return _frames[i]; }
        public int Wi(int i) { return _w[i]; }
        public int Hi(int i) { return _h[i]; }
        public float Cxi(int i) { return _cx[i]; }
        public float Gyi(int i) { return _gy[i]; }
    }

    public enum Mode
    {
        Stand, Move, Drag, DriveEnter, DriveLoop, DriveTurn, DriveExit,
        DanceTake, DanceLoop, DancePut, React, SitDown, Rest, RestEnding, Standup
    }

    public class PetWindow : Window
    {
        string _baseDir = AppDomain.CurrentDomain.BaseDirectory + "assets\\frames\\";
        Dictionary<string, BeanAction> _map = new Dictionary<string, BeanAction>();
        List<BeanAction> _all;
        Image _img; Canvas _canvas;
        DispatcherTimer _timer; System.Diagnostics.Stopwatch _sw = new System.Diagnostics.Stopwatch();

        double _g = 1.0;          // dpi 缩放 (物理/逻辑)
        double _leftDip;          // 窗口逻辑X
        BeanAction _cur; int _frameIdx; bool _mirror;
        double _frameAcc; bool _needRender = true;

        Mode _mode; double _phaseTimer; int _loopsLeft; int _dir = 1; double _vx;
        int _driveUnits; int _turnCooldown; bool _reactQueued; bool _exitPending; bool _danceInterrupt;
        bool _edgeClear = true;
        double _exitZoom = 1.0;
        DateTime _lastClick; DateTime _lastStandUp;
        Random _rng = new Random();
        Action _afterReact; Action _menuQueued;
        bool _pinned; bool _pinTravel; bool _pinRequest;
        bool _dragMoved; Point _dragGrab;

        double WinWDip { get { return BeanFrames.WinW / _g; } }
        double WinHDip { get { return BeanFrames.WinH / _g; } }
        double GroundDip { get { return BeanFrames.WinH / _g - 26.0 / _g; } }
        double MinLeft { get { return 8; } }
        double MaxLeft { get { return SystemParameters.WorkArea.Width - WinWDip - 8; } }
        double GroundScreenDip { get { return SystemParameters.WorkArea.Bottom - 4; } }

        public PetWindow()
        {
            foreach (BeanAction a in BeanFrames.Build()) { _map[a.Name] = a; }
            _all = new List<BeanAction>(_map.Values);

            AllowsTransparency = true;
            WindowStyle = WindowStyle.None;
            Title = "BeanPet";
            Background = Brushes.Transparent;
            ShowInTaskbar = false;
            Topmost = true;
            ShowActivated = false;
            UseLayoutRounding = true;
            SnapsToDevicePixels = true;
            Left = 200; Top = 600;

            _canvas = new Canvas();
            _img = new Image();
            RenderOptions.SetBitmapScalingMode(_img, BitmapScalingMode.NearestNeighbor);
            _img.RenderTransformOrigin = new Point(0.5, 0.5);
            _img.RenderTransform = new ScaleTransform();
            _canvas.Children.Add(_img);
            Content = _canvas;

            ContextMenu menu = new ContextMenu();
            MenuItem miFace = new MenuItem(); miFace.Header = "做鬼脸";
            miFace.Click += delegate { QueueMenu(StartFace); };
            MenuItem miDance = new MenuItem(); miDance.Header = "跳舞";
            miDance.Click += delegate { QueueMenu(StartDance); };
            MenuItem miExit = new MenuItem(); miExit.Header = "退出";
            miExit.Click += delegate { Close(); };
            menu.Items.Add(miFace); menu.Items.Add(miDance); menu.Items.Add(miExit);
            ContextMenu = menu;

            MouseLeftButtonDown += OnPress;
            MouseMove += OnDragMove;
            MouseLeftButtonUp += OnRelease;
            LostMouseCapture += OnLostCapture;
            Loaded += delegate {
                PresentationSource ps = PresentationSource.FromVisual(this);
                if (ps != null) _g = ps.CompositionTarget.TransformToDevice.M11;
                Width = WinWDip; Height = WinHDip;
                Left = Snap(NewStartX()); _leftDip = Left;
                Top = Snap(GroundScreenDip - WinHDip);
                Play("stand", false);
                _mode = Mode.Stand; _phaseTimer = Rand(1.0, 2.0);
                _lastClick = DateTime.Now; _lastStandUp = DateTime.Now;
                _sw.Start();
                _timer = new DispatcherTimer(DispatcherPriority.Render);
                _timer.Interval = TimeSpan.FromMilliseconds(15);
                _timer.Tick += OnTick;
                _timer.Start();
                Log("started pid=" + System.Diagnostics.Process.GetCurrentProcess().Id
                    + " dpi=" + _g.ToString("F2", CultureInfo.InvariantCulture));
            };
        }

        double Snap(double v) { return Math.Round(v * _g) / _g; }
        double Rand(double a, double b) { return a + _rng.NextDouble() * (b - a); }
        int RandInt(int a, int b) { return _rng.Next(a, b + 1); }

        double NewStartX()
        {
            double w = MaxLeft - MinLeft;
            return MinLeft + w * (0.25 + 0.5 * _rng.NextDouble());
        }

        void Log(string s)
        {
            try
            {
                File.AppendAllText(AppDomain.CurrentDomain.BaseDirectory + "beanpet.log",
                    DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + " " + s + "\r\n");
            }
            catch { }
        }

        void Play(string name, bool mirror)
        {
            BeanAction a;
            if (!_map.TryGetValue(name, out a)) { Log("missing action " + name); return; }
            _cur = a; _frameIdx = 0; _frameAcc = 0; _mirror = mirror; _needRender = true;
            a.EnsureLoaded(_baseDir);
            TrimCache();
        }

        void TrimCache()
        {
            int live = 0;
            foreach (BeanAction a in _all) if (a != _cur && a.Name != "stand") live++;
            if (live <= 3) return;
            foreach (BeanAction a in _all)
            {
                if (a != _cur && a.Name != "stand" && a.Name != "sitdown" && a.Name != "rest" && a.Name != "standup")
                {
                    a.Unload(); live--;
                    if (live <= 3) break;
                }
            }
        }

        // ---------- 状态机 ----------
        void SetPhase(Mode m, string log)
        {
            _mode = m;
            Log(log);
        }

        void StartStand(double secs)
        {
            _vx = 0;
            Play("stand", _dir < 0);
            _phaseTimer = secs;
            SetPhase(Mode.Stand, "stand " + secs.ToString("F1", CultureInfo.InvariantCulture) + "s");
        }

        void ChooseNext()
        {
            if (_pinRequest) { StartGoRight(); return; }
            if ((DateTime.Now - _lastClick).TotalSeconds >= Cfg.InactiveSecs) { StartSitCycle(); return; }
            if (_pinned) { ChoosePinnedIdle(); return; }
            if (_rng.NextDouble() < Cfg.DanceChance) { StartDance(); return; }
            int roll = _rng.Next(3);
            if (roll == 0) StartBout("walk", Cfg.WalkSpeed, RandInt(Cfg.WalkLoopsMin, Cfg.WalkLoopsMax));
            else if (roll == 1) StartBout("run", Cfg.RunSpeed, RandInt(Cfg.RunLoopsMin, Cfg.RunLoopsMax));
            else StartDrive();
        }

        void PickDir()
        {
            double openL = _leftDip - MinLeft, openR = MaxLeft - _leftDip;
            if (Math.Abs(openR - openL) < 100) _dir = _rng.Next(2) == 0 ? 1 : -1;
            else _dir = openR > openL ? 1 : -1;
        }

        void StartBout(string act, double speed, int loops)
        {
            PickDir();
            _loopsLeft = loops;
            _vx = speed * _dir;
            Play(act, _dir < 0);
            SetPhase(Mode.Move, act + " dir=" + _dir + " loops=" + loops);
        }

        void StartDrive()
        {
            PickDir();
            _reactQueued = false; _exitPending = false; _turnCooldown = 0;
            _vx = 0;
            Play("enter", _dir < 0);
            SetPhase(Mode.DriveEnter, "enter dir=" + _dir);
        }

        void StartDriveLoop(int units)
        {
            _driveUnits = units;
            PlayDriveClip();
            _vx = _pinned ? 0 : Cfg.CarSpeed * _dir;
            SetPhase(Mode.DriveLoop, "drive units=" + units + (_pinned ? " (in place)" : ""));
        }

        void PlayDriveClip()
        {
            Play(_rng.NextDouble() < 0.65 ? "drive1" : "drive2", _dir < 0);
        }

        void StartTurn()
        {
            _vx = 0;
            // turn 原生: 朝右->朝左。向右行进撞右缘: 原生; 向左行进撞左缘: 镜像
            Play("turn", _dir < 0);
            SetPhase(Mode.DriveTurn, "turn from dir=" + _dir);
        }

        void StartDance()
        {
            _vx = 0;
            _reactQueued = false; _danceInterrupt = false;
            Play("takeout", false);
            SetPhase(Mode.DanceTake, "dance takeout");
        }

        void StartReact()
        {
            _vx = 0;
            bool hit = _rng.Next(2) == 0;
            Play(hit ? "hit" : "face", _dir < 0);
            SetPhase(Mode.React, "react " + (hit ? "hit" : "face"));
        }

        void StartFace()
        {
            _vx = 0;
            Play("face", _dir < 0);
            SetPhase(Mode.React, "face (menu)");
        }

        // ---------- 右缘驻留 (双击触发) ----------
        void ChoosePinnedIdle()
        {
            int roll = _rng.Next(4);
            if (roll == 0) { StartStand(Rand(2.0, 5.0)); return; }
            if (roll == 1) { StartBout("walk", 0, RandInt(Cfg.WalkLoopsMin, Cfg.WalkLoopsMax)); return; }
            if (roll == 2) { StartBout("run", 0, RandInt(Cfg.RunLoopsMin, Cfg.RunLoopsMax)); return; }
            StartDriveInPlace();
        }

        void StartDriveInPlace()
        {
            _dir = -1;
            _reactQueued = false; _exitPending = false; _turnCooldown = 0;
            _vx = 0;
            Play("enter", true);
            SetPhase(Mode.DriveEnter, "enter in place (pinned)");
        }

        void StartGoRight()
        {
            _pinRequest = false; _pinTravel = true; _pinned = false;
            _exitPending = false; _danceInterrupt = false;
            Log("go right edge y=" + ((int)Top));
            if (_mode == Mode.DriveLoop)
            {
                if (_dir < 0) StartTurn();
                else _vx = Cfg.CarSpeed;
                return;
            }
            _dir = 1;
            _loopsLeft = 1000000;
            _vx = Cfg.RunSpeed;
            Play("run", false);
            SetPhase(Mode.Move, "run -> right edge");
        }

        void ArrivePin()
        {
            _vx = 0;
            _pinTravel = false; _pinRequest = false;
            _pinned = true;
            _edgeClear = true; _turnCooldown = 0;
            Log("pinned at right edge y=" + ((int)Top));
            if (_mode == Mode.DriveLoop) StartExit();
            else StartStand(Rand(0.8, 1.6));
        }

        void Unpin()
        {
            _pinned = false; _pinRequest = false; _pinTravel = false;
            Log("unpin -> free roam");
            if (_mode == Mode.DriveLoop)
            {
                _dir = -1; _turnCooldown = 1; _edgeClear = false;
                _vx = -Cfg.CarSpeed;
                PlayDriveClip();
            }
            else if (_mode == Mode.DriveEnter)
            {
                _dir = -1; _turnCooldown = 1; _edgeClear = false;
            }
            else
            {
                StartStand(Rand(0.4, 0.8));
            }
        }

        // ---------- 右键菜单动作 ----------
        void QueueMenu(Action a)
        {
            if (_mode == Mode.Drag) return;
            Log("menu action queued mode=" + _mode);
            switch (_mode)
            {
                case Mode.DriveLoop:
                    _menuQueued = a; _reactQueued = false; _exitPending = true;
                    return;
                case Mode.DanceLoop:
                    _menuQueued = a; _danceInterrupt = true;
                    return;
                case Mode.Rest:
                case Mode.RestEnding:
                    _menuQueued = a; _reactQueued = true;
                    if (_mode == Mode.Rest) _mode = Mode.RestEnding;
                    return;
                case Mode.DanceTake:
                case Mode.SitDown:
                case Mode.DriveEnter:
                    _menuQueued = a;
                    return;
                default:
                    a();
                    return;
            }
        }

        void StartSitCycle()
        {
            _vx = 0;
            _reactQueued = false;
            Play("sitdown", false);
            SetPhase(Mode.SitDown, "sitdown (inactive "
                + ((int)(DateTime.Now - _lastClick).TotalSeconds) + "s)");
        }

        void StartRest()
        {
            double secs = Rand(Cfg.RestMinSecs, Cfg.RestMaxSecs);
            Play("rest", false);
            _phaseTimer = secs;
            SetPhase(Mode.Rest, "rest " + ((int)secs) + "s");
        }

        void AfterReact(Action next) { _afterReact = next; }

        // ---------- 帧推进 ----------
        void AdvanceFrame()
        {
            if (_cur == null) return;
            _frameIdx++;
            if (_frameIdx < _cur.Count) { _needRender = true; return; }
            _frameIdx = 0; _needRender = true;
            OnLoopEnd();
        }

        void OnLoopEnd()
        {
            switch (_mode)
            {
                case Mode.Stand:
                    break; // 由计时器驱动
                case Mode.Drag:
                    break; // 拖拽中: face 自动循环
                case Mode.Move:
                    if (_pinRequest && !_pinTravel) { StartGoRight(); break; }
                    _loopsLeft--;
                    if (_loopsLeft <= 0) { StartStand(Rand(1.2, 3.2)); }
                    else Play(_cur.Name, _dir < 0);
                    break;
                case Mode.DriveEnter:
                    StartDriveLoop(RandInt(Cfg.DriveUnitsMin, Cfg.DriveUnitsMax));
                    break;
                case Mode.DriveLoop:
                    _turnCooldown--;
                    if (_exitPending) { StartExit(); break; }
                    _driveUnits--;
                    if (_driveUnits <= 0) { StartExit(); break; }
                    PlayDriveClip();
                    break;
                case Mode.DriveTurn:
                    _dir = -_dir;
                    _turnCooldown = Cfg.TurnCooldownUnits;
                    _edgeClear = false;
                    _vx = _pinned ? 0 : Cfg.CarSpeed * _dir;
                    _mode = Mode.DriveLoop;
                    PlayDriveClip();
                    if (_pinRequest) { _pinRequest = false; _pinTravel = true; }
                    Log("drove turn now dir=" + _dir);
                    break;
                case Mode.DriveExit:
                    if (_menuQueued != null) { Action mq = _menuQueued; _menuQueued = null; mq(); break; }
                    if (_pinRequest) { StartGoRight(); break; }
                    if (_reactQueued) { _reactQueued = false; StartReact(); break; }
                    StartStand(Rand(0.8, 2.0));
                    break;
                case Mode.DanceTake:
                    _loopsLeft = RandInt(Cfg.DanceLoopsMin, Cfg.DanceLoopsMax);
                    _mode = Mode.DanceLoop;
                    PlayDanceClip();
                    Log("dance loops=" + _loopsLeft);
                    break;
                case Mode.DanceLoop:
                    _loopsLeft--;
                    if (_loopsLeft <= 0 || _danceInterrupt || _menuQueued != null || _pinRequest)
                    {
                        _danceInterrupt = false;
                        Play("putaway", false);
                        SetPhase(Mode.DancePut, "dance putaway");
                    }
                    else PlayDanceClip();
                    break;
                case Mode.DancePut:
                    if (_menuQueued != null) { Action mp = _menuQueued; _menuQueued = null; mp(); break; }
                    if (_pinRequest) { StartGoRight(); break; }
                    if (_reactQueued) { _reactQueued = false; StartReact(); break; }
                    StartStand(Rand(1.0, 2.5));
                    break;
                case Mode.React:
                    if (_afterReact != null) { Action n = _afterReact; _afterReact = null; n(); break; }
                    if (_menuQueued != null) { Action mr = _menuQueued; _menuQueued = null; mr(); break; }
                    if (_pinRequest) { StartGoRight(); break; }
                    StartStand(Rand(1.0, 2.5));
                    break;
                case Mode.SitDown:
                    if (_menuQueued != null || _pinRequest)
                    {
                        Play("standup", false);
                        SetPhase(Mode.Standup, "standup (interrupt)");
                        break;
                    }
                    StartRest();
                    break;
                case Mode.RestEnding:
                    Play("standup", false);
                    SetPhase(Mode.Standup, "standup");
                    break;
                case Mode.Standup:
                    _lastClick = DateTime.Now; _lastStandUp = DateTime.Now;
                    Log("cycle done, next sit at " + Cfg.InactiveSecs + "s idle");
                    if (_menuQueued != null) { Action ms = _menuQueued; _menuQueued = null; ms(); break; }
                    if (_pinRequest) { StartGoRight(); break; }
                    if (_reactQueued) { _reactQueued = false; StartReact(); break; }
                    StartStand(Rand(0.6, 1.6));
                    break;
            }
        }

        void PlayDanceClip()
        {
            Play(_rng.Next(2) == 0 ? "dance1" : "dance2", false);
        }

        void StartExit()
        {
            _vx = 0;
            _exitZoom = BeanFrames.ExitZoom;   // 开车段车大 -> 下车段车小，前8帧渐变
            Play("exitcar", _dir < 0);
            SetPhase(Mode.DriveExit, "exitcar");
        }

        // ---------- 每帧 ----------
        void OnTick(object sender, EventArgs e)
        {
            double dt = _sw.Elapsed.TotalSeconds;
            _sw.Restart();
            if (dt > 0.25) dt = 0.25;

            _frameAcc += dt;
            double fd = 1.0 / BeanFrames.Fps;
            while (_frameAcc >= fd) { _frameAcc -= fd; AdvanceFrame(); }

            StepPhase(dt);
            Move(dt);
            IdleCheck();

            if (_needRender && _cur != null) Render();
        }

        void StepPhase(double dt)
        {
            switch (_mode)
            {
                case Mode.Stand:
                    _phaseTimer -= dt;
                    if (_phaseTimer <= 0) ChooseNext();
                    break;
                case Mode.Rest:
                    _phaseTimer -= dt;
                    if (_phaseTimer <= 0) _mode = Mode.RestEnding;
                    break;
                case Mode.RestEnding:
                    // 等 rest 正向段播到源帧29(rest列表idx 11)再起身
                    if (_cur != null && _cur.Name == "rest" && _frameIdx == 11) OnLoopEnd();
                    break;
                case Mode.DriveLoop:
                    if (!_edgeClear && !NearEdge()) _edgeClear = true;
                    if (_vx != 0 && NearEdge() && _edgeClear && _turnCooldown <= 0 && _driveUnits > 1) StartTurn();
                    break;
            }
        }

        bool NearEdge()
        {
            return _leftDip <= MinLeft + Cfg.EdgeMarginPx / _g
                || _leftDip >= MaxLeft - Cfg.EdgeMarginPx / _g;
        }

        void Move(double dt)
        {
            if (_vx == 0) return;
            double nx = _leftDip + _vx * dt / _g;
            if (nx < MinLeft) { nx = MinLeft; OnHitEdge(); }
            else if (nx > MaxLeft) { nx = MaxLeft; OnHitEdge(); }
            _leftDip = nx;
            Left = Snap(nx);
        }

        void OnHitEdge()
        {
            if (_mode == Mode.Move)
            {
                if (_pinTravel && _dir > 0) { ArrivePin(); return; }
                _dir = -_dir; _vx = Math.Abs(_vx) * _dir;
                _mirror = _dir < 0;
                Log("bout bounce dir=" + _dir);
            }
            else if (_mode == Mode.DriveLoop)
            {
                if (_pinTravel) { if (_dir > 0) ArrivePin(); else StartTurn(); return; }
                if (_turnCooldown > 0 && _edgeClear)
                {
                    // 冷却中撞墙: 掉头但不算转弯动作
                    _dir = -_dir; _vx = Math.Abs(_vx) * _dir;
                    _edgeClear = false;
                    Log("drive clamp bounce dir=" + _dir);
                }
            }
        }

        void IdleCheck()
        {
            // 空闲计时在 ChooseNext / 走停时统一判断, 这里只处理移动中到点的情况:
            if (_mode == Mode.Move && (DateTime.Now - _lastClick).TotalSeconds >= Cfg.InactiveSecs)
            {
                StartSitCycle();
            }
        }

        void Render()
        {
            int i = _frameIdx;
            // exitcar 前8帧：车从开车段尺寸平滑渐变到下车段尺寸（模拟刹车沉降）
            double eff = 1.0;
            if (_exitZoom > 1.0 && _cur != null && _cur.Name == "exitcar")
            {
                double t = i >= 8 ? 1.0 : i / 8.0;
                eff = _exitZoom + (1.0 - _exitZoom) * t;
                if (i >= 8) _exitZoom = 1.0;
            }
            _img.Source = _cur.Get(i);
            _img.Width = _cur.Wi(i) * eff / _g;
            _img.Height = _cur.Hi(i) * eff / _g;
            ((ScaleTransform)_img.RenderTransform).ScaleX = _mirror ? -1 : 1;
            double cx = _cur.Cxi(i);
            if (_mirror) cx = _cur.Wi(i) - cx;
            Canvas.SetLeft(_img, Snap(WinWDip / 2.0 - cx * eff / _g));
            Canvas.SetTop(_img, Snap(GroundDip - _cur.Gyi(i) * eff / _g));
            _needRender = false;
        }

        // ---------- 交互 ----------
        void OnPress(object sender, MouseButtonEventArgs e)
        {
            _lastClick = DateTime.Now;
            Point p = e.GetPosition(this);
            _dragGrab = p;
            _dragMoved = false;
            CaptureMouse();
            if (e.ClickCount >= 2) { OnDoubleClickAction(); return; }
            Log("click mode=" + _mode);
            ClickReact();
        }

        void ClickReact()
        {
            switch (_mode)
            {
                case Mode.Stand:
                case Mode.Move:
                    StartReact();
                    break;
                case Mode.Rest:
                    _mode = Mode.RestEnding;
                    _reactQueued = true;
                    break;
                case Mode.RestEnding:
                    _reactQueued = true;
                    break;
                case Mode.DriveLoop:
                    _reactQueued = true; _exitPending = true;
                    break;
                case Mode.DanceLoop:
                    _reactQueued = true; _danceInterrupt = true;
                    break;
                default:
                    break; // 过渡动作期间忽略
            }
        }

        void OnDoubleClickAction()
        {
            if (_mode == Mode.Drag || _dragMoved) return;
            if (_pinTravel) return;
            if (_pinned) { Unpin(); return; }
            RequestPin();
        }

        void RequestPin()
        {
            Log("dblclick pin request mode=" + _mode);
            switch (_mode)
            {
                case Mode.Stand:
                case Mode.Move:
                case Mode.DriveLoop:
                    StartGoRight();
                    break;
                case Mode.DriveEnter:
                    _pinTravel = true;
                    break;
                case Mode.Rest:
                case Mode.RestEnding:
                    _pinRequest = true;
                    if (_mode == Mode.Rest) _mode = Mode.RestEnding;
                    break;
                case Mode.DanceLoop:
                    _pinRequest = true; _danceInterrupt = true;
                    break;
                default:
                    _pinRequest = true; // 收尾动作结束时接管
                    break;
            }
        }

        // ---------- 拖动 ----------
        void OnDragMove(object sender, MouseEventArgs e)
        {
            if (Mouse.LeftButton != MouseButtonState.Pressed) return;
            if (!_dragMoved)
            {
                if (Mouse.Captured != this) return;
                Point p0 = e.GetPosition(this);
                if (Math.Abs(p0.X - _dragGrab.X) < SystemParameters.MinimumHorizontalDragDistance
                    && Math.Abs(p0.Y - _dragGrab.Y) < SystemParameters.MinimumVerticalDragDistance) return;
                BeginDrag();
            }
            Point p = e.GetPosition(this);
            double nl = Left + (p.X - _dragGrab.X);
            double nt = Top + (p.Y - _dragGrab.Y);
            nl = Math.Max(MinLeft, Math.Min(MaxLeft, nl));
            nt = Math.Max(0, Math.Min(SystemParameters.WorkArea.Bottom - 60, nt));
            Left = Snap(nl); _leftDip = Left;
            Top = Snap(nt);
        }

        void BeginDrag()
        {
            _dragMoved = true;
            bool wasPinned = _pinned || _pinTravel;
            _pinned = false; _pinTravel = false; _pinRequest = false;
            _reactQueued = false; _exitPending = false; _danceInterrupt = false;
            _menuQueued = null; _afterReact = null;
            _vx = 0;
            Play("face", false);
            SetPhase(Mode.Drag, "drag start" + (wasPinned ? " (pin cancelled)" : ""));
        }

        void OnRelease(object sender, MouseButtonEventArgs e)
        {
            if (IsMouseCaptured) ReleaseMouseCapture();
            if (_dragMoved) EndDrag();
        }

        void OnLostCapture(object sender, MouseEventArgs e)
        {
            if (_dragMoved) EndDrag();
        }

        void EndDrag()
        {
            _dragMoved = false;
            _leftDip = Math.Max(MinLeft, Math.Min(MaxLeft, Left));
            Left = Snap(_leftDip);
            _lastClick = DateTime.Now;
            Log("dropped at " + ((int)_leftDip) + "," + ((int)Top));
            StartStand(Rand(0.8, 1.8));
        }

        protected override void OnClosed(EventArgs e)
        {
            if (_timer != null) _timer.Stop();
            base.OnClosed(e);
            Application.Current.Shutdown();
        }
    }

    public class App : Application
    {
        [STAThread]
        public static void Main()
        {
            App a = new App();
            PetWindow w = new PetWindow();
            w.Show();
            a.Run(w);
        }
    }
}
