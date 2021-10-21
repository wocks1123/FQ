import click


from FQ.FQueue import run_queue
from FQ.Sender import run_sender


@click.command("send")
@click.option('--src', help='list of video sources')
def send(src):
    if not src:
        print("[ERROR] enter list of video sources...")
        exit(1)
    run_sender(src)


@click.command("queue")
def queue():
    run_queue()


@click.group()
def cli():
    pass


cli.add_command(send)
cli.add_command(queue)


def main():
    cli.main()


if __name__ == '__main__':
    main()