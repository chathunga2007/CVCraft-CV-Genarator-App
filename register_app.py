import os
import sys
import win32com.client
from win32com.propsys import propsys, pscon

def register_shortcuts_and_app_id():
    shell = win32com.client.Dispatch('WScript.Shell')
    start_menu = os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Start Menu\Programs')
    lnk_path = os.path.join(start_menu, 'CVCraft.lnk')
    
    desktop_folder = shell.SpecialFolders('Desktop')
    desktop_lnk = os.path.join(desktop_folder, 'CVCraft.lnk')
    local_lnk = os.path.abspath('CVCraft.lnk')

    ico_path = os.path.abspath('assets/cvcraft.ico')
    app_id = 'CVCraft.ProfessionalResumeBuilder.App.1.0'

    pythonw = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
    if not os.path.exists(pythonw):
        pythonw = sys.executable

    main_py = os.path.abspath('main.py')
    working_dir = os.path.abspath('.')
    exe_path = os.path.join(working_dir, 'CVCraft.exe')

    for p in [lnk_path, desktop_lnk, local_lnk]:
        try:
            shortcut = shell.CreateShortCut(p)
            if os.path.exists(exe_path):
                shortcut.Targetpath = exe_path
                shortcut.Arguments = ''
            else:
                shortcut.Targetpath = pythonw
                shortcut.Arguments = f'"{main_py}"'
            shortcut.WorkingDirectory = working_dir
            shortcut.IconLocation = f'{ico_path},0'
            shortcut.Description = 'CVCraft — Professional Resume & CV Builder'
            shortcut.Save()

            # Set the AppUserModelID and RelaunchIcon on the shortcut's property store
            store = propsys.SHGetPropertyStoreFromParsingName(p, None, 2)
            pv = propsys.PROPVARIANTType(app_id)
            store.SetValue(pscon.PKEY_AppUserModel_ID, pv)
            pv_icon = propsys.PROPVARIANTType(f'{ico_path},0')
            store.SetValue(pscon.PKEY_AppUserModel_RelaunchIconResource, pv_icon)
            store.Commit()
            print(f'Successfully registered shortcut with AUMID: {p}')
        except Exception as e:
            print(f'Error creating shortcut {p}: {e}')

if __name__ == '__main__':
    register_shortcuts_and_app_id()
