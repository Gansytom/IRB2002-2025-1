import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/grupo1/IRB2002-2025-1/src/install/detection_pkg'
