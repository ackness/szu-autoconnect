import argparse


def build_config():
    args = argparse.ArgumentParser("SZU Auto Reconnect")
    args.add_argument('--username', '-u', default='', type=str, help="your username")
    args.add_argument('--password', '-p', default='', type=str, help="your password")
    args.add_argument('--zone', '-z', default='office', type=str, choices=['office', 'dormitory'], help="which zone")
    args.add_argument('--interval', '-i', default=60, type=int, help="time interval to check connection status")
    args.add_argument('--use_ui', '-ui', action='store_true', help="whether to use UI")

    return args.parse_args()


def create_job(configs):
    import datetime
    from szu_autoconnect.core.auto import Connector
    from apscheduler.schedulers.background import BlockingScheduler

    assert configs.username != '', "please input your username with -u"
    assert configs.password != '', "please input your password with -p"

    connect_config = {
        'username': configs.username,
        'password': configs.password,
        'zone': configs.zone,
        'interval': configs.interval
    }

    connector = Connector(connect_config, log_printer=None)
    scheduler = BlockingScheduler()
    run_task = connector.run
    scheduler.add_job(run_task, 'interval', seconds=connector.interval, name='run',
                      next_run_time=datetime.datetime.now())
    scheduler.start()


def run():
    config = build_config()
    if config.use_ui:
        from szu_autoconnect.core.ui import main_loop

        main_loop()
    else:
        create_job(config)


if __name__ == '__main__':
    run()
