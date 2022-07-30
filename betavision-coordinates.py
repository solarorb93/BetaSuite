import win32gui, win32ui

while( True ):
    flags, hcursor, (cx,cy) = win32gui.GetCursorInfo()
    print( 'x: %4d, y: %4d'%( cx, cy ) )
