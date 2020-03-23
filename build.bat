@RD /S /Q dist

robocopy "img" "dist/img"
robocopy /S /E "scenes" "dist/scenes"
robocopy /S /E "ui" "dist/ui"

copy "embree3.dll" "dist/embree3.dll"
copy "OpenImageDenoise.dll" "dist/OpenImageDenoise.dll"
copy "OpenImageIO.dll" "dist/OpenImageIO.dll"
copy "pyluxcore.pyd" "dist/pyluxcore.pyd"
copy "tbb.dll" "dist/tbb.dll"
copy "tbbmalloc.dll" "dist/tbbmalloc.dll"


%PYTHONPATH%\Scripts\\pyinstaller.exe ^
	-F --windowed --"icon=img/CNDL.ico" ^
	cndl.py

cd dist

7z a CNDL_v%1.zip *

cd ..

candle.exe cndl.wxs
light.exe cndl.wixobj

del cndl.wixobj
del cndl.wixpdb

move cndl.msi dist/CNDL_v%1.msi
