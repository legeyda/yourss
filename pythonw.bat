@Echo Off

setlocal

set SELFDIR=%~dp0

IF DEFINED PYTHONW_WORK_DIR (
	set ROOT=%PYTHONW_WORK_DIR%
) ELSE (
	set ROOT=%SELFDIR%.python\windows
)
set PYTHON_HOME=%ROOT%\miniconda\envs\default

if not exist %PYTHON_HOME%\bin\activate (
	if not exist %PYTHON_HOME% (
		if not exist %ROOT%\miniconda (
			if not exist %ROOT%\temp\miniconda-installer.exe (
				if not exist "%ROOT%"      md "%ROOT%"
				if not exist "%ROOT%\temp" md "%ROOT%\temp"
				echo downloading miniconda...
				powershell -Command "Invoke-WebRequest https://repo.continuum.io/miniconda/Miniconda3-4.2.12-Windows-x86.exe -OutFile %ROOT%\temp\miniconda-installer.exe"
			)
			if not exist "%ROOT%"            md "%ROOT%"
			rem if not exist "%ROOT%\miniconda"  md "%ROOT%\miniconda"
			echo installing miniconda...
			start /wait "installing miniconda" "%ROOT%\temp\miniconda-installer.exe" /NoRegistry=1 /S /D=%ROOT%\miniconda
		)
		echo virtual environment is to be installed into %PYTHON_HOME%
		echo y | "%ROOT%\miniconda\Scripts\conda" create --name default pip
	)
)

call %ROOT%\miniconda\Scripts\activate.bat default
if exist requirements.txt (
	echo pip installing requirements.txt...
	start /wait "pip installing requirements.txt" "%PYTHON_HOME%\Scripts\pip" install -r requirements.txt
)

%PYTHON_HOME%\python.exe %*
