import click
## TODO: Add how often you want to check?? I think that is for the cron no??

@click.command()
@click.option(
    '--port', '-p',
    default='8443',
    help='port number of the jupyter server. default is 8443'
)
@click.option(
    '--idle-time', '-t',
    default=3600,
    help='Auto stop time in seconds. default 1 hour'
)
@click.option(
    '--ignore-connections',
    is_flag=True,
    help='Stop notebook once idle, ignore connected users'
)
def main(port, idle_time, ignore_connections):
    print("I'm a beautiful CLI")
    print(f'args {port}, {idle_time}, {ignore_connections}')


if __name__ == "__main__":
    main()
    