@echo off
chcp 65001 > nul
echo Pythonキャッシュを削除しています...

REM __pycache__ ディレクトリを再帰的に削除（.gitフォルダを除く）
for /d /r %%i in (__pycache__) do (
    echo %%i | findstr /i ".git" > nul
    if errorlevel 1 (
        echo 削除中: %%i
        rmdir /s /q "%%i"
    )
)

REM .pyc ファイルも削除（.git配下は除外）
for /r %%i in (*.pyc) do (
    echo %%i | findstr /i ".git" > nul
    if errorlevel 1 (
        echo 削除中: %%i
        del /q "%%i"
    )
)

echo 完了しました。
pause
