# CS1604-Judger

## 重新安装 judger

`uv tool install --force` 不会重新打包，代码变更后必须：

```bash
uv tool uninstall judger
uv cache clean --force
uv tool install .
```

开发时用 `uv run judger` 直接跑源码，无需重装。
