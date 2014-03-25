set dir=%USERPROFILE%\printers_lock
set file=%dir%\004
IF not EXIST "%file%" (

    REG DELETE "HKEY_CURRENT_USER\Printers\Connections" /f

    \\fileserver\Archiv\scripts\printers\%username%.bat

    mkdir "%dir%"
    echo > "%file%"
)
