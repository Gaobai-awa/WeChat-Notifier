# 介绍
基于[Ciphertalk](https://github.com/ILoveBingLu/CipherTalk)读取聊天信息并且通过Ciphertalk的Http Api功能持续检测新消息,发送系统通知

powershell分支由deepseek生成,不做任何运行效果保证,不受理任何issue

## 快速开始
- 安装[微信](https://pc.weixin.qq.com)
- 安装[Ciphertalk](https://github.com/ILoveBingLu/CipherTalk)
- 打开Ciphertalk并且进行初始配置
- 前往开放接口栏,打开HTTP API,删掉访问密钥,监听模式为仅本机,监听端口为5031,然后保存并应用
- 下载项目的那个.ps1文件
- 下载config.json
- 在配置文件(config.json)里修改需要监听的用户的原始id(可以去ciphertalk的聊天查看里找到你要监听的人,然后点右上角会话详细,找到会话id那一栏复制)
- 启动
## 注意事项
请注意wechat(海外版微信)是不受支持的(高版本微信也有可能不受支持,详细请查看Ciphertalk的官方文档)

如果ciphertalk通过注入dll获取微信的密钥以及新消息,所以微信与ciphertalk都必须保持在后台常开

## 作者的话
本程序有可能因为微信/ciphertalk更新导致失效,失效了可以来踢我一脚,欢迎前往issues反馈

使用了deepseek-v4-pro配合reasonix优化代码结构

做这个软件呃本来就是为了方便在玩游戏的时候看到女朋友的消息,微信的通知做的太烂了,而且还有bug,有时候通知会没声音,根本不知道来消息了

希望可以方便到更多的人^w^

奥对了windows的通知需要在程序无边框全屏的情况下才可以正常显示,普通全屏是显示不出来的,这个是windows的锅,我也没办法捏,其他的通知方法都会让游戏失去焦点,对fps游戏很不友好

## 协议
[MIT](https://github.com/Gaobai-awa/WeChat-Notifier/blob/main/LICENSE)
呃呃虽然但是可以不要倒卖吗qwq,不过写的这么烂应该也没什么人会倒卖吧QAQ
