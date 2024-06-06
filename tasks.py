from robocorp.tasks import task

from bot.core import Core

@task
def solve_challenge():
    Core()
