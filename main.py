# ----------------------------------------------------------------
# Author: WayneFerdon wayneferdon@hotmail.com
# Date: 2023-04-02 11:57:59
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-04-09 21:35:02
# FilePath: \undefinedc:\Users\WayneFerdon\AppData\Roaming\FlowLauncher\Plugins\Wox.Base.Plugin.WindowsRegistry\main.py
# ----------------------------------------------------------------
# Copyright (c) 2023 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

import os, sys
import json
import ctypes
from winreg import *
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from WoxPluginBase_Query import *

ICON = './Images/Registry.png'

def is_admin():
    '''
    Checks if the script is running with administrative privileges.
    Returns True if is running as admin, False otherwise.
    '''    
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class WindowsRegedit(QueryPlugin):
    REG_ROOTS = {
        'HKEY_CLASSES_ROOT':HKEY_CLASSES_ROOT,
        'HKEY_CURRENT_CONFIG':HKEY_CURRENT_CONFIG,
        'HKEY_CURRENT_USER':HKEY_CURRENT_USER,
        'HKEY_LOCAL_MACHINE':HKEY_LOCAL_MACHINE,
        'HKEY_USERS':HKEY_USERS,
        '':None
        # 'HKEY_PERFORMANCE_DATA':HKEY_PERFORMANCE_DATA,
        # 'HKEY_DYN_DATA':HKEY_DYN_DATA
    }
    def query(self, query:str):
        splited = repr(query)[1:-1].split('\\\\')
        if splited.count('') > 1:
            return None
        root = splited[0]
        results = list()
        if len(splited) <= 1:
            for rootKeyName in WindowsRegedit.REG_ROOTS:
                if rootKeyName == '':
                    continue
                if root.lower() not in rootKeyName.lower():
                    continue
                results.append(self.getQueryResult(rootKeyName,''))
            return results
        
        if root not in WindowsRegedit.REG_ROOTS.keys():
            return None
        subKey = r'\\'.join(splited[1:-1]).replace('\\\\','\\')
        keyHandle = OpenKey(ConnectRegistry(None,WindowsRegedit.REG_ROOTS[root]), subKey, access=KEY_ALL_ACCESS)
        count, _, _ = QueryInfoKey(keyHandle)
        if count == 0:
            results.append(self.getQueryResult(root, subKey))
        last = splited[-1]
        for i in range(count):
            subKeyName = repr(EnumKey(keyHandle, i))
            if last.lower() not in subKeyName.lower():
                continue
            if subKey == '':
                subPath = "\\".join([subKeyName[1:-1]])
            else:
                subPath = "\\".join([subKey, subKeyName[1:-1]])
            results.append(self.getQueryResult(root, subPath))
        return results

    def getQueryResult(self, root:str, sub:str):
        try:
            a = ConnectRegistry(None,WindowsRegedit.REG_ROOTS[root])
            subKeyHandle = OpenKey(a, sub,access=KEY_ALL_ACCESS)
            subCount, valueCount, _ = QueryInfoKey(subKeyHandle)
            full = root
            if sub != '':
                full = full + '\\' + sub
            subtitle = 'Sub keys:' + str(subCount) +' - Values:' + str(valueCount)
            return QueryResult(full,subtitle,ICON,full, LauncherAPI.ChangeQuery.name, False, Plugin.actionKeyword + ' ' + full + '\\',True).toDict()
        except Exception as e:
            return self.getExceptionResult(root, sub, e)
        
    def getExceptionResult(self, root:str, sub:str, e:Exception):
        full = root
        if sub != '':
            full = full + '\\' + sub
        return QueryResult(full, str(e), ICON, full, None, False).toDict()

    def context_menu(self, fullKey:str): 
        results = list()
        results.append(QueryResult(fullKey,'Press Enter to Open in Regedit',ICON,'',WindowsRegedit.openInRegedit.__name__,False,fullKey).toDict())
        results.append(self.getCopyDataResult('Path',fullKey,ICON))
        return results
    
    def openInRegedit(self, fullKey:str):
        regRoot = ConnectRegistry(None,HKEY_CURRENT_USER)
        keyHandle = OpenKey(regRoot, r'Software\Microsoft\Windows\CurrentVersion\Applets\Regedit',access=KEY_ALL_ACCESS)
        SetValueEx(keyHandle, 'LastKey', 0, REG_SZ, fullKey)
        os.popen('regedit')
        return

if __name__ == '__main__':
    WindowsRegedit()