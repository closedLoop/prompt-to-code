import signal
import subprocess
import traceback


def timeout_handler_wrapper(timeout=5):
    msg = f"Execution took longer than {format} seconds"

    def timeout_handler(_signum, _frame):
        raise TimeoutError(msg)

    return timeout_handler


def run_code(code, timeout=60):
    signal.signal(signal.SIGALRM, timeout_handler_wrapper(timeout=timeout))
    tb_str = None
    try:
        # Set an alarm for 10 seconds
        signal.alarm(timeout)
        exec(code)
    except TimeoutError as te:
        error = f"TimeoutError: Execution took longer than {timeout} seconds"
        tb_str = traceback.format_exception(type(te), value=error, tb=te.__traceback__)
    except Exception as e:
        tb_str = traceback.format_exception(type(e), value=e, tb=e.__traceback__)
    finally:
        # Cancel the alarm if it didn't go off
        signal.alarm(0)
        # Remove the signal handler and set it to the default behavior
        signal.signal(signal.SIGALRM, signal.SIG_DFL)
    return tb_str


def run_shell_command(command, timeout=60) -> tuple[str, bool]:
    """Returns stdout of command and a boolean indicating if there was an error"""
    try:
        signal.alarm(timeout)
        result = subprocess.run(
            command, capture_output=True, text=True, check=True, shell=True
        )
        return result.stdout.strip(), False
    except TimeoutError as te:
        error = f"TimeoutError: Execution took longer than {timeout} seconds {command}. Error: {te}"
        if te.stdout:
            error += "\n" + te.stdout.strip()
        return error, True
    except subprocess.CalledProcessError as e:
        if e.stdout:
            return e.stdout.strip(), True
        return f"Command failed: {command}. Error: {e}", True
    except Exception as e:
        raise RuntimeError(f"Command failed: {command}. Error: {e}") from e
    finally:
        # Cancel the alarm if it didn't go off
        signal.alarm(0)
        # Remove the signal handler and set it to the default behavior
        signal.signal(signal.SIGALRM, signal.SIG_DFL)
