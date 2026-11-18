@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo [1/3] 正在重新編譯閱讀器與 GitHub Pages 檔案...
python build_reader.py
echo [2/3] 正在打包變更...
git add docs/ *.md *.html *.py
git commit -m "Update novel chapters and sync GitHub Pages"
echo [3/3] 正在推送到 GitHub Pages 線上網站...
git push origin main
echo.
echo ====================================================
echo 同步完成！線上網站將在約 15~30 秒內自動更新至最新內容。
echo ====================================================
pause
