# ----------------------------------------------------------------
# Author: WayneFerdon wayneferdon@hotmail.com
# Date: 2023-04-02 11:57:59
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-04-04 17:32:25
# FilePath: \Wox.Base.Plugin.WindowsRegistry\main.py
# ----------------------------------------------------------------
# Copyright (c) 2023 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

import os, sys
import json
from winreg import *
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from WoxPluginBase_Query import *

ICON = './Images/Registry.png'

class WindowsRegedit(Query):
    __actionKeyword__ = None

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
        if WindowsRegedit.__actionKeyword__ is None:
            with(open('./plugin.json','r') as pluginJson):
                WindowsRegedit.__actionKeyword__ = WindowsRegedit.GetActionKeyword(json.load(pluginJson)['ID'])

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
                results.append(self.GetQueryResult(rootKeyName,''))
            return results
        
        if root not in WindowsRegedit.REG_ROOTS.keys():
            return None
        subKey = r'\\'.join(splited[1:-1]).replace('\\\\','\\')
        keyHandle = OpenKey(ConnectRegistry(None,WindowsRegedit.REG_ROOTS[root]), subKey, access=KEY_ALL_ACCESS)
        count,_,_ = QueryInfoKey(keyHandle)
        if count == 0:
            results.append(self.GetQueryResult(root, subKey))
        last = splited[-1]
        for i in range(count):
            subKeyName = repr(EnumKey(keyHandle, i))
            if last.lower() not in subKeyName.lower():
                continue
            if subKey == '':
                subPath = "\\".join([subKeyName[1:-1]])
            else:
                subPath = "\\".join([subKey, subKeyName[1:-1]])
            results.append(self.GetQueryResult(root, subPath))
        return results

    def GetQueryResult(self, root:str, sub:str):
        try:
            a = ConnectRegistry(None,WindowsRegedit.REG_ROOTS[root])
            subKeyHandle = OpenKey(a, sub,access=KEY_ALL_ACCESS)
            subCount, valueCount, _ = QueryInfoKey(subKeyHandle)
            full = root
            if sub != '':
                full = full + '\\' + sub
            subtitle = 'Sub keys:' + str(subCount) +' - Values:' + str(valueCount)
            return QueryResult(full,subtitle,ICON,full,Launcher.GetAPI(Launcher.API.ChangeQuery), False,WindowsRegedit.__actionKeyword__ + ' ' + full + '\\',True).toDict()
        except Exception as e:
            return self.GetExceptionResult(root, sub, e)
        
    
    def GetExceptionResult(self, root:str, sub:str, e:Exception):
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