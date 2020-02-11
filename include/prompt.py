import os
import tempfile

def prompt(default = None):
    editor = 'nano'

    with tempfile.NamedTemporaryFile(mode='r+') as temp:
        if default:
            temp.write(default)
            temp.flush()

        child_pid = os.fork()
        
        is_child = child_pid == 0

        if is_child:
            os.execvp(editor,[editor, temp.name])
        else:
            os.waitpid(child_pid, 0)
            temp.seek(0)
            return temp.read().strip()