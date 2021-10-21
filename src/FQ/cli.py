import click


from FQ.FQueue import run_queue
from FQ.Sender import run_sender


@click.command("send")
@click.option('--src', help='list of video sources')
def send(src):
    run_sender(src)


@click.command("queue")
def queue():
    run_queue()


@click.group()
def main():
    pass


main.add_command(send)
main.add_command(queue)

if __name__ == '__main__':
    main()