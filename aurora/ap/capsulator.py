# Python capsulator class
# Configures and runs the capsulator program developed by Stanford (v 0.01b)

import subprocess
class Capsulator:    

    def __init__(self):
        self.process_list = {}

    def start(self, tunnel_interface, forward_to, border_interface, virtual=True):
        """Starts an instance of capsulator.  Returns PID.
        
        tunnel_interface = names the interface which is the tunnel endpoint
        forward_to = the IP the tunnel should forward frames to
        border_interface = specifies a border interface and its tag; 
                           format is INTF#TAG ... ex: eth0#1248
        virtual = whether or not to create a virtual interface for
                  border_interface (i.e. a tap).  In this case, border_interface
                  should not be a real interface, as it will be created
                  automatically."""
        if virtual:
            command = ["capsulator","-t", tunnel_interface, "-f", forward_to, "-vb", border_interface]
        else:
            command = ["capsulator","-t", tunnel_interface, "-f", forward_to, "-b", border_interface]

        process = subprocess.Popen(command)
        self.process_list[process.pid] = process
        
        return process.pid
        

    def stop(self, pid):
        """Stops an instance of capsulator with this PID."""
        process = self.process_list.pop(pid)
        process.terminate()
        # Need .wait(), otherwise process hangs around as defunct.
        process.wait()


    def kill_all(self):
        """Stops all known instances of capsulator."""
        for key in self.process_list:
            process = self.process_list.pop(key)
            process.terminate()
            process.wait()
