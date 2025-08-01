import click


@click.group()
def cli():
    pass


@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def infra(
    args: list[str],
):
    from synth_crunch.infra.miner import main

    main()
