import datetime
import threading
from json import (load as jsonload, dump as jsondump)

import PySimpleGUI as sg
from apscheduler.schedulers.background import BlockingScheduler

from szu_autoconnect.core.auto import Connector

SETTINGS_FILE = 'settings.cfg'
DEFAULT_SETTINGS = {
    'username': '',
    'password': '',
    'office': True,
    'dormitory': False,
    'interval': 20,
    'pin': True,
}
# "Map" from the settings dictionary keys to the window's element keys
SETTINGS_KEYS_TO_ELEMENT_KEYS = {
    'username': '-username-',
    'password': '-password-',
    'office': '-office-',
    'dormitory': '-dormitory-',
    'interval': '-interval-',
    'pin': '-pin-',
}


def load_settings(settings_file, default_settings):
    try:
        with open(settings_file, 'r') as f:
            settings = jsonload(f)
    except Exception as e:
        print('load from default settings')
        settings = default_settings
        save_settings(settings_file, settings, None)
    return settings


def save_settings(settings_file, settings, values):
    if values:  # if there are stuff specified by another window, fill in those values
        for key in SETTINGS_KEYS_TO_ELEMENT_KEYS:  # update window with the values read from settings file
            try:
                settings[key] = values[SETTINGS_KEYS_TO_ELEMENT_KEYS[key]]
            except Exception as e:
                print(f'{e}')

    with open(settings_file, 'w') as f:
        jsondump(settings, f)

    if values:
        sg.popup('Settings saved')


def create_auto_connection(config, window):
    if config['username'] == '':
        window['log'].print('Check Username')
        return None, None
    if config['password'] == '':
        window['log'].print('Check Password')
        return None, None
    connector = Connector(config, log_printer=None)
    window['log'].print('Creating a Job')
    scheduler = BlockingScheduler()
    run_task = connector.run
    scheduler.add_job(run_task, 'interval', seconds=connector.interval, name='run',
                      next_run_time=datetime.datetime.now())
    return connector, scheduler


def start_work(scheduler):
    if scheduler is not None:
        scheduler.start()


def create_ui(settings):
    sg.theme('Topanga')
    title_font = ('Gigi', 18)
    config_name_font = ('宋体', 10)
    log_font = ('宋体', 9)

    bar = [
        [
            sg.Col(
                [
                    [
                        sg.Text('SZU Auto Connector', grab=True, text_color='gray')
                    ]
                ], pad=(0, 0)),
            sg.Col(
                [
                    [
                        sg.Check('Pin', enable_events=True, key='-pin-'),
                        sg.Text(sg.SYMBOL_X, enable_events=True, key='-X-')  # '❎'
                    ]
                ],
                element_justification='r', grab=True, pad=(0, 0), expand_x=True)
        ],
        [sg.HorizontalSeparator()]
    ]

    title_ui = [
        sg.Text("SZU Auto Connector", text_color='yellow', font=title_font, justification='center',
                size=(20, 1)),
    ]

    author_ui = [
        sg.Text('作者: 红领巾二号', text_color='red', font=config_name_font, size=(38, 1), justification='right')
    ]

    config_ui = [sg.Frame(
        layout=[
            [
                sg.Text('网络选择: ', font=config_name_font, size=(10, 1)),
                sg.Radio('教学区', key='-office-', group_id='zone', default=True),
                sg.Radio('宿舍区', key='-dormitory-', group_id='zone')
            ],
            [
                sg.Text('用户名: ', font=config_name_font, size=(10, 1)),
                sg.In(key='-username-', size=(25, 1))
            ],
            [
                sg.Text('密码: ', font=config_name_font, size=(10, 1)),
                sg.In(key='-password-', size=(25, 1), password_char='*')
            ],
            [
                sg.Text('间隔(s): ', font=config_name_font, size=(10, 1)),
                sg.Spin(values=[i for i in range(1, 1000)], initial_value=10, key='-interval-', size=(23, 1))
            ]
        ],
        title='Configs'
    )]

    log_ui = [sg.Frame(
        layout=[
            [
                sg.MLine('', key='log', size=(40, 8), font=log_font)
            ]
        ],
        title='Logs'
    )]

    tail_ui = [
        sg.Button("Login", size=(7, 1)),
        sg.Save(size=(7, 1)),
        sg.Button('Pause', size=(7, 1)),
        sg.Exit(size=(6, 1))
    ]

    total_ui = [bar, title_ui, author_ui, config_ui, tail_ui, log_ui, ]

    # return sg.Window('* SZU Auto Connector *', layout=total_ui, font='Helvetica 10', )

    window = sg.Window('* SZU Auto Connector *', layout=total_ui, font='Helvetica 10',
                       no_titlebar=True, finalize=True, keep_on_top=settings['pin']
                       )

    for k, v in SETTINGS_KEYS_TO_ELEMENT_KEYS.items():  # update window with the values read from settings file
        try:
            window[SETTINGS_KEYS_TO_ELEMENT_KEYS[k]].update(value=settings[k])
        except Exception as e:
            print(e)

    return window


def main_loop():
    window, settings = None, load_settings(SETTINGS_FILE, DEFAULT_SETTINGS)
    scheduler = None
    pause_flag = None
    while True:
        if window is None:
            window = create_ui(settings)
        event, values = window.read()

        if event == 'Login':
            if values['-office-']:
                zone = 'office'
            elif values['-dormitory-']:
                zone = 'dormitory'
            else:
                zone = ''
            configs = {
                'username': values['-username-'],
                'password': values['-password-'],
                'zone': zone,
                'interval': values['-interval-']
            }
            if not scheduler:
                connector, scheduler = create_auto_connection(configs, window)
            else:
                scheduler.shutdown()
                del connector, scheduler
                connector, scheduler = create_auto_connection(configs, window)

            if scheduler:
                window['log'].print('Start a Job')
                threading.Thread(target=start_work, args=(scheduler,), daemon=True).start()

            window['Login'].update(disabled=True)

        if event in ['Pause', 'Resume']:
            if not scheduler:
                window['log'].print('Not find a Job')
            else:
                if not pause_flag:
                    window['log'].print('Pause Job')
                    threading.Thread(target=scheduler.pause, daemon=True).start()
                    window['Pause'].update('Resume')
                    pause_flag = True
                else:
                    window['log'].print('Resume Job')
                    threading.Thread(target=scheduler.resume, daemon=True).start()
                    window['Pause'].update('Pause')
                    pause_flag = False

        if event == 'Save':
            save_settings(SETTINGS_FILE, settings, values)
            window.close()
            window = None

        if event in (None, 'Exit', '-X-'):
            break

        if event == '-pin-':
            window.close()
            window = None
            settings['pin'] = values['-pin-']

    window.close()

# if __name__ == '__main__':
#     main_loop()
