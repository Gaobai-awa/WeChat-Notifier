"""
WeChat Notifier - Reads CipherTalk messages, shows Windows toast notifications.
Auto-generates config.json on first run. Supports zh_cn / zh_tw / en_us.
"""
import urllib.request, json, time, subprocess, os, sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, 'config.json')
AUMID = 'WeChat'
SEP = ' / '

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ── i18n ──────────────────────────────────────────────────
T = {
    'zh_cn': {
        'banner': 'WeChat Notifier (Toast)',
        'target': '监听',
        'check': '进程检查间隔',
        'notify': '消息轮询间隔',
        'fetch_limit': '每次拉取消息数',
        'show_self': '显示自己发的消息',
        'autostart': '开机自启动',
        'language': '界面语言 (zh_cn / zh_tw / en_us)',
        'api_base': 'API 地址',
        'wechat_proc': '微信进程名',
        'ctalk_proc': 'CipherTalk 进程名',
        'no_user': '未配置有效的 session_id！请编辑 config.json。',
        'exit_soon': '程序将在 10 秒后退出...',
        'created': '已创建 config.json 模板，请编辑。',
        'parse_error': 'config.json 解析失败',
        'autostart_on': '开机自启: 已启用',
        'autostart_off': '开机自启: 已禁用',
        'started': '已启动',
        'ready': '已就绪',
        'disconnected': '连接断开',
        'wechat_dead': '微信未运行',
        'ctalk_dead': 'CipherTalk 未运行',
        'wechat_closed': '微信已关闭',
        'ctalk_closed': 'CipherTalk 已关闭',
        'dead': '未运行',
        'closed': '已关闭',
        'check_mode': '检查模式',
        'stop': '已停止',
        'msg_image': '[图片]',
        'msg_video': '[视频]',
        'msg_voice': '[语音]',
        'msg_transfer': '[转账]',
        'msg_app': '[应用]',
        'msg_quote': '[引用]',
        'msg_file': '[文件]',
        'label_app': 'app',
        'label_quote': 'quote',
        'label_quote_prefix': '[引用消息]',
        'state_title': '状态',
        'config_comment_users': '监听的用户列表（可添加多个）',
        'config_comment_interval': '进程检查间隔（秒）',
        'config_comment_notify': '消息轮询间隔（秒）',
        'config_comment_limit': '每次拉取消息数',
        'config_comment_self': '是否显示自己发的消息',
        'config_comment_autostart': '开机自启动',
        'config_comment_lang': '界面语言 (zh_cn / zh_tw / en_us)',
        'config_comment_api': 'API 地址（一般不改）',
        'config_comment_wp': '微信进程名（一般不改）',
        'config_comment_cp': 'CipherTalk 进程名（一般不改）',
        'placeholder_name': '昵称',
        'placeholder_id': 'wxid_xxxxxxxxxxxx',
    },
    'zh_tw': {
        'banner': 'WeChat Notifier (Toast)',
        'target': '監聽',
        'check': '處理程序檢查間隔',
        'notify': '訊息輪詢間隔',
        'fetch_limit': '每次拉取訊息數',
        'show_self': '顯示自己發的訊息',
        'autostart': '開機自動啟動',
        'language': '介面語言 (zh_cn / zh_tw / en_us)',
        'api_base': 'API 位址',
        'wechat_proc': '微信處理程序名',
        'ctalk_proc': 'CipherTalk 處理程序名',
        'no_user': '未設定有效的 session_id！請編輯 config.json。',
        'exit_soon': '程式將在 10 秒後退出...',
        'created': '已建立 config.json 模板，請編輯。',
        'parse_error': 'config.json 解析失敗',
        'autostart_on': '開機自啟: 已啟用',
        'autostart_off': '開機自啟: 已禁用',
        'started': '已啟動',
        'ready': '已就緒',
        'disconnected': '連線中斷',
        'wechat_dead': '微信未執行',
        'ctalk_dead': 'CipherTalk 未執行',
        'wechat_closed': '微信已關閉',
        'ctalk_closed': 'CipherTalk 已關閉',
        'dead': '未執行',
        'closed': '已關閉',
        'check_mode': '檢查模式',
        'stop': '已停止',
        'msg_image': '[圖片]',
        'msg_video': '[影片]',
        'msg_voice': '[語音]',
        'msg_transfer': '[轉帳]',
        'msg_app': '[應用]',
        'msg_quote': '[引用]',
        'msg_file': '[檔案]',
        'label_app': 'app',
        'label_quote': 'quote',
        'label_quote_prefix': '[引用訊息]',
        'state_title': '狀態',
        'config_comment_users': '監聽的使用者列表（可添加多個）',
        'config_comment_interval': '處理程序檢查間隔（秒）',
        'config_comment_notify': '訊息輪詢間隔（秒）',
        'config_comment_limit': '每次拉取訊息數',
        'config_comment_self': '是否顯示自己發的訊息',
        'config_comment_autostart': '開機自動啟動',
        'config_comment_lang': '介面語言 (zh_cn / zh_tw / en_us)',
        'config_comment_api': 'API 位址（一般不改）',
        'config_comment_wp': '微信處理程序名（一般不改）',
        'config_comment_cp': 'CipherTalk 處理程序名（一般不改）',
        'placeholder_name': '暱稱',
        'placeholder_id': 'wxid_xxxxxxxxxxxx',
    },
    'en_us': {
        'banner': 'WeChat Notifier (Toast)',
        'target': 'target',
        'check': 'check interval',
        'notify': 'notify interval',
        'fetch_limit': 'fetch limit',
        'show_self': 'show self messages',
        'autostart': 'autostart',
        'language': 'language (zh_cn / zh_tw / en_us)',
        'api_base': 'API base URL',
        'wechat_proc': 'WeChat process',
        'ctalk_proc': 'CipherTalk process',
        'no_user': 'No valid session_id configured! Edit config.json.',
        'exit_soon': 'Exiting in 10 seconds...',
        'created': 'Created config.json template. Please edit it.',
        'parse_error': 'config.json parse error',
        'autostart_on': 'autostart: enabled',
        'autostart_off': 'autostart: disabled',
        'started': 'started',
        'ready': 'ready',
        'disconnected': 'disconnected',
        'wechat_dead': 'WeChat dead',
        'ctalk_dead': 'CTalk dead',
        'wechat_closed': 'WeChat closed',
        'ctalk_closed': 'CTalk closed',
        'dead': 'dead',
        'closed': 'closed',
        'check_mode': 'check mode',
        'stop': 'stopped',
        'msg_image': '[image]',
        'msg_video': '[video]',
        'msg_voice': '[voice]',
        'msg_transfer': '[transfer]',
        'msg_app': '[app]',
        'msg_quote': '[quote]',
        'msg_file': '[file]',
        'label_app': 'app',
        'label_quote': 'quote',
        'label_quote_prefix': '[Quote]',
        'state_title': 'state',
        'config_comment_users': 'Users to monitor (add multiple)',
        'config_comment_interval': 'Process check interval (seconds)',
        'config_comment_notify': 'Message poll interval (seconds)',
        'config_comment_limit': 'Messages per fetch',
        'config_comment_self': 'Show notifications for own messages',
        'config_comment_autostart': 'Start with Windows',
        'config_comment_lang': 'Language (zh_cn / zh_tw / en_us)',
        'config_comment_api': 'API base URL (usually unchanged)',
        'config_comment_wp': 'WeChat process name (usually unchanged)',
        'config_comment_cp': 'CipherTalk process name (usually unchanged)',
        'placeholder_name': 'Name',
        'placeholder_id': 'wxid_xxxxxxxxxxxx',
    },
}

def t(key, lang=None):
    if lang is None:
        lang = CFG.get('language', 'zh_cn')
    return T.get(lang, T['en_us']).get(key, key)

# ── config ────────────────────────────────────────────────
def _config_template(lang):
    tpl = T.get(lang, T['en_us'])
    return f"""{{
  // {tpl['config_comment_users']}
  "users": [
    {{ "session_id": "{tpl['placeholder_id']}", "display_name": "{tpl['placeholder_name']}" }}
  ],
  // {tpl['config_comment_interval']}
  "check_interval": 120,
  // {tpl['config_comment_notify']}
  "notify_interval": 10,
  // {tpl['config_comment_limit']}
  "fetch_limit": 5,
  // {tpl['config_comment_self']}
  "show_self": false,
  // {tpl['config_comment_autostart']}
  "autostart": false,
  // {tpl['config_comment_lang']}
  "language": "{lang}",
  // {tpl['config_comment_api']}
  "ciphertalk_api_base": "http://127.0.0.1:5031",
  // {tpl['config_comment_wp']}
  "wechat_process": "Weixin.exe",
  // {tpl['config_comment_cp']}
  "ciphertalk_process": "CipherTalk.exe"
}}
"""

def create_default_config():
    lang = 'zh_cn'  # default language for new config
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            f.write(_config_template(lang))
        print(f'[CFG] {t("created", lang)}')
    except Exception as e:
        print(f'[E] config: {e}')

def load_config():
    if not os.path.isfile(CONFIG_PATH):
        create_default_config()
    cfg = {}
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8-sig') as f:
            raw = f.read()
        lines = [l for l in raw.split('\n') if not l.strip().startswith('//')]
        cfg = json.loads('\n'.join(lines))
    except Exception as e:
        print(f'[W] {t("parse_error")}: {e}')
        cfg = {}
    defaults = {
        'users': [], 'check_interval': 120, 'notify_interval': 10,
        'fetch_limit': 5, 'autostart': False, 'show_self': False,
        'language': 'zh_cn',
        'ciphertalk_api_base': 'http://127.0.0.1:5031',
        'wechat_process': 'Weixin.exe', 'ciphertalk_process': 'CipherTalk.exe',
    }
    for k, v in defaults.items():
        cfg.setdefault(k, v)
    users = cfg.get('users', [])
    cfg['users'] = [users] if isinstance(users, dict) else users
    return cfg

CFG = load_config()



# ── AUMID shortcut registration ───────────────────────────
def ensure_shortcut():
    """Create Start Menu shortcut so toast icon works from any path.
    Shortcut points to our EXE (icon embedded), AUMID='WeChat'."""
    try:
        import pythoncom
        from win32com.shell import shell
        from win32com.propsys import propsys, pscon
    except ImportError:
        return  # not available (e.g. EXE without pywin32)

    lnk = os.path.join(
        os.environ.get('APPDATA', ''),
        'Microsoft', 'Windows', 'Start Menu', 'Programs',
        'WeChat-Notifier.lnk'
    )

    # Check if already registered
    if os.path.isfile(lnk):
        try:
            r = subprocess.run(['powershell','-NoP','-Command',
                f"(New-Object -ComObject Shell.Application).NameSpace('{os.path.dirname(lnk)}')"
                f".ParseName('{os.path.basename(lnk)}').ExtendedProperty('System.AppUserModel.ID')"
            ], capture_output=True, text=True, timeout=5)
            if 'WeChat' in (r.stdout or ''):
                return
        except Exception:
            pass
        try: os.remove(lnk)
        except Exception: pass

    try:
        shortcut = pythoncom.CoCreateInstance(
            shell.CLSID_ShellLink, None, pythoncom.CLSCTX_INPROC_SERVER,
            shell.IID_IShellLink
        )
        shortcut.SetPath(sys.executable)
        shortcut.SetIconLocation(sys.executable, 0)

        ps = shortcut.QueryInterface(propsys.IID_IPropertyStore)
        pv = propsys.PROPVARIANTType(AUMID, pythoncom.VT_LPWSTR)
        ps.SetValue(pscon.PKEY_AppUserModel_ID, pv)
        ps.Commit()

        pf = shortcut.QueryInterface(pythoncom.IID_IPersistFile)
        pf.Save(lnk, True)
        print('[AUMID] shortcut registered')
    except Exception as e:
        print(f'[W] shortcut: {e}')

# ── autostart ─────────────────────────────────────────────
def setup_autostart(enable):
    startup = os.path.join(os.environ.get('APPDATA', ''),
                           'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    lnk = os.path.join(startup, 'WeChat-Notifier.lnk')
    if enable:
        if not os.path.isfile(lnk):
            ps = (
                "$w=New-Object -ComObject WScript.Shell;"
                f"$s=$w.CreateShortcut('{lnk}');"
                f"$s.TargetPath='{sys.executable}';"
                "$s.WorkingDirectory='{0}';".format(SCRIPT_DIR) +
                "$s.WindowStyle=7;$s.Save()"
            )
            subprocess.run(['powershell','-NoP','-Command',ps], capture_output=True, timeout=5)
            print(f'[{t("autostart")}] {t("autostart_on")}')
    else:
        if os.path.isfile(lnk):
            os.remove(lnk)
            print(f'[{t("autostart")}] {t("autostart_off")}')

# ── toast ─────────────────────────────────────────────────
def _get_icon_path():
    """Ensure an icon file exists for toast appLogoOverride. Returns path or None."""
    # 1. Check for weixin.ico next to EXE
    ico = os.path.join(SCRIPT_DIR, 'weixin.ico')
    if os.path.isfile(ico) and os.path.getsize(ico) > 100:
        return ico
    # 2. Extract icon from our own EXE to temp
    try:
        import win32gui, win32con, win32ui
        hicon = win32gui.ExtractIcon(0, sys.executable, 0)
        if hicon:
            tmp = os.path.join(os.environ.get('TEMP', SCRIPT_DIR), 'wx_icon.ico')
            # Save HICON to .ico via win32ui
            dc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
            bmp = win32ui.CreateBitmap()
            bmp.CreateCompatibleBitmap(dc, 32, 32)
            memdc = dc.CreateCompatibleDC()
            memdc.SelectObject(bmp)
            win32gui.DrawIconEx(memdc.GetHandleOutput(), 0, 0, hicon, 32, 32, 0, None, win32con.DI_NORMAL)
            bmp.SaveBitmapFile(memdc, tmp)
            memdc.DeleteDC()
            win32gui.DestroyIcon(hicon)
            if os.path.isfile(tmp) and os.path.getsize(tmp) > 100:
                return tmp
    except Exception:
        pass
    return None


def send_toast(title, body):
    ttl = title.replace("'", "''")
    bdy = body.replace("'", "''")
    ps = (
        "[Windows.UI.Notifications.ToastNotificationManager,"
        "Windows.UI.Notifications,ContentType=WindowsRuntime]|Out-Null;"
        "$t=[Windows.UI.Notifications.ToastNotificationManager]"
        "::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02);"
        "$n=$t.GetElementsByTagName('text');"
        f"$n.Item(0).AppendChild($t.CreateTextNode('{ttl}'))|Out-Null;"
        f"$n.Item(1).AppendChild($t.CreateTextNode('{bdy}'))|Out-Null;"
        f"[Windows.UI.Notifications.ToastNotificationManager]"
        f"::CreateToastNotifier('{AUMID}').Show([Windows.UI.Notifications.ToastNotification]::new($t))"
    )
    try:
        r = subprocess.run(['powershell','-NoP','-Command',ps], capture_output=True, text=True, timeout=10)
        if r.returncode != 0:
            print(f'[E] toast: {r.stderr.strip()[:150]}')
        else:
            print(f'[Toast] {title}: {body}')
    except Exception as e:
        print(f'[E] toast: {e}')

# ── helpers ───────────────────────────────────────────────
def is_running(name):
    try:
        r = subprocess.run(['tasklist','/fi',f'IMAGENAME eq {name}','/nh','/fo','csv'],
                           capture_output=True, text=True, timeout=5)
        return name.lower() in r.stdout.lower()
    except Exception:
        return False

def fetch_msgs(session_id, limit=5):
    url = f'{CFG["ciphertalk_api_base"]}/v1/messages?sessionId={session_id}&limit={limit}&order=desc'
    try:
        r = urllib.request.urlopen(url, timeout=10)
        return json.loads(r.read().decode('utf-8')).get('data',{}).get('messages',[])
    except Exception as e:
        print(f'[E] fetch ({session_id[:12]}..): {e}')
        return []

def load_state():
    try:
        with open(os.path.join(SCRIPT_DIR, 'notifier_state.json'),'r') as f:
            return json.load(f)
    except Exception:
        return {}

def save_state(s):
    with open(os.path.join(SCRIPT_DIR, 'notifier_state.json'),'w') as f:
        json.dump(s, f)

def fmt_msg(msg):
    kind = msg.get('messageKind','text')
    content = msg.get('parsedContent','')
    if kind == 'image': return t('msg_image')
    if kind == 'video': return t('msg_video')
    if kind == 'voice': return t('msg_voice')
    if kind == 'app_transfer': return t('msg_transfer')
    if kind == 'app':
        try:
            ad = json.loads(content)
            title = ad.get('title','') or ad.get('appName','')
            return f'[{t("label_app")}] {title}' if title else t('msg_app')
        except Exception:
            return f'[{t("label_app")}] {content[:30]}'
    if kind in ('quote','app_quote'):
        reply = content or ''
        prefix = t('label_quote_prefix')
        return f'{prefix} {reply[:70]}' if reply else t('msg_quote')
    return content[:80] if content else f'[{kind}]'

# ── main ──────────────────────────────────────────────────
def main():
    print('=' * 45)
    print(f'  {t("banner")}')
    print('=' * 45)
    users = CFG.get('users', [])
    if not any(u.get('session_id','') and 'xxx' not in u.get('session_id','') for u in users):
        print(f'  [W] {t("no_user")}')
        print(f'  {t("exit_soon")}')
        print('=' * 45); time.sleep(10); sys.exit(1)
    for u in users:
        print(f'  {t("target")}: {u.get("display_name","?")} ({u.get("session_id","?")})')
    print(f'  {t("check")}: {CFG["check_interval"]}s | {t("notify")}: {CFG["notify_interval"]}s')
    print(f'  {t("autostart")}: {CFG["autostart"]} | {t("show_self")}: {CFG["show_self"]}')
    print(f'  {t("language")}: {CFG["language"]}')
    print('=' * 45); print()
    ensure_shortcut()  # register AUMID on first run
    setup_autostart(CFG['autostart'])

    state = load_state()
    if state:
        print(f'[{t("state_title")}]')
        for sid, lid in state.items():
            print(f'  {sid[:12]}.. -> last_id={lid}')
        print()

    send_toast(t('banner'), t('started'))

    mode, interval = 'checking', CFG['check_interval']
    wp, cp = CFG['wechat_process'], CFG['ciphertalk_process']
    last_status = 'started'
    users = CFG.get('users', [])
    ci, ni = CFG['check_interval'], CFG['notify_interval']

    while True:
        try:
            w = is_running(wp); c = is_running(cp)
            now = datetime.now().strftime('%H:%M:%S')
            if mode == 'checking':
                if w and c:
                    print(f'[+] {now} {t("ready")} -> notify')
                    if last_status != 'ready':
                        send_toast(t('banner'), t('ready')); last_status = 'ready'
                    mode, interval = 'notifying', ni
                else:
                    parts = []
                    if not w: parts.append(t('wechat_dead'))
                    if not c: parts.append(t('ctalk_dead'))
                    print(f'[.] {now} {SEP.join(parts)}, {ci}s'); interval = ci
            else:
                if not w or not c:
                    parts = []
                    if not w: parts.append(t('wechat_closed'))
                    if not c: parts.append(t('ctalk_closed'))
                    print(f'[!] {now} {SEP.join(parts)}, {t("check_mode")}')
                    if last_status != 'disconnected':
                        send_toast(t('banner'), t('disconnected')); last_status = 'disconnected'
                    mode, interval = 'checking', ci
                else:
                    if not users: time.sleep(interval); continue
                    any_new = False
                    for user in users:
                        sid = user.get('session_id','')
                        dname = user.get('display_name','?')
                        if not sid: continue
                        msgs = fetch_msgs(sid, CFG['fetch_limit'])
                        if msgs:
                            last_id = state.get(sid,0); new_max = last_id
                            for m in reversed(msgs):
                                lid = m.get('localId',0)
                                if lid > last_id:
                                    if lid > new_max: new_max = lid
                                    if m.get('direction')=='in' and (
                                        CFG.get('show_self') or
                                        not m.get('sender',{}).get('isSelf',False)
                                    ):
                                        send_toast(f'{dname} ({datetime.now():%H:%M})', fmt_msg(m))
                            if new_max > last_id: state[sid] = new_max; any_new = True
                    if any_new: save_state(state)
            time.sleep(interval)
        except KeyboardInterrupt: print(f'\n{t("stop")}'); break
        except Exception as e: print(f'[E] {e}'); time.sleep(interval)

if __name__ == '__main__':
    main()
